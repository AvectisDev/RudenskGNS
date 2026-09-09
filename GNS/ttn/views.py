from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.db.models import Q, Sum
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import BalloonTtn
from .forms import BalloonTtnForm
from .services import save_balloon_ttn

BALLOON_TTN_RELATED = (
    'shipper', 'consignee', 'carrier', 'city', 'loading_batch', 'unloading_batch',
)


# ТТН для баллонов
class TTNView(generic.ListView):
    model = BalloonTtn
    paginate_by = 10
    queryset = BalloonTtn.objects.select_related(*BALLOON_TTN_RELATED)


class TTNDetailView(generic.DetailView):
    model = BalloonTtn
    queryset = BalloonTtn.objects.select_related(*BALLOON_TTN_RELATED)


class TTNCreateView(generic.CreateView):
    model = BalloonTtn
    form_class = BalloonTtnForm
    template_name = 'ttn/_equipment_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        save_balloon_ttn(self.object)
        messages.success(self.request, f'ТТН {self.object.number} успешно создана')
        return redirect(self.get_success_url())


class TTNUpdateView(generic.UpdateView):
    model = BalloonTtn
    form_class = BalloonTtnForm
    template_name = 'ttn/_equipment_form.html'
    queryset = BalloonTtn.objects.select_related(*BALLOON_TTN_RELATED)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect('ttn:ttn_detail', pk=self.get_object().pk)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        save_balloon_ttn(self.object)
        messages.success(self.request, f'ТТН {self.object.number} успешно обновлена')
        return redirect(self.get_success_url())


class TTNDeleteView(generic.DeleteView):
    model = BalloonTtn
    success_url = reverse_lazy("ttn:ttn_list")
    template_name = 'ttn/balloonttn_confirm_delete.html'
