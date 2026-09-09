from rest_framework import serializers


class ApiErrorSerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
