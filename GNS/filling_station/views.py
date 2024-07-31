from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import Ballon
from .admin import BallonResources
from .forms import Process, GetBallonsAmount
from datetime import datetime, date, time, timedelta
import locale


# locale.setlocale(locale.LC_TIME, "ru-RU")

def index(request):
    ballons = Ballon.objects.all()
    return render(request, "home.html", {"ballons": ballons})


def client(request):
    ballons = Ballon.objects.all()
    return render(request, "home.html", {"ballons": ballons})


def reader_info(request, reader = '1'):

    if reader == '1':
        status = 'Регистрация пустого баллона на складе (цех)'
    elif reader == '2':
        status = 'Наполнение баллона сжиженным газом'
    elif reader == '3':
        status = 'Регистрация пустого баллона на складе (рампа)'
    elif reader == '4':
        status = 'Регистрация полного баллона на складе'
    elif reader == '5':
        status = 'Погрузка полного баллона на тралл 2'
    elif reader == '6':
        status = 'Погрузка полного баллона на тралл 1'
    elif reader == '7':
        status = 'Погрузка полного баллона в кассету'
    elif reader == '8':
        status = 'Регистрация пустого баллона на складе (из кассеты)'

    ballons = Ballon.objects.order_by('-id').filter(state = status)
    paginator = Paginator(ballons, 15)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    date_process = GetBallonsAmount()
    if request.method == "POST":
        required_date = request.POST.get("date")
        format_required_date = datetime.strptime(required_date, '%d.%m.%Y')

        dataset = BallonResources().export(Ballon.objects.filter(state = status, creation_date = format_required_date))
        response = HttpResponse(dataset.xls, content_type='xls')
        response['Content-Disposition'] = f'attachment; filename="RFID_1_{datetime.strftime(format_required_date, '%Y.%m.%d')}.xls"'
        return response
    else:
        date_process = GetBallonsAmount()
        format_required_date = datetime.today()

    last_date_amount = len(ballons.filter(creation_date = datetime.today()))
    previous_date_amount = len(ballons.filter(creation_date = datetime.today() - timedelta(days=1)))     
    required_date_amount = len(ballons.filter(creation_date = format_required_date))

    view_required_data = datetime.strftime(format_required_date, '%d.%m.%Y')

    return render(request, "ballons_table.html", {
        "page_obj": page_obj, 
        'ballons_amount': last_date_amount, 
        'previous_ballons_amount': previous_date_amount,
        'required_date_amount': required_date_amount,
        'format_required_date': view_required_data,
        'form': date_process})
