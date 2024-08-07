from django.db import models
from django.contrib.auth.models import User


class Balloon(models.Model):
    STATE = {"r": "Зарегистрирован", "f": "Наполнение", "e": "На рампе", "o": "Отгружен"}

    nfc_tag = models.CharField(blank=False, max_length=30, verbose_name="Номер метки")
    serial_number = models.CharField(null=True, blank=True, max_length=30, verbose_name="Серийный номер")
    creation_date = models.DateField(null=True, blank=True, verbose_name="Дата производства")
    size = models.FloatField(null=True, blank=True, verbose_name="Объём")
    netto = models.FloatField(null=True, blank=True, verbose_name="Вес пустого баллона")
    brutto = models.FloatField(null=True, blank=True, verbose_name="Вес наполненного баллона")
    current_examination_date = models.DateField(null=True, blank=True, verbose_name="Дата освидетельствования")
    next_examination_date = models.DateField(null=True, blank=True, verbose_name="Дата следующего освидетельствования")
    manufacturer = models.CharField(null=True, blank=True, max_length=30, verbose_name="Производитель")
    wall_thickness = models.FloatField(null=True, blank=True, verbose_name="Толщина стенок")
    status = models.CharField(blank=True, max_length=100, verbose_name="Статус")
    change_date = models.DateField(null=True, blank=True, auto_now_add=True, verbose_name="Дата изменений")
    change_time = models.TimeField(null=True, blank=True, auto_now_add=True, verbose_name="Время изменений")

    def __str__(self):
        return self.nfc_tag

    class Meta:
        verbose_name = "Баллон"
        verbose_name_plural = "Баллоны"


class Truck(models.Model):
    registration_number = models.CharField(blank=False, max_length=10, verbose_name="Регистрационный знак")
    type = models.CharField(blank=False, max_length=50, verbose_name="Тип")
    max_capacity_cylinders_by_type = models.IntegerField(null=True, blank=True,
                                                         verbose_name="Максимальная вместимость баллонов")
    max_weight_of_transported_cylinders = models.IntegerField(null=True, blank=True,
                                                              verbose_name="Максимальная масса перевозимых баллонов")
    max_mass_of_transported_gas = models.IntegerField(null=True, blank=True,
                                                      verbose_name="Максимальная масса перевозимого газа")
    empty_weight = models.IntegerField(null=True, blank=True, verbose_name="Вес пустого т/с")
    full_weight = models.IntegerField(null=True, blank=True, verbose_name="Вес полного т/с")

    def __str__(self):
        return self.registration_number

    class Meta:
        verbose_name = "Грузовик"
        verbose_name_plural = "Грузовики"


class BalloonAmount(models.Model):
    reader_id = models.IntegerField(null=True, blank=True, verbose_name="Номер считывателя")
    amount_of_balloons = models.IntegerField(null=True, blank=True, verbose_name="Количество баллонов по датчику")
    change_date = models.DateField(null=True, blank=True, auto_now_add=True, verbose_name="Дата обновления")
    change_time = models.TimeField(null=True, blank=True, auto_now_add=True, verbose_name="Время обновления")
