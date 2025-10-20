from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.db.models import Q, Sum, Count
from .models import Balloon, Truck, Trailer, BalloonsLoadingBatch, BalloonsUnloadingBatch, Reader, ReaderSettings
from .admin import BalloonResources
from .forms import (
    GetBalloonsAmount,
    BalloonForm,
    TruckForm,
    TrailerForm,
    BalloonsLoadingBatchForm,
    BalloonsUnloadingBatchForm
)
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


class BalloonUpdateView(generic.UpdateView):
    model = Balloon
    form_class = BalloonForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect('filling_station:balloon_detail', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)


class BalloonDeleteView(generic.DeleteView):
    model = Balloon
    success_url = reverse_lazy("filling_station:balloon_list")
    template_name = 'filling_station/balloon_confirm_delete.html'


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


# Партии приёмки баллонов
class BalloonLoadingBatchListView(generic.ListView):
    model = BalloonsLoadingBatch
    paginate_by = 10
    template_name = 'filling_station/balloon_batch_list.html'


class BalloonLoadingBatchDetailView(generic.DetailView):
    model = BalloonsLoadingBatch
    context_object_name = 'batch'
    template_name = 'filling_station/balloon_batch_detail.html'


class BalloonLoadingBatchUpdateView(generic.UpdateView):
    model = BalloonsLoadingBatch
    form_class = BalloonsLoadingBatchForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect('filling_station:balloon_loading_batch_detail', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)


class BalloonLoadingBatchDeleteView(generic.DeleteView):
    model = BalloonsLoadingBatch
    success_url = reverse_lazy("filling_station:balloon_loading_batch_list")
    template_name = 'filling_station/balloons_loading_batch_confirm_delete.html'


# Партии отгрузки баллонов
class BalloonUnloadingBatchListView(generic.ListView):
    model = BalloonsUnloadingBatch
    paginate_by = 10
    template_name = 'filling_station/balloon_batch_list.html'


class BalloonUnloadingBatchDetailView(generic.DetailView):
    model = BalloonsUnloadingBatch
    context_object_name = 'batch'
    template_name = 'filling_station/balloon_batch_detail.html'


class BalloonUnloadingBatchUpdateView(generic.UpdateView):
    model = BalloonsUnloadingBatch
    form_class = BalloonsUnloadingBatchForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect('filling_station:balloon_unloading_batch_detail', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)


class BalloonUnloadingBatchDeleteView(generic.DeleteView):
    model = BalloonsUnloadingBatch
    success_url = reverse_lazy("filling_station:balloon_unloading_batch_list")
    template_name = 'filling_station/balloons_unloading_batch_confirm_delete.html'


# Грузовики
class TruckView(generic.ListView):
    model = Truck
    paginate_by = 10


class TruckDetailView(generic.DetailView):
    model = Truck


class TruckCreateView(generic.CreateView):
    model = Truck
    form_class = TruckForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()


class TruckUpdateView(generic.UpdateView):
    model = Truck
    form_class = TruckForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect('filling_station:truck_detail', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)


class TruckDeleteView(generic.DeleteView):
    model = Truck
    success_url = reverse_lazy("filling_station:truck_list")
    template_name = 'filling_station/truck_confirm_delete.html'


# Прицепы
class TrailerView(generic.ListView):
    model = Trailer
    paginate_by = 10


class TrailerDetailView(generic.DetailView):
    model = Trailer


class TrailerCreateView(generic.CreateView):
    model = Trailer
    form_class = TrailerForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()


class TrailerUpdateView(generic.UpdateView):
    model = Trailer
    form_class = TrailerForm
    template_name = 'filling_station/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect('filling_station:trailer_detail', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)


class TrailerDeleteView(generic.DeleteView):
    model = Trailer
    success_url = reverse_lazy("filling_station:trailer_list")
    template_name = 'filling_station/trailer_confirm_delete.html'


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
        'balloon_loading_stats': BalloonsLoadingBatch.get_period_stats(start_date, end_date),
        'balloon_unloading_stats': BalloonsUnloadingBatch.get_period_stats(start_date, end_date),
        'auto_gas_stats': AutoGasBatch.get_period_stats(start_date, end_date),
        'railway_stats': RailwayBatch.get_period_stats(start_date, end_date),
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, "statistic.html", context)
