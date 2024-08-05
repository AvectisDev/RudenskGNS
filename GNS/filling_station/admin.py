from django.contrib import admin
from .models import Balloon
from import_export import resources


class BalloonResources(resources.ModelResource):
    class Meta:
        model = Balloon
        fields = ('id', 'nfc_tag', 'creation_date', 'state')


# Register your models here.
admin.site.register(Balloon)
