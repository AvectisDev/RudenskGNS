from django import forms
from django.utils.html import format_html
from django.conf import settings
from filling_station.models import BalloonsLoadingBatch, BalloonsUnloadingBatch
from .models import BalloonTtn
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class BalloonTtnForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('save', 'Сохранить', css_class='btn btn-success'))
        self.helper.add_input(Submit('cancel', 'Отмена', css_class='btn btn-secondary'))
        self.helper.form_method = 'POST'

        self.fields['shipper'].empty_label = 'Выберите грузоотправителя'
        self.fields['carrier'].empty_label = 'Выберите перевозчика'
        self.fields['consignee'].empty_label = 'Выберите грузополучателя'
        self.fields['city'].empty_label = 'Выберите город'
        self.fields['loading_batch'].empty_label = 'Выберите партию приёмки'
        self.fields['unloading_batch'].empty_label = 'Выберите партию отгрузки'

        # Добавляем ID для JS, но оставляем поле редактируемым
        self.fields['number'].widget.attrs.update({
            'id': 'id_ttn_number',
            'class': 'form-control',
            'placeholder': 'Номер заполнится автоматически или введите вручную'
        })

        # Оптимизированные запросы для партий с select_related
        self.fields['loading_batch'].queryset = BalloonsLoadingBatch.objects.select_related('truck')
        self.fields['unloading_batch'].queryset = BalloonsUnloadingBatch.objects.select_related('truck')

        self.fields['loading_batch'].label_from_instance = self.format_batch_choice
        self.fields['unloading_batch'].label_from_instance = self.format_batch_choice

        # Добавляем data-атрибуты для выпадающих списков
        self.fields['loading_batch'].widget.attrs['data-ttn-field'] = 'id_ttn_number'
        self.fields['unloading_batch'].widget.attrs['data-ttn-field'] = 'id_ttn_number'

    def format_batch_choice(self, obj):
        """Форматирует отображение партии в выпадающем списке"""
        if isinstance(obj, BalloonsLoadingBatch):
            batch_type = 'Приёмка'
        else:
            batch_type = 'Отгрузка'

        truck_number = obj.truck.registration_number if obj.truck else '---'
        ttn_number = obj.ttn if obj.ttn else '---'

        return format_html(
            '<span data-ttn="{}">{} №{} | Автомобиль: {} | ТТН: {}</span>',
            ttn_number,
            batch_type,
            obj.id,
            truck_number,
            ttn_number
        )

    class Meta:
        model = BalloonTtn
        fields = [
            'number',
            'contract',
            'shipper',
            'carrier',
            'consignee',
            'city',
            'loading_batch',
            'unloading_batch'
        ]
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер заполнится автоматически'
            }),
            'contract': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер договора'
            }),
            'shipper': forms.Select(attrs={
                'class': 'form-control',
            }),
            'carrier': forms.Select(attrs={
                'class': 'form-control',
            }),
            'consignee': forms.Select(attrs={
                'class': 'form-control',
            }),
            'city': forms.Select(attrs={
                'class': 'form-control',
            }),
            'loading_batch': forms.Select(attrs={
                'class': 'form-control',
            }),
            'unloading_batch': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        loading_batch = cleaned_data.get('loading_batch')
        unloading_batch = cleaned_data.get('unloading_batch')

        if loading_batch and unloading_batch:
            raise forms.ValidationError("Выберите только партию приёмки ИЛИ партию отгрузки, не обе одновременно")

        return cleaned_data
