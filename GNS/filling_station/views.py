from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.mixins import CancelFormMixin, DateRangeListFilterMixin, ModalDeleteMixin, PreserveListQueryMixin
from core.navigation import redirect_preserve_query
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.decorators.http import require_POST
from django.db.models import Q, Sum, Count, OuterRef, Prefetch, Subquery
from ttn.models import MiriadaTtn
from .models import Balloon, Truck, Trailer, BalloonsBatch, BatchStatus, Reader, ReaderSettings
from .admin import BalloonResources
from .forms import (
    GetBalloonsAmount,
    BalloonForm,
    TruckForm,
    TrailerForm,
    BalloonsBatchForm
)
from .services import save_and_close_balloons_batch
from datetime import datetime, time, timedelta

STATUS_LIST = {
    1: 'Линия 1 - приёмка баллонов',
    2: 'Линия 1 - вход в наполнительный цех',
    3: 'Линия 2 - приёмка баллонов',
    4: 'Линия 2 - вход в наполнительный цех',
    5: 'Линия 1 - отбраковка перед каруселью',
    6: 'Линия 2 - выход из карусели',
    7: 'Линия 2 - отбраковка перед каруселью',
    8: 'Линия 1 - выход из карусели',
    9: 'Линия 1 - карусель',
    10: 'Линия 2 - карусель',
}


def resolve_batch_list_query_filter(query):
    """
    Определяет подпись фильтра по строке поиска (ТТН или грузовик).

    Returns:
        dict | None: ``{'label': str, 'value': str}`` или ``None``.
    """
    query = (query or '').strip()
    if not query:
        return None

    ttn_match = MiriadaTtn.objects.filter(name__icontains=query).exists()
    truck_match = Truck.objects.filter(registration_number__icontains=query).exists()
    if ttn_match and not truck_match:
        label = 'Фильтр по номеру ТТН'
    elif truck_match and not ttn_match:
        label = 'Фильтр по номеру грузовика'
    elif ttn_match and truck_match:
        label = 'Фильтр по номеру ТТН' if query.isdigit() else 'Фильтр по номеру грузовика'
    elif any(char.isalpha() for char in query):
        label = 'Фильтр по номеру грузовика'
    else:
        label = 'Фильтр по номеру ТТН'

    return {'label': label, 'value': query}


class BalloonListView(generic.ListView):
    model = Balloon
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('query', '')

        if query:
            return Balloon.objects.filter(
                Q(nfc_tag=query) | Q(serial_number=query)
            )
        else:
            return Balloon.objects.all()


class BalloonDetailView(generic.DetailView):
    model = Balloon


class BalloonUpdateView(PreserveListQueryMixin, generic.UpdateView):
    model = Balloon
    form_class = BalloonForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return self.redirect_preserve_query('filling_station:balloon_detail', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)


class BalloonDeleteView(ModalDeleteMixin, PreserveListQueryMixin, generic.DeleteView):
    """Удаление баллона через модальное окно."""

    model = Balloon
    success_url = reverse_lazy("filling_station:balloon_list")


def reader_info(request, reader_number=1):
    current_date = datetime.now().date()
    form = GetBalloonsAmount(request.POST or None)

    if request.method == "POST" and form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        action = request.POST.get('action')
        if action == 'export':
            dataset = BalloonResources().export(
                Reader.objects.filter(
                    number=reader_number,
                    change_date__range=(start_date, end_date)
                )
            )
            response = HttpResponse(dataset.xlsx, content_type='xlsx')
            response['Content-Disposition'] = f'attachment; filename="RFID_{reader_number}_{start_date}-{end_date}.xlsx"'
            return response
    else:
        start_date = end_date = current_date

    # Получаем все данные через метод модели
    stats = Reader.get_reader_stats(reader_number, start_date, end_date)
    reader = ReaderSettings.objects.get(number=reader_number)

    paginator = Paginator(stats['balloons_list'], 10)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    context = {
        "page_obj": page_obj,
        'current_quantity_by_reader': stats['total_rfid'],
        'current_quantity_by_sensor': stats['total_balloons'],
        'loading_ttn_quantity': stats.get('loading_ttn_quantity', 0),
        'unloading_ttn_quantity': stats.get('unloading_ttn_quantity', 0),
        'form': form,
        'reader': reader,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'filling_station/rfid_tables.html', context)


class BalloonBatchTypeMixin:
    """Определяет тип партии (приёмка/отгрузка) по URL."""

    def get_batch_type(self):
        """
        Извлекает тип партии из пути запроса.

        Returns:
            str | None: ``'u'`` (отгрузка), ``'l'`` (приёмка) или ``None``.
        """
        path = self.request.path.lower()
        if 'unloading' in path:
            return 'u'
        if 'loading' in path:
            return 'l'
        return None


