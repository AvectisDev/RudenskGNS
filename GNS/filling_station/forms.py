from django import forms
from django.utils import timezone
from .models import Balloon, Truck, Trailer, AutoGasBatch, BalloonsLoadingBatch, BalloonsUnloadingBatch, BALLOON_SIZE_CHOICES
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

USER_STATUS_LIST = [
    ('Создание паспорта баллона', 'Создание паспорта баллона'),
    ('Наполнение баллона сжиженным газом', 'Наполнение баллона сжиженным газом'),
    ('Погрузка пустого баллона в трал', 'Погрузка пустого баллона в трал'),
    ('Снятие RFID метки', 'Снятие RFID метки'),
    ('Установка новой RFID метки', 'Установка новой RFID метки'),
    ('Редактирование паспорта баллона', 'Редактирование паспорта баллона'),
    ('Покраска', 'Покраска'),
    ('Техническое освидетельствование', 'Техническое освидетельствование'),
    ('Выбраковка', 'Выбраковка'),
    ('Утечка газа', 'Утечка газа'),
    ('Опорожнение(слив) баллона', 'Опорожнение(слив) баллона'),
    ('Контрольное взвешивание', 'Контрольное взвешивание'),
]


class GetBalloonsAmount(forms.Form):
    start_date = forms.DateField(
        label="Начальная дата",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    end_date = forms.DateField(
        label="Конечная дата",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'POST'


class BalloonForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('Сохранить', 'Сохранить', css_class='btn btn-success'))
        self.helper.form_method = 'POST'

    class Meta:
        model = Balloon
        fields = ['nfc_tag', 'serial_number', 'creation_date', 'size', 'netto', 'brutto', 'current_examination_date',
                  'next_examination_date', 'diagnostic_date', 'working_pressure', 'status', 'manufacturer',
                  'wall_thickness', 'filling_status', 'update_passport_required']
        widgets = {
            'nfc_tag': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'creation_date': forms.DateInput(attrs={'type': 'date'}),
            'size': forms.Select(choices=BALLOON_SIZE_CHOICES, attrs={'class': 'form-control'}),
            'netto': forms.NumberInput(attrs={'class': 'form-control'}),
            'brutto': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_examination_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'next_examination_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'diagnostic_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'working_pressure': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(choices=USER_STATUS_LIST, attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'wall_thickness': forms.NumberInput(attrs={'class': 'form-control'}),
            'filling_status': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'update_passport_required': forms.CheckboxInput(attrs={'class': 'form-control'})
        }


class TruckForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('Сохранить', 'Сохранить', css_class='btn btn-success'))
        self.helper.form_method = 'POST'

    class Meta:
        model = Truck
        fields = [
            'car_brand',
            'registration_number',
            'type',
            'capacity_cylinders',
            'max_weight_of_transported_cylinders',
            'max_mass_of_transported_gas',
            'max_gas_volume',
            'empty_weight',
            'full_weight',
            'is_on_station',
            'entry_date',
            'entry_time',
            'departure_date',
            'departure_time'
        ]
        widgets = {
            'car_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'capacity_cylinders': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_weight_of_transported_cylinders': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_mass_of_transported_gas': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_gas_volume': forms.NumberInput(attrs={'class': 'form-control'}),
            'empty_weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'full_weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_on_station': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'entry_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'entry_time': forms.TimeInput(attrs={'type': 'time'}),
            'departure_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'})
        }


class TrailerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('Сохранить', 'Сохранить', css_class='btn btn-success'))
        self.helper.form_method = 'POST'

    class Meta:
        model = Trailer
        fields = [
            'truck',
            'trailer_brand',
            'registration_number',
            'type',
            'capacity_cylinders',
            'max_weight_of_transported_cylinders',
            'max_mass_of_transported_gas',
            'max_gas_volume',
            'empty_weight',
            'full_weight',
            'is_on_station',
            'entry_date',
            'entry_time',
            'departure_date',
            'departure_time'
        ]
        widgets = {
            'truck': forms.Select(attrs={'class': 'form-control'}),
            'trailer_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'capacity_cylinders': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_weight_of_transported_cylinders': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_mass_of_transported_gas': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_gas_volume': forms.NumberInput(attrs={'class': 'form-control'}),
            'empty_weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'full_weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_on_station': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'entry_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'entry_time': forms.TimeInput(attrs={'type': 'time'}),
            'departure_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'})
        }


class BalloonsLoadingBatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('Сохранить', 'Сохранить', css_class='btn btn-success'))
        self.helper.form_method = 'POST'

        self.fields['truck'].empty_label = 'Выберите автомобиль'
        self.fields['trailer'].empty_label = 'Выберите прицеп'

    class Meta:
        model = BalloonsLoadingBatch
        fields = [
            'end_date',
            'end_time',
            'truck',
            'trailer',
            'reader_number',
            'amount_of_rfid',
            'amount_of_5_liters',
            'amount_of_12_liters',
            'amount_of_27_liters',
            'amount_of_50_liters',
            'gas_amount',
            'is_active',
            'ttn',
            'amount_of_ttn'
        ]
        widgets = {
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'truck': forms.Select(attrs={
                'class': 'form-control'
            }),
            'trailer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reader_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите номер считывателя'
            }),
            'amount_of_rfid': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Количество по RFID'
            }),
            'amount_of_5_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'amount_of_12_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'amount_of_27_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'amount_of_50_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'gas_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Количество газа',
                'step': '0.01'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ttn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер ТТН'
            }),
            'amount_of_ttn': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Количество по ТТН'
            })
        }
        labels = {
            'amount_of_ttn': 'Количество баллонов по ТТН',
            'ttn': 'Номер ТТН'
        }


class BalloonsUnloadingBatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('Сохранить', 'Сохранить', css_class='btn btn-success'))
        self.helper.form_method = 'POST'

        self.fields['truck'].empty_label = 'Выберите автомобиль'
        self.fields['trailer'].empty_label = 'Выберите прицеп'

    class Meta:
        model = BalloonsUnloadingBatch
        fields = [
            'end_date',
            'end_time',
            'truck',
            'trailer',
            'reader_number',
            'amount_of_rfid',
            'amount_of_5_liters',
            'amount_of_12_liters',
            'amount_of_27_liters',
            'amount_of_50_liters',
            'gas_amount',
            'is_active',
            'ttn',
            'amount_of_ttn'
        ]
        widgets = {
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'truck': forms.Select(attrs={
                'class': 'form-control'
            }),
            'trailer': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reader_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите номер считывателя'
            }),
            'amount_of_rfid': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Количество по RFID'
            }),
            'amount_of_5_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'amount_of_12_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'amount_of_27_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'amount_of_50_liters': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'gas_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Количество газа',
                'step': '0.01'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ttn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер ТТН'
            }),
            'amount_of_ttn': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Количество по ТТН'
            })
        }
        labels = {
            'amount_of_ttn': 'Количество баллонов по ТТН',
            'ttn': 'Номер ТТН'
        }


class AutoGasBatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('Сохранить', 'Сохранить', css_class='btn btn-success'))
        self.helper.form_method = 'POST'

        self.fields['truck'].empty_label = 'Выберите автомобиль'
        self.fields['trailer'].empty_label = 'Выберите прицеп'

        self.fields['end_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['end_time'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = AutoGasBatch
        fields = [
            'batch_type',
            'end_date',
            'end_time',
            'truck',
            'trailer',
            'gas_amount',
            'gas_type',
            'scale_empty_weight',
            'scale_full_weight',
            'weight_gas_amount',
            'is_active'
        ]
        widgets = {
            'batch_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'truck': forms.Select(attrs={
                'class': 'form-control',
            }),
            'trailer': forms.Select(attrs={
                'class': 'form-control',
            }),
            'gas_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите количество газа по массомеру',
                'step': '0.01'
            }),
            'gas_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'scale_empty_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Вес пустого транспорта',
                'step': '0.01'
            }),
            'scale_full_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Вес груженого транспорта',
                'step': '0.01'
            }),
            'weight_gas_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Количество газа по весам',
                'step': '0.01'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            })
        }
        labels = {
            'weight_gas_amount': 'Количество газа (по весам)',
            'gas_amount': 'Количество газа (по массомеру)'
        }

    def clean(self):
        cleaned_data = super().clean()

        # Проверка, что дата окончания не раньше даты начала
        if self.instance.pk and cleaned_data.get('end_date'):
            if cleaned_data['end_date'] < self.instance.begin_date:
                raise forms.ValidationError(
                    "Дата окончания не может быть раньше даты начала"
                )

        # Проверка весовых показателей
        scale_empty = cleaned_data.get('scale_empty_weight')
        scale_full = cleaned_data.get('scale_full_weight')
        weight_gas = cleaned_data.get('weight_gas_amount')

        if scale_empty and scale_full:
            if scale_full <= scale_empty:
                raise forms.ValidationError(
                    "Вес груженого транспорта должен быть больше веса пустого"
                )

            calculated_gas = scale_full - scale_empty
            if weight_gas and abs(weight_gas - calculated_gas) > 0.1:
                raise forms.ValidationError(
                    f"Расчетное количество газа ({calculated_gas:.2f}) не совпадает с введенным ({weight_gas:.2f})"
                )

        return cleaned_data
