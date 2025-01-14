import logging
import time
from ..models import (Balloon, BalloonAmount, BalloonsLoadingBatch, BalloonsUnloadingBatch)
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import datetime, date
from .serializers import (BalloonSerializer, BalloonAmountSerializer,
                          BalloonsLoadingBatchSerializer, BalloonsUnloadingBatchSerializer,
                          ActiveLoadingBatchSerializer, ActiveUnloadingBatchSerializer,
                          BalloonAmountLoadingSerializer, BalloonAmountUnloadingSerializer)

USER_STATUS_LIST = [
    'Создание паспорта баллона',
    'Наполнение баллона сжиженным газом',
    'Погрузка полного баллона в кассету',
    'Погрузка полного баллона в трал',
    'Погрузка пустого баллона в кассету',
    'Погрузка пустого баллона в трал',
    'Регистрация полного баллона на складе',
    'Регистрация пустого баллона на складе',
    'Снятие пустого баллона у потребителя',
    'Установка баллона потребителю',
    'Принятие баллона от другой организации',
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

logger = logging.getLogger('filling_station')

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
    def update_by_reader(self, request):
        nfc_tag = request.data.get('nfc_tag')
        balloon, created = Balloon.objects.get_or_create(
            nfc_tag=nfc_tag,
            defaults={
                'status': request.data.get('status'),
                'update_passport_required': True
            }
        )
        if not created:
            balloon.status = request.data.get('status')
            if balloon.update_passport_required:
                balloon.update_passport_required = request.data.get('update_passport_required')
                balloon.serial_number = request.data.get('serial_number')
                balloon.netto = request.data.get('netto')
                balloon.brutto = request.data.get('brutto')
                balloon.filling_status = request.data.get('filling_status', False)
            balloon.save()

        reader_number = request.data.get('reader_number')
        reader_function = request.data.get('reader_function')
        if reader_function:
            self.add_balloon_to_batch_from_reader(balloon, reader_number, reader_function)

        serializer = BalloonSerializer(balloon)
        return Response(serializer.data)

    def add_balloon_to_batch_from_reader(self, balloon, reader_number, batch_type):
        today = date.today()

        if batch_type == 'loading':
            batch = BalloonsLoadingBatch.objects.filter(begin_date=today,
                                                        reader_number=reader_number,
                                                        is_active=True).first()
        elif batch_type == 'unloading':
            batch = BalloonsUnloadingBatch.objects.filter(begin_date=today,
                                                          reader_number=reader_number,
                                                          is_active=True).first()
        else:
            batch = None

        if batch:
            batch.balloon_list.add(balloon)
            batch.amount_of_rfid = (batch.amount_of_rfid or 0) + 1
            batch.save()

    @action(detail=False, methods=['get'], url_path='statistic')
    def get_statistic(self, request):
        today = date.today()
        first_day_of_month = today.replace(day=1)

        # Баллонов на станции
        filled_balloons_on_station = (Balloon.objects
                                      .filter(status='Регистрация полного баллона на складе')
                                      .aggregate(total=Count('id')))
        empty_balloons_on_station = (Balloon.objects
                                     .filter(status__in=['Регистрация пустого баллона на складе (рампа)',
                                                         'Регистрация пустого баллона на складе (цех)'])
                                     .aggregate(total=Count('id')))

        # Баллонов за текущий месяц
        balloons_monthly_stats = (BalloonAmount.objects
                                  .filter(change_date__gte=first_day_of_month)
                                  .order_by('reader_id')
                                  .values('reader_id')
                                  .annotate(balloons_month=Sum('amount_of_balloons'), rfid_month=Sum('amount_of_rfid'))
                                  )

        # Баллонов за текущий день
        balloons_today_stats = (BalloonAmount.objects
                                .filter(change_date=today)
                                .values('reader_id')
                                .annotate(balloons_today=Sum('amount_of_balloons'), rfid_today=Sum('amount_of_rfid')))

        # Партий за текущий месяц
        loading_batches_last_month = (BalloonsLoadingBatch.objects
                                      .filter(begin_date__gte=first_day_of_month)
                                      .values('reader_number')
                                      .annotate(month_batches=Count('id'))
                                      )
        unloading_batches_last_month = (BalloonsUnloadingBatch.objects
                                        .filter(begin_date__gte=first_day_of_month)
                                        .values('reader_number')
                                        .annotate(month_batches=Count('id'))
                                        )
        # Объединяем результаты по партиям за последний месяц
        batches_last_month = {}
        for batch in loading_batches_last_month:
            reader_number = batch['reader_number']
            batches_last_month[reader_number] = batches_last_month.get(reader_number, 0) + batch['month_batches']

        for batch in unloading_batches_last_month:
            reader_number = batch['reader_number']
            batches_last_month[reader_number] = batches_last_month.get(reader_number, 0) + batch['month_batches']

        # Партий за текущий день
        loading_batches_last_day = (BalloonsLoadingBatch.objects
                                    .filter(begin_date=today)
                                    .values('reader_number')
                                    .annotate(day_batches=Count('id'))
                                    )
        unloading_batches_last_day = (BalloonsUnloadingBatch.objects
                                      .filter(begin_date=today)
                                      .values('reader_number')
                                      .annotate(day_batches=Count('id'))
                                      )
        # Объединяем результаты по партиям за последний день
        batches_last_day = {}
        for batch in loading_batches_last_day:
            reader_number = batch['reader_number']
            batches_last_day[reader_number] = batches_last_day.get(reader_number, 0) + batch['day_batches']

        for batch in unloading_batches_last_day:
            reader_number = batch['reader_number']
            batches_last_day[reader_number] = batches_last_day.get(reader_number, 0) + batch['day_batches']

        # Преобразуем данные по баллонам за сегодня в словарь для быстрого доступа
        today_dict = {stat['reader_id']: stat for stat in balloons_today_stats}

        # Объединяем данные
        response = []
        for stat in balloons_monthly_stats:
            reader_id = stat['reader_id']
            balloons_today = today_dict.get(reader_id, {}).get('balloons_today', 0)
            rfid_today = today_dict.get(reader_id, {}).get('rfid_today', 0)
            truck_month = batches_last_month.get(reader_id, 0)
            truck_today = batches_last_day.get(reader_id, 0)

            # Создаем новый словарь с данными
            response.append({
                'reader_id': reader_id,
                'balloons_month': stat['balloons_month'],
                'rfid_month': stat['rfid_month'],
                'balloons_today': balloons_today,
                'rfid_today': rfid_today,
                'truck_month': truck_month,
                'truck_today': truck_today
            })

        response.append({
            'filled_balloons_on_station': filled_balloons_on_station.get('total', 0),
            'empty_balloons_on_station': empty_balloons_on_station.get('total', 0)
        })
        return JsonResponse(response, safe=False)

    def create(self, request):
        nfc_tag = request.data.get('nfc_tag', None)
        balloons = Balloon.objects.filter(nfc_tag=nfc_tag).exists()
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
            if batch.balloon_list.filter(id=balloon_id).exists():
                return Response(status=status.HTTP_409_CONFLICT)
            else:
                batch.balloon_list.add(balloon)
                batch.amount_of_rfid = (batch.amount_of_rfid or 0) + 1
                batch.save()
                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='remove-balloon')
    def remove_balloon(self, request, pk=None):
        balloon_id = request.data.get('balloon_id', None)
        batch = get_object_or_404(BalloonsLoadingBatch, id=pk)

        if balloon_id:
            balloon = get_object_or_404(Balloon, id=balloon_id)
            if batch.balloon_list.filter(id=balloon_id).exists():
                batch.balloon_list.remove(balloon)
                if batch.amount_of_rfid:
                    batch.amount_of_rfid -= 1
                else:
                    batch.amount_of_rfid = 0
                batch.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_400_BAD_REQUEST)


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
            if batch.balloon_list.filter(id=balloon_id).exists():
                return Response(status=status.HTTP_409_CONFLICT)
            else:
                batch.balloon_list.add(balloon)
                batch.amount_of_rfid = (batch.amount_of_rfid or 0) + 1
                batch.save()
                return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='remove-balloon')
    def remove_balloon(self, request, pk=None):
        balloon_id = request.data.get('balloon_id', None)
        batch = get_object_or_404(BalloonsUnloadingBatch, id=pk)

        if balloon_id:
            balloon = get_object_or_404(Balloon, id=balloon_id)
            if batch.balloon_list.filter(id=balloon_id).exists():
                batch.balloon_list.remove(balloon)
                if batch.amount_of_rfid:
                    batch.amount_of_rfid -= 1
                else:
                    batch.amount_of_rfid = 0
                batch.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_400_BAD_REQUEST)


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

        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_active_balloon_batch(request):
    today = date.today()
    # Активные партии на сегодня
    loading_batches = (BalloonsLoadingBatch.objects
                       .filter(begin_date=today, is_active=True))
    unloading_batches = (BalloonsUnloadingBatch.objects
                         .filter(begin_date=today, is_active=True))

    response = []
    for batch in loading_batches:
        response.append({
            'reader_id': batch.reader_number,
            'truck_registration_number': batch.truck.registration_number,
            'trailer_registration_number': batch.trailer.registration_number
        })
    for batch in unloading_batches:
        response.append({
            'reader_id': batch.reader_number,
            'truck_registration_number': batch.truck.registration_number,
            'trailer_registration_number': batch.trailer.registration_number
        })
    return JsonResponse(response, safe=False)
