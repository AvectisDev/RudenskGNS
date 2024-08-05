from django.db import models


class Balloon(models.Model):
    STATE = {"r": "Зарегистрирован", "f": "Наполнение", "e": "На рампе", "o": "Отгружен"}

    nfc_tag = models.CharField(blank=False, max_length=30, verbose_name="Номер метки")
    serial_number = models.CharField(null=True, blank=True, max_length=30, verbose_name="Серийный номер")
    creation_date = models.DateField(null=True, blank=True, verbose_name="Дата производства")
    capacity = models.FloatField(null=True, blank=True, verbose_name="Объём")
    empty_weight = models.FloatField(null=True, blank=True, verbose_name="Вес пустого баллона")
    full_weight = models.FloatField(null=True, blank=True, verbose_name="Вес наполненного баллона")
    current_examination_date = models.DateField(null=True, blank=True, verbose_name="Дата освидетельствования")
    next_examination_date = models.DateField(null=True, blank=True, verbose_name="Дата следующего освидетельствования")
    state = models.CharField(blank=True, max_length=50, verbose_name="Статус")

    def __str__(self):
        return self.nfc_tag

    class Meta:
        verbose_name = "Баллон"
        verbose_name_plural = "Баллоны"


class ChangeBalloonStatus(models.Model):
    cylinder = models.ForeignKey(Balloon, on_delete=models.CASCADE)
    change_status_date = models.DateField(null=True, blank=True, verbose_name="Дата смены статуса")
    change_status_time = models.TimeField(null=True, blank=True, verbose_name="Время смены статуса")
    status = models.CharField(blank=True, max_length=50, verbose_name="Статус")


class Truck(models.Model):
    registration_number = models.CharField(blank=False, max_length=10, verbose_name="Регистрационный знак")
    type = models.CharField(blank=False, max_length=50, verbose_name="Тип")
    maximum_capacity_cylinders_by_type = models.IntegerField(null=True, blank=True,
                                                             verbose_name="Максимальная вместимость баллонов")
    maximum_weight_of_transported_cylinders = models.IntegerField(null=True, blank=True,
                                                                  verbose_name="Максимальная масса перевозимых баллонов")
    maximum_mass_of_transported_gas = models.IntegerField(null=True, blank=True,
                                                          verbose_name="Максимальная масса перевозимого газа")
    empty_weight = models.IntegerField(null=True, blank=True, verbose_name="Вес пустого транспортного средства")
    full_weight = models.IntegerField(null=True, blank=True, verbose_name="Вес полного транспортного средства")