# Единые классы для работы с партиями баллонов
class BalloonBatchListView(DateRangeListFilterMixin, BalloonBatchTypeMixin, generic.ListView):
    """Отображает список партий баллонов в зависимости от типа"""
    model = BalloonsBatch
    form_class = BalloonsBatchForm
    paginate_by = 10
    template_name = 'filling_station/balloon_batch_list.html'

    def get_list_query_filter(self):
        if hasattr(self, '_list_query_filter'):
            return self._list_query_filter
        query = self.request.GET.get('query', '').strip()
        self._list_query_filter = query
        return query

    def get_queryset(self):
        """
        Список партий с ТТН, отфильтрованный по типу, дате и номеру ТС/ТТН.

        Returns:
            QuerySet: Партии приёмки, отгрузки или все.
        """
        batch_type = self.get_batch_type()
        ttn_name_sq = MiriadaTtn.objects.filter(
            ttn_id=OuterRef('ttn_id')
        ).values('name')[:1]
        queryset = BalloonsBatch.objects.select_related(
            'truck', 'trailer', 'truck__type'
        ).annotate(ttn_name=Subquery(ttn_name_sq))
        if batch_type:
            queryset = queryset.filter(batch_type=batch_type)

        query = self.get_list_query_filter()
        queryset = self.apply_date_range_filter(queryset, field_name='started_at')
        if query:
            ttn_ids = MiriadaTtn.objects.filter(
                name__icontains=query,
            ).values_list('ttn_id', flat=True)
            queryset = queryset.filter(
                Q(truck__registration_number__icontains=query)
                | Q(ttn_id__in=ttn_ids)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.get_list_query_filter()
        context['query'] = query
        context['query_filter'] = resolve_batch_list_query_filter(query)
        return context


class BalloonBatchDetailView(BalloonBatchTypeMixin, generic.DetailView):
    """Отображает детальное представление партии баллонов"""
    model = BalloonsBatch
    context_object_name = 'batch'
    template_name = 'filling_station/balloon_batch_detail.html'

    def get_queryset(self):
        """
        Queryset партии с предзагрузкой баллонов и именем ТТН.

        Returns:
            QuerySet: Оптимизированный queryset с фильтром по типу партии.
        """
        ttn_name_sq = MiriadaTtn.objects.filter(
            ttn_id=OuterRef('ttn_id')
        ).values('name')[:1]
        queryset = BalloonsBatch.objects.select_related(
            'truck', 'trailer', 'truck__type'
        ).prefetch_related(
            Prefetch('balloon_list', queryset=Balloon.objects.order_by('nfc_tag'))
        ).annotate(ttn_name=Subquery(ttn_name_sq))
        batch_type = self.get_batch_type()
        if batch_type:
            queryset = queryset.filter(batch_type=batch_type)
        return queryset


class BalloonBatchUpdateView(BalloonBatchTypeMixin, PreserveListQueryMixin, generic.UpdateView):
    """Универсальное редактирование партии баллонов"""
    model = BalloonsBatch
    form_class = BalloonsBatchForm
    template_name = 'filling_station/_equipment_form.html'

    def get_queryset(self):
        """
        Queryset партий с транспортом, ограниченный типом из URL.

        Returns:
            QuerySet: Партии для редактирования.
        """
        queryset = BalloonsBatch.objects.select_related('truck', 'trailer', 'truck__type')
        batch_type = self.get_batch_type()
        if batch_type:
            queryset = queryset.filter(batch_type=batch_type)
        return queryset

    def get_success_url(self):
        """
        URL карточки партии после сохранения.

        Returns:
            str: Абсолютный URL объекта.
        """
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает форму; при ``cancel`` возвращает на карточку партии.

        Returns:
            HttpResponse: Редирект или ответ базового ``post``.
        """
        if 'cancel' in request.POST:
            return redirect_preserve_query(request, self.get_object().get_absolute_url())
        return super().post(request, *args, **kwargs)


@require_POST
def balloon_batch_retry_close(request, pk):
    """Завершить партию: сохранить текущие данные и закрыть ТТН в Мириаде."""
    path = request.path.lower()
    batch_type = 'u' if 'unloading' in path else 'l'
    batch = get_object_or_404(BalloonsBatch, pk=pk, batch_type=batch_type)

    # Разрешаем повтор, только если есть флаг ошибки Мириады
    if batch.status != BatchStatus.MIRIADA_ERROR:
        messages.error(request, 'Партия не содержит ошибок.')
        return redirect_preserve_query(request, batch.get_absolute_url())

    success, error_payload, _ = save_and_close_balloons_batch(batch, request.POST)
    if success:
        messages.success(request, f'Партия №{batch.id} успешно завершена. ТТН закрыта в Мириаде.')
    elif isinstance(error_payload, dict) and error_payload.get('message'):
        messages.error(request, error_payload['message'])
    elif error_payload:
        messages.error(request, error_payload)

    return redirect_preserve_query(request, batch.get_absolute_url())


class BalloonBatchDeleteView(BalloonBatchTypeMixin, ModalDeleteMixin, PreserveListQueryMixin, generic.DeleteView):
    """Универсальное удаление партии баллонов"""
    model = BalloonsBatch

    def get_queryset(self):
        """
        Queryset партий для удаления с фильтром по типу из URL.

        Returns:
            QuerySet: Партии приёмки или отгрузки.
        """
        queryset = BalloonsBatch.objects.select_related('truck', 'trailer', 'truck__type')
        batch_type = self.get_batch_type()
        if batch_type:
            queryset = queryset.filter(batch_type=batch_type)
        return queryset

    def get_success_url(self):
        """
        Список партий того же типа после удаления.

        Returns:
            str: URL списка приёмки или отгрузки.
        """
        if self.get_batch_type() == 'u':
            return reverse_lazy("filling_station:balloon_unloading_batch_list")
        return reverse_lazy("filling_station:balloon_loading_batch_list")


# Алиасы для обратной совместимости
BalloonLoadingBatchListView = BalloonBatchListView
BalloonLoadingBatchDetailView = BalloonBatchDetailView
BalloonLoadingBatchUpdateView = BalloonBatchUpdateView
BalloonLoadingBatchDeleteView = BalloonBatchDeleteView

BalloonUnloadingBatchListView = BalloonBatchListView
BalloonUnloadingBatchDetailView = BalloonBatchDetailView
BalloonUnloadingBatchUpdateView = BalloonBatchUpdateView
BalloonUnloadingBatchDeleteView = BalloonBatchDeleteView


# Грузовики
class TruckView(generic.ListView):
    """Список тягачей с поиском по госномеру или марке."""

    model = Truck
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('type')
        query = self.request.GET.get('query', '').strip()
        if query:
            queryset = queryset.filter(
                Q(registration_number__icontains=query) | Q(car_brand__icontains=query)
            )
        return queryset


class TruckDetailView(generic.DetailView):
    model = Truck


class TruckCreateView(CancelFormMixin, PreserveListQueryMixin, generic.CreateView):
    model = Truck
    form_class = TruckForm
    template_name = 'filling_station/_equipment_form.html'
    cancel_url = reverse_lazy('filling_station:truck_list')

    def get_success_url(self):
        return self.object.get_absolute_url()


class TruckUpdateView(PreserveListQueryMixin, generic.UpdateView):
    model = Truck
    form_class = TruckForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return self.redirect_preserve_query('filling_station:truck_detail', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)


class TruckDeleteView(ModalDeleteMixin, PreserveListQueryMixin, generic.DeleteView):
    """Удаление тягача через модальное окно."""

    model = Truck
    success_url = reverse_lazy("filling_station:truck_list")


# Прицепы
class TrailerView(generic.ListView):
    """Список прицепов с поиском по госномеру или марке."""

    model = Trailer
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('type', 'truck')
        query = self.request.GET.get('query', '').strip()
        if query:
            queryset = queryset.filter(
                Q(registration_number__icontains=query) | Q(trailer_brand__icontains=query)
            )
        return queryset


class TrailerDetailView(generic.DetailView):
    model = Trailer


class TrailerCreateView(CancelFormMixin, PreserveListQueryMixin, generic.CreateView):
    model = Trailer
    form_class = TrailerForm
    template_name = 'filling_station/_equipment_form.html'
    cancel_url = reverse_lazy('filling_station:trailer_list')

    def get_success_url(self):
        return self.object.get_absolute_url()


class TrailerUpdateView(PreserveListQueryMixin, generic.UpdateView):
    model = Trailer
    form_class = TrailerForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return self.redirect_preserve_query('filling_station:trailer_detail', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)


class TrailerDeleteView(ModalDeleteMixin, PreserveListQueryMixin, generic.DeleteView):
    """Удаление прицепа через модальное окно."""

    model = Trailer
    success_url = reverse_lazy("filling_station:trailer_list")


# Обработка данных для вкладки "Статистика"
def statistic(request):
    current_date = datetime.now().date()

    if request.method == "POST":
        form = GetBalloonsAmount(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
        else:
            start_date = current_date
            end_date = current_date
    else:
        form = GetBalloonsAmount()
        start_date = current_date
        end_date = current_date

    context = {
        'readers_stats': Reader.get_all_readers_stats(start_date, end_date),
        'balloon_loading_stats': BalloonsBatch.get_period_stats(start_date, end_date, batch_type='l'),
        'balloon_unloading_stats': BalloonsBatch.get_period_stats(start_date, end_date, batch_type='u'),
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, "statistic.html", context)
