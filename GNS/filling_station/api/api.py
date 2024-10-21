from ..models import (Balloon, Truck, Trailer, RailwayTank, TTN, BalloonsLoadingBatch, BalloonsUnloadingBatch,
                      RailwayBatch, AutoGasBatch)
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from .serializers import (BalloonSerializer, TruckSerializer, TrailerSerializer, RailwayTankSerializer, TTNSerializer,
                          BalloonsLoadingBatchSerializer, BalloonsUnloadingBatchSerializer,
                          RailwayLoadingBatchSerializer, AutoGasBatchSerializer,
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


class BalloonView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nfc_tag = request.query_params.get('nfc_tag', False)
        serial_number = request.query_params.get('serial_number', False)

        if nfc_tag:
            balloon = get_object_or_404(Balloon, nfc_tag=nfc_tag)
            serializer = BalloonSerializer(balloon)
            return Response(serializer.data)

        elif serial_number:
            balloons = Balloon.objects.filter(serial_number=serial_number)
            if not balloons:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = BalloonSerializer(balloons, many=True)
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = BalloonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        nfc_tag = request.query_params.get('nfc_tag')
        balloon = get_object_or_404(Balloon, nfc_tag=nfc_tag)

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


class TruckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        on_station = request.query_params.get('on_station', False)
        registration_number = request.query_params.get('registration_number', False)

        if on_station:
            trucks = Truck.objects.filter(is_on_station=True)
            if not trucks:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = TruckSerializer(trucks, many=True)
            return Response(serializer.data)

        if registration_number:
            trucks = get_object_or_404(Truck, registration_number=registration_number)
            serializer = TruckSerializer(trucks)
            return Response(serializer.data)

    def post(self, request):
        serializer = TruckSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        truck_id = request.data['id']
        truck = get_object_or_404(Truck, id=truck_id)

        serializer = TruckSerializer(truck, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrailerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        on_station = request.query_params.get('on_station', False)
        registration_number = request.query_params.get('registration_number', False)

        if on_station:
            trailers = Trailer.objects.filter(is_on_station=True)
            if not trailers:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = TrailerSerializer(trailers, many=True)
            return Response(serializer.data)

        if registration_number:
            trailer = get_object_or_404(Trailer, registration_number=registration_number)
            serializer = TrailerSerializer(trailer)
            return Response(serializer.data)

    def post(self, request):
        serializer = TrailerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        trailer_id = request.data['id']
        trailer = get_object_or_404(Trailer, id=trailer_id)

        serializer = TrailerSerializer(trailer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RailwayTanksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        on_station = request.query_params.get('on_station', False)
        registration_number = request.query_params.get('registration_number', False)

        if on_station:
            railway_tanks = RailwayTank.objects.filter(is_on_station=True)
            if not railway_tanks:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = RailwayTankSerializer(railway_tanks, many=True)
            return Response(serializer.data)

        if registration_number:
            railway_tank = get_object_or_404(RailwayTank, registration_number=registration_number)
            serializer = RailwayTankSerializer(railway_tank)
            return Response(serializer.data)

    def post(self, request):
        serializer = RailwayTankSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        railway_tank_id = request.data['id']
        railway_tank = get_object_or_404(RailwayTank, id=railway_tank_id)

        serializer = RailwayTankSerializer(railway_tank, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class RailwayBatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        batches = RailwayBatch.objects.filter(is_active=True).first()

        if not batches:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = RailwayLoadingBatchSerializer(batches)
        return Response(serializer.data)

    def post(self, request):
        serializer = RailwayLoadingBatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        batch_id = request.data.get('id')
        batch = get_object_or_404(RailwayBatch, id=batch_id)

        if not request.data.get('is_active', True):
            current_date = datetime.now()
            request.data['end_date'] = current_date.date()
            request.data['end_time'] = current_date.time()

        serializer = RailwayLoadingBatchSerializer(batch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AutoGasBatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        batch = AutoGasBatch.objects.filter(is_active=True).first()

        if not batch:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = AutoGasBatchSerializer(batch)
        return Response(serializer.data)

    def post(self, request):
        serializer = AutoGasBatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        batch_id = request.data.get('id')
        batch = get_object_or_404(AutoGasBatch, id=batch_id)

        if not request.data.get('is_active', True):
            current_date = datetime.now()
            request.data['end_date'] = current_date.date()
            request.data['end_time'] = current_date.time()

        serializer = AutoGasBatchSerializer(batch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
