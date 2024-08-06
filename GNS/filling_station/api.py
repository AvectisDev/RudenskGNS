from django.http import JsonResponse
from .models import Balloon, Truck


def getBalloonPassport(request):
    nfc = request.GET.get("nfc", 0)
    balloons = Balloon.objects.filter(nfc_tag=nfc)
    print(balloons)
    return JsonResponse({
        'nfc_tag': balloons[0].nfc_tag,
        'serial_number': balloons[0].serial_number,
        'creation_date': balloons[0].creation_date,
        'size': balloons[0].size,
        'netto': balloons[0].netto,
        'brutto': balloons[0].brutto,
        'current_examination_date': balloons[0].current_examination_date,
        'next_examination_date': balloons[0].next_examination_date,
        'status': balloons[0].status
    })
