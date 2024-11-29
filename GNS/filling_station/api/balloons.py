from ..models import (Balloon, BalloonAmount, BalloonsLoadingBatch, BalloonsUnloadingBatch)
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date
from .serializers import (BalloonSerializer, BalloonAmountSerializer,
                          BalloonsLoadingBatchSerializer, BalloonsUnloadingBatchSerializer,
                          ActiveLoadingBatchSerializer, ActiveUnloadingBatchSerializer,
                          BalloonAmountLoadingSerializer, BalloonAmountUnloadingSerializer)

USER_STATUS_LIST = [
    'Создание паспорта баллона',
    'Наполнение баллона сжиженным газом',
    'Погрузка пустого баллона в трал',
    'Снятие RFID метки',
    'Установка новой RFID метки',
    'Редактирование паспорта баллона',
    'Покраска',
    'Техническое освидетельствование',
    'Выбраковка',
    'Утечка газа',
    'Опорожнение(слив) баллона',
    'Контрольное взвешивание'
]
BALLOONS_LOADING_READER_LIST = [1, 6]
BALLOONS_UNLOADING_READER_LIST = [2, 3, 4]


class BalloonViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='nfc/(?P<nfc_tag>[^/.]+)')
    def get_by_nfc(self, request, nfc_tag=None):
        balloon = get_object_or_404(Balloon, nfc_tag=nfc_tag)
        serializer = BalloonSerializer(balloon)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='serial-number/(?P<serial_number>[^/.]+)')
    def get_by_serial_number(self, request, serial_number=None):
        balloons = Balloon.objects.filter(serial_number=serial_number)
        serializer = BalloonSerializer(balloons, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='update-by-reader')
    def update_by_reader(self, request, *args, **kwargs):
        nfc_tag = request.data.get('nfc_tag')
        instance, created = Balloon.objects.get_or_create(
            nfc_tag=nfc_tag,
            defaults={
                'status': request.data.get('status'),
                'update_passport_required': request.data.get('update_passport_required')
            }
        )
        if not created:
            instance.status = request.data.get('status')
            instance.save()
        serializer = BalloonSerializer(instance)
        return Response(serializer.data)

    def create(self, request):
        nfc_tag = request.data.get('nfc_tag', None)
        balloons = Balloon.objects.filter(nfc_tag=nfc_tag)
        if not balloons:
            serializer = BalloonSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_409_CONFLICT)

    def partial_update(self, request, pk=None):
        balloon = get_object_or_404(Balloon, id=pk)

        serializer = BalloonSerializer(balloon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_balloon_status_options(request):
    return Response(USER_STATUS_LIST)


@api_view(['GET'])
def get_loading_balloon_reader_list(request):
    return Response(BALLOONS_LOADING_READER_LIST)


@api_view(['GET'])
def get_unloading_balloon_reader_list(request):
    return Response(BALLOONS_UNLOADING_READER_LIST)


class BalloonsLoadingBatchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='active')
    def is_active(self, request):
        batches = BalloonsLoadingBatch.objects.filter(is_active=True)
        serializer = ActiveLoadingBatchSerializer(batches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='last-active')
    def last_active(self, request):
        batch = BalloonsLoadingBatch.objects.filter(is_active=True).first()
        if not batch:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BalloonsLoadingBatchSerializer(batch)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='rfid-amount')
    def rfid_amount(self, request, pk=None):
        batch = get_object_or_404(BalloonsLoadingBatch, id=pk)
        serializer = BalloonAmountLoadingSerializer(batch)
        return Response(serializer.data)

    def create(self, request):
        serializer = BalloonsLoadingBatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        batch = get_object_or_404(BalloonsLoadingBatch, id=pk)

        if not request.data.get('is_active', True):
            current_date = datetime.now()
            request.data['end_date'] = current_date.date()
            request.data['end_time'] = current_date.time()

        serializer = BalloonsLoadingBatchSerializer(batch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='add-balloon')
    def add_balloon(self, request, pk=None):
        balloon_id = request.data.get('balloon_id', None)
        batch = get_object_or_404(BalloonsLoadingBatch, id=pk)

        if balloon_id:
            balloon = get_object_or_404(Balloon, id=balloon_id)
            batch.balloon_list.add(balloon)
            if batch.amount_of_rfid:
                batch.amount_of_rfid += 1
            else:
                batch.amount_of_rfid = 1
            batch.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='remove-balloon')
    def remove_balloon(self, request, pk=None):
        balloon_id = request.data.get('balloon_id', None)
        batch = get_object_or_404(BalloonsLoadingBatch, id=pk)

        if balloon_id:
            balloon = get_object_or_404(Balloon, id=balloon_id)
            batch.balloon_list.add(balloon)
            if batch.amount_of_rfid:
                batch.amount_of_rfid -= 1
            else:
                batch.amount_of_rfid = 0
            batch.save()

        return Response(status=status.HTTP_200_OK)


class BalloonsUnloadingBatchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='active')
    def is_active(self, request):
        batches = BalloonsUnloadingBatch.objects.filter(is_active=True)
        serializer = ActiveUnloadingBatchSerializer(batches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='last-active')
    def last_active(self, request):
        batch = BalloonsUnloadingBatch.objects.filter(is_active=True).first()
        if not batch:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BalloonsUnloadingBatchSerializer(batch)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='rfid-amount')
    def rfid_amount(self, request, pk=None):
        batch = get_object_or_404(BalloonsUnloadingBatch, id=pk)
        serializer = BalloonAmountUnloadingSerializer(batch)
        return Response(serializer.data)

    def create(self, request):
        serializer = BalloonsUnloadingBatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        batch = get_object_or_404(BalloonsUnloadingBatch, id=pk)

        if not request.data.get('is_active', True):
            current_date = datetime.now()
            request.data['end_date'] = current_date.date()
            request.data['end_time'] = current_date.time()

        serializer = BalloonsUnloadingBatchSerializer(batch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='add-balloon')
    def add_balloon(self, request, pk=None):
        balloon_id = request.data.get('balloon_id', None)
        batch = get_object_or_404(BalloonsUnloadingBatch, id=pk)

        if balloon_id:
            balloon = get_object_or_404(Balloon, id=balloon_id)
            batch.balloon_list.add(balloon)
            if batch.amount_of_rfid:
                batch.amount_of_rfid += 1
            else:
                batch.amount_of_rfid = 1
            batch.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='remove-balloon')
    def remove_balloon(self, request, pk=None):
        balloon_id = request.data.get('balloon_id', None)
        batch = get_object_or_404(BalloonsUnloadingBatch, id=pk)

        if balloon_id:
            balloon = get_object_or_404(Balloon, id=balloon_id)
            batch.balloon_list.add(balloon)
            if batch.amount_of_rfid:
                batch.amount_of_rfid -= 1
            else:
                batch.amount_of_rfid = 0
            batch.save()

        return Response(status=status.HTTP_200_OK)


class BalloonAmountViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='update-amount-of-rfid')
    def update_amount_of_rfid(self, request, *args, **kwargs):
        today = date.today()
        reader_id = request.data.get('reader_id')
        instance, created = BalloonAmount.objects.get_or_create(
            change_date=today,
            reader_id=reader_id,
            defaults={
                'amount_of_rfid': 1,
                'amount_of_balloons': 0,
                'reader_status': request.data.get('reader_status')
            }
        )
        if not created:
            instance.amount_of_rfid += 1
            instance.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='update-amount-of-sensor')
    def update_amount_of_sensor(self, request, *args, **kwargs):
        today = date.today()
        reader_id = request.data.get('reader_id')
        instance, created = BalloonAmount.objects.get_or_create(
            change_date=today,
            reader_id=reader_id,
            defaults={
                'amount_of_rfid': 0,
                'amount_of_balloons': 1,
                'reader_status': request.data.get('reader_status')
            }
        )
        if not created:
            instance.amount_of_balloons += 1
            instance.save()
        serializer = BalloonAmountSerializer(instance)
        return Response(serializer.data)
