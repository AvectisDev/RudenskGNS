from django import forms
from .models import Balloon


class Process(forms.Form):
    truck_number = forms.CharField(max_length=15, label="Госномер автомобиля", widget=forms.TextInput(attrs={'placeholder': '1234 AA-1'}))
    phone_number = forms.CharField(max_length=15, label="Номер телефона", widget=forms.TextInput(attrs={'placeholder': '375291112233'}))
    company = forms.CharField(max_length=200, label="Компания")

    def clean_phone_number(self):
        phone_number_data = self.cleaned_data["phone_number"]
        if not phone_number_data.isdigit():
            raise forms.ValidationError("Номер телефона должен состоять только из цифр")
        return phone_number_data


class GetBalloonsAmount(forms.Form):
    date = forms.CharField(max_length=10, label="Дата", widget=forms.TextInput(attrs={'placeholder': 'дд.мм.гггг'}))

    def clean_data(self):
        date_data = self.cleaned_data["date"]
        if date_data is None or len(date_data) != 10:
            raise forms.ValidationError("Поле не может быть пустым")
        return date_data


class BalloonPassportForm(forms.Form):
    nfc_tag = forms.CharField(max_length=30, label="Метка", widget=forms.TextInput())
    serial_number = forms.CharField(max_length=30, label="Серийный номер", widget=forms.TextInput())
    creation_date = forms.DateField(label="Дата производства")
    size = forms.FloatField(min_value=0.0, max_value=100.0, label="Объём")
    netto = forms.FloatField(min_value=0.0, max_value=100.0, label="Вес нетто")
    brutto = forms.FloatField(min_value=0.0, max_value=100.0, label="Вес брутто")
    current_examination_date = forms.DateField(label="Дата освидетельствования", widget=forms.SelectDateWidget)
    next_examination_date = forms.DateField(label="Дата следующего освидетельствования", widget=forms.SelectDateWidget)
    manufacturer = forms.CharField(label="Производитель")
    wall_thickness = forms.FloatField(label="Толщина стенок")
    status = forms.ChoiceField(label="Статус", choices=((1, "English"), (2, "German"), (3, "French")))


