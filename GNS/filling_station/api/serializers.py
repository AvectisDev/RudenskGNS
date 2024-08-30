from rest_framework import serializers
from ..models import Balloon


class BalloonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balloon
        fields = ['id', 'nfc_tag', 'serial_number', 'creation_date', 'size', 'netto', 'brutto',
                  'current_examination_date', 'next_examination_date', 'manufacturer', 'wall_thickness', 'status']
