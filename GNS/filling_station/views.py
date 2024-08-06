from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.core.paginator import Paginator
from .models import Balloon
from .admin import BalloonResources
from .forms import Process, GetBalloonsAmount
from datetime import datetime, date, time, timedelta


def index(request):
    balloons = Balloon.objects.all()
    return render(request, "home.html", {"balloons": balloons})


def apiGetBalloonPassport(request):
    nfc = request.GET.get("nfc", 0)
    balloons = Balloon.objects.order_by('-id').filter(nfc_tag=nfc)
    # serialized_queryset = serializers.serialize('json', balloon)
    return JsonResponse({
        'nfc_tag': balloons[0].nfc_tag,
        'serial_number': balloons[0].serial_number,
        'creation_date': balloons[0].creation_date,
        'capacity': balloons[0].capacity,
        'empty_weight': balloons[0].empty_weight,
        'full_weight': balloons[0].full_weight,
        'current_examination_date': balloons[0].current_examination_date,
        'next_examination_date': balloons[0].next_examination_date,
        'status': balloons[0].status
    })


def reader_info(request, reader='1'):
    if reader == '1':
        status = 'Регистрация пустого баллона на складе (цех)'
    elif reader == '2':
        status = 'Наполнение баллона сжиженным газом'
    elif reader == '3':
        status = 'Регистрация пустого баллона на складе (рампа)'
    elif reader == '4':
        status = 'Регистрация полного баллона на складе'
    elif reader == '5':
        status = 'Погрузка полного баллона на трал 2'
    elif reader == '6':
        status = 'Погрузка полного баллона на трал 1'
    elif reader == '7':
        status = 'Погрузка полного баллона в кассету'
    elif reader == '8':
        status = 'Регистрация пустого баллона на складе (из кассеты)'

    balloons = Balloon.objects.order_by('-id').filter(state=status)
    paginator = Paginator(balloons, 15)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    date_process = GetBalloonsAmount()
    if request.method == "POST":
        required_date = request.POST.get("date")
        format_required_date = datetime.strptime(required_date, '%d.%m.%Y')

        dataset = BalloonResources().export(Balloon.objects.filter(state=status, creation_date=format_required_date))
        response = HttpResponse(dataset.xls, content_type='xls')
        response[
            'Content-Disposition'] = f'attachment; filename="RFID_1_{datetime.strftime(format_required_date, '%Y.%m.%d')}.xls"'
        return response
    else:
        date_process = GetBalloonsAmount()
        format_required_date = datetime.today()

    last_date_amount = len(balloons.filter(creation_date=datetime.today()))
    previous_date_amount = len(balloons.filter(creation_date=datetime.today() - timedelta(days=1)))
    required_date_amount = len(balloons.filter(creation_date=format_required_date))

    view_required_data = datetime.strftime(format_required_date, '%d.%m.%Y')

    return render(request, "balloons_table.html", {
        "page_obj": page_obj,
        'balloons_amount': last_date_amount,
        'previous_balloons_amount': previous_date_amount,
        'required_date_amount': required_date_amount,
        'format_required_date': view_required_data,
        'form': date_process})
