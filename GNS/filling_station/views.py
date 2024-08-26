from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import Balloon, BalloonAmount, BalloonHistory
from .admin import BalloonResources
from .forms import GetBalloonsAmount, BalloonPassportForm
from datetime import datetime, timedelta
from django.http import Http404

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


def balloons(request):
    balloons_list = Balloon.objects.order_by('-id').all()

    paginator = Paginator(balloons_list, 15)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    return render(request, "balloons_table.html", {"page_obj": page_obj})


def balloon_passport(request, nfc_tag):
    # try:
    balloon = Balloon.objects.filter(nfc_tag=nfc_tag).last()
    history = BalloonHistory.objects.filter(balloon=balloon.id).last()

    if request.method == 'POST':
        form = BalloonPassportForm(request.POST)
        if form.is_valid():
            balloon.nfc_tag = form.cleaned_data['nfc_tag']
            balloon.serial_number = form.cleaned_data['serial_number']
            balloon.creation_date = form.cleaned_data['creation_date']
            history.netto = form.cleaned_data['netto']
            history.brutto = form.cleaned_data['brutto']
            history.current_examination_date = form.cleaned_data['current_examination_date']
            history.next_examination_date = form.cleaned_data['next_examination_date']
            balloon.manufacturer = form.cleaned_data['manufacturer']
            balloon.wall_thickness = form.cleaned_data['wall_thickness']
            balloon.save()
            history.save()
            # return redirect('profile_detail', profile_id=profile.id)
    else:
        form = BalloonPassportForm(initial={
            'nfc_tag': balloon.nfc_tag,
            'serial_number': balloon.serial_number,
            'creation_date': balloon.creation_date,
            'size': balloon.size,
            'netto': history.netto,
            'brutto': history.brutto,
            'current_examination_date': history.current_examination_date,
            'next_examination_date': history.next_examination_date,
            'manufacturer': balloon.manufacturer,
            'wall_thickness': balloon.wall_thickness,
        })
    # except:
    #     raise Http404("No Balloon found")

    return render(request, "balloon_passport.html", {'balloon': balloon, 'form': form})


def reader_info(request, reader='1'):
    current_date = datetime.now().date()
    previous_date = current_date - timedelta(days=1)

    if request.method == "POST":
        required_date = request.POST.get("date")
        format_required_date = datetime.strptime(required_date, '%d.%m.%Y')
        dataset = BalloonResources().export(Balloon.objects.order_by('-id').filter(status=STATUS_LIST[reader],
                                                                                   change_date=format_required_date))
        response = HttpResponse(dataset.xls, content_type='xls')
        response[
            'Content-Disposition'] = f'attachment; filename="RFID_1_{datetime.strftime(format_required_date, '%Y.%m.%d')}.xls"'
        return response
    else:
        date_process = GetBalloonsAmount()

    balloons_list = Balloon.objects.order_by('-id').filter(history__status=STATUS_LIST[reader])
    current_quantity_by_sensor = BalloonAmount.objects.filter(reader_id=reader, change_date=current_date)
    previous_quantity_by_sensor = BalloonAmount.objects.filter(reader_id=reader, change_date=previous_date)
    current_quantity_by_reader = len(balloons_list.filter(change_date=current_date))
    previous_quantity_by_reader = len(balloons_list.filter(change_date=previous_date))

    paginator = Paginator(balloons_list, 15)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    current_quantity_by_sensor_item = previous_quantity_by_sensor_item = 0
    for amount in current_quantity_by_sensor:
        current_quantity_by_sensor_item = amount.amount_of_balloons
    for amount in previous_quantity_by_sensor:
        previous_quantity_by_sensor_item = amount.amount_of_balloons

    return render(request, "rfid_tables.html", {
        "page_obj": page_obj,
        'current_quantity_by_reader': current_quantity_by_reader,
        'previous_quantity_by_reader': previous_quantity_by_reader,
        'current_quantity_by_sensor': current_quantity_by_sensor_item,
        'previous_quantity_by_sensor': previous_quantity_by_sensor_item,
        'form': date_process
    })
