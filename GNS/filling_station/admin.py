from django.contrib import admin
from .models import Balloon, Truck
from import_export import resources


class BalloonResources(resources.ModelResource):
    class Meta:
        model = Balloon
        fields = ('id', 'nfc_tag', 'creation_date', 'state')


@admin.register(Balloon)
class BalloonAdmin(admin.ModelAdmin):
    list_display = ['id', 'nfc_tag', 'serial_number', 'creation_date', 'size', 'netto', 'brutto',
                    'current_examination_date', 'next_examination_date', 'manufacturer', 'wall_thickness', 'status']


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ['id', 'registration_number', 'type', 'max_capacity_cylinders_by_type',
                    'max_weight_of_transported_cylinders', 'max_mass_of_transported_gas', 'empty_weight',
                    'full_weight']
