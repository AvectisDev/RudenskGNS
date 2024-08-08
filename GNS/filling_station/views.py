from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import Balloon, BalloonAmount
from .admin import BalloonResources
from .forms import Process, GetBalloonsAmount
from datetime import datetime, timedelta


STATUS_LIST = {
    '1': 'Регистрация пустого баллона на складе (из кассеты)',
    '2': 'Погрузка полного баллона в кассету',
    '3': 'Погрузка полного баллона на трал 1',
    '4': 'Погрузка полного баллона на трал 2',
    '5': 'Регистрация полного баллона на складе',
    '6': 'Регистрация пустого баллона на складе (рампа)',
    '7': 'Регистрация пустого баллона на складе (цех)',
    '8': 'Наполнение баллона сжиженным газом',
}


def index(request):
    balloons = Balloon.objects.all()
    return render(request, "home.html", {"balloons": balloons})


def reader_info(request, reader='1'):
    current_date = datetime.now().date()
    previous_date = current_date - timedelta(days=1)

    balloons = Balloon.objects.order_by('-id').filter(status=STATUS_LIST[reader])
    current_quantity_by_sensor = BalloonAmount.objects.filter(reader_id=reader, change_date=current_date)
    previous_quantity_by_sensor = BalloonAmount.objects.filter(reader_id=reader, change_date=previous_date)

    print(current_quantity_by_sensor,previous_quantity_by_sensor,sep="-----")

    paginator = Paginator(balloons, 15)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    date_process = GetBalloonsAmount()
    if request.method == "POST":
        required_date = request.POST.get("date")
        format_required_date = datetime.strptime(required_date, '%d.%m.%Y')

        dataset = BalloonResources().export(Balloon.objects.order_by('-id').filter(state=STATUS_LIST[reader],
                                                                                   change_date=format_required_date))
        response = HttpResponse(dataset.xls, content_type='xls')
        response[
            'Content-Disposition'] = f'attachment; filename="RFID_1_{datetime.strftime(format_required_date, '%Y.%m.%d')}.xls"'
        return response
    else:
        date_process = GetBalloonsAmount()
        format_required_date = datetime.today()

    last_date_amount = len(balloons.filter(change_date=datetime.today()))
    previous_date_amount = len(balloons.filter(change_date=datetime.today() - timedelta(days=1)))
    required_date_amount = len(balloons.filter(change_date=format_required_date))

    view_required_data = datetime.strftime(format_required_date, '%d.%m.%Y')

    current_quantity_by_sensor_item = previous_quantity_by_sensor_item = 0
    for amount in current_quantity_by_sensor:
        current_quantity_by_sensor_item = amount.amount_of_balloons
    for amount in previous_quantity_by_sensor:
        previous_quantity_by_sensor_item = amount.amount_of_balloons
    

    return render(request, "balloons_table.html", {
        "page_obj": page_obj,
        'balloons_amount': last_date_amount,
        'previous_balloons_amount': previous_date_amount,
        'required_date_amount': required_date_amount,
        'format_required_date': view_required_data,
        'current_quantity_by_sensor': current_quantity_by_sensor_item,
        'previous_quantity_by_sensor': previous_quantity_by_sensor_item,
        'form': date_process})
