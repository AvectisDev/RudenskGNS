from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import Balloon
from .admin import BalloonResources
from .forms import Process, GetBalloonsAmount
from datetime import datetime, timedelta


STATUS_LIST = {
    '1': 'Регистрация пустого баллона на складе (цех)',
    '2': 'Наполнение баллона сжиженным газом',
    '3': 'Регистрация пустого баллона на складе (рампа)',
    '4': 'Регистрация полного баллона на складе',
    '5': 'Погрузка полного баллона на трал 2',
    '6': 'Погрузка полного баллона на трал 1',
    '7': 'Погрузка полного баллона в кассету',
    '8': 'Регистрация пустого баллона на складе (из кассеты)',
}


def index(request):
    balloons = Balloon.objects.all()
    return render(request, "home.html", {"balloons": balloons})


def reader_info(request, reader='1'):
    balloons = Balloon.objects.filter(status=STATUS_LIST[reader])
    paginator = Paginator(balloons, 15)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    date_process = GetBalloonsAmount()
    if request.method == "POST":
        required_date = request.POST.get("date")
        format_required_date = datetime.strptime(required_date, '%d.%m.%Y')

        dataset = BalloonResources().export(Balloon.objects.filter(state=STATUS_LIST[reader], creation_date=format_required_date))
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
