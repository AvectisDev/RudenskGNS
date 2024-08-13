from django.http import HttpRequest, JsonResponse
from .models import Balloon, Truck
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


USER_STATUS_LIST = [
    'Принят',
    'Наполнен',
    'На наполнении',
    'На освидетельствовании',
    'Прошёл освидетельствование',
    'Отгружен',
    'Утилизация',
    'На покраске',
    'Покрашен',
]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balloon_passport(request):
    nfc = request.GET.get("nfc", 0)
    balloons = Balloon.objects.order_by('-id').filter(nfc_tag=nfc)
    # serialized_queryset = serializers.serialize('json', balloon)
    return JsonResponse({
        'nfc_tag': balloons[0].nfc_tag,
        'serial_number': balloons[0].serial_number,
        'creation_date': balloons[0].creation_date,
        'size': balloons[0].size,
        'netto': balloons[0].netto,
        'brutto': balloons[0].brutto,
        'current_examination_date': balloons[0].current_examination_date,
        'next_examination_date': balloons[0].next_examination_date,
        'status': balloons[0].status}
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_balloon_passport(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body.decode('utf-8'))
        nfc = data.get("nfc_tag")
        balloon = Balloon.objects.filter(nfc_tag=nfc).first()

        if not balloon:
            return JsonResponse({'error': 'Balloon not found'}, status=404)

        balloon.serial_number = data.get('serial_number')
        balloon.creation_date = data.get('creation_date')
        balloon.size = data.get('size')
        balloon.netto = data.get('netto')
        balloon.brutto = data.get('brutto')
        balloon.current_examination_date = data.get('current_examination_date')
        balloon.next_examination_date = data.get('next_examination_date')
        balloon.status = data.get('status')

        balloon.save()

        return JsonResponse({'error': 'OK'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balloon_state_options(request):
    try:
        return JsonResponse(USER_STATUS_LIST, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data'}, status=400)
