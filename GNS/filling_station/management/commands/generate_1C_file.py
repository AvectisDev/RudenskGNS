import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from filling_station.models import FilePath, RailwayBatch, BalloonsUnloadingBatch, BalloonsLoadingBatch, AutoGasBatch


class Command(BaseCommand):
    help = 'Generate 1C file'
    today = timezone.now().strftime('%d.%m.%y')
    day_for_search = timezone.now()
    # day_for_search = datetime(2024, 10, 17)     # для тестирования

    def handle(self, *args, **kwargs):
        filename = f'ГНС{self.today}.txt'
        file_path = FilePath.objects.first()
        path = file_path.path if file_path and file_path.path else None

        content_1 = self.generate_railway_list()
        content_2 = self.generate_loading_auto_gas_list()
        content_3 = self.generate_unloading_auto_gas_list()
        content_4 = self.generate_balloon_loading_list()
        content_5 = self.generate_balloon_unloading_list()

        content = '\n'.join([content_1, content_2, content_3, content_4, content_5])

        if path:
            full_path = os.path.join(path, filename)
            with open(full_path, 'w', encoding='windows-1251') as file:
                file.write(content)
        else:
            # Логика для обмена по API
            pass

    def generate_railway_list(self):
        batch = RailwayBatch.objects.get(begin_date=self.day_for_search)

        lines = ['ГНС-ТТН1']

        if batch:
            import_ttn = batch.import_ttn
            export_ttn = batch.export_ttn
            railway_tanks = batch.railway_tank_list.all()

            lines.append(f'{import_ttn.number};'
                         f'{import_ttn.date.strftime("%d.%m.%y")};'
                         f'{batch.begin_date.strftime("%d.%m.%y")};'
                         f'{import_ttn.shipper};')

            for tank in railway_tanks:
                lines.append(f'{tank.registration_number};'
                             f'{tank.gas_type};'
                             f'{import_ttn.gas_amount};'
                             f'{tank.gas_weight};'
                             f'{tank.departure_date.strftime("%d.%m.%y") if tank.departure_date else 0};'
                             f'{export_ttn.number};')
        return '\n'.join(lines)

    def generate_loading_auto_gas_list(self):
        batches = AutoGasBatch.objects.filter(batch_type='l', begin_date=self.day_for_search)

        lines = ['ГНС-ТТН2']

        if batches:
            for batch in batches:
                ttn = batch.ttn
                lines.append(f'{ttn.number};'
                             f'{ttn.date.strftime("%d.%m.%y")};'
                             f'{ttn.shipper};'
                             f'{batch.weight_gas_amount};'
                             f'{batch.gas_amount};'
                             f'{batch.truck.registration_number};')
        return '\n'.join(lines)

    def generate_unloading_auto_gas_list(self):
        batches = AutoGasBatch.objects.filter(batch_type='u', begin_date=self.day_for_search)

        lines = ['ГНС-ТТН3']

        if batches:
            for batch in batches:
                ttn = batch.ttn
                lines.append(f'{ttn.number};'
                             f'{ttn.date.strftime("%d.%m.%y")};'
                             f'{ttn.shipper};'
                             f'{batch.weight_gas_amount};'
                             f'{batch.gas_amount};'
                             f'{batch.truck.registration_number};')
        return '\n'.join(lines)

    def generate_balloon_loading_list(self):
        batches = BalloonsLoadingBatch.objects.filter(begin_date=self.day_for_search)

        lines = ['ГНС-ТТН4']

        if batches:
            for batch in batches:
                ttn = batch.ttn
                truck = batch.truck
                lines.append(f'{ttn.number};'
                             f'{ttn.date.strftime("%d.%m.%y")};'
                             f'{ttn.shipper};'
                             f'{truck.registration_number};')

                lines.append(f';'
                             f'Баллоны 50 л;'
                             f'{batch.amount_of_rfid + batch.amount_of_50_liters};'
                             f'0;'
                             f'0;')
                lines.append(f';'
                             f'Баллоны 27 л;'
                             f'{batch.amount_of_27_liters};'
                             f'0;'
                             f'0;')
                lines.append(f';'
                             f'Баллоны 12 л;'
                             f'{batch.amount_of_12_liters};'
                             f'0;'
                             f'0;')
                lines.append(f';'
                             f'Баллоны 5 л;'
                             f'{batch.amount_of_5_liters};'
                             f'0;'
                             f'0;')
        return '\n'.join(lines)

    def generate_balloon_unloading_list(self):
        batches = BalloonsUnloadingBatch.objects.filter(begin_date=self.day_for_search)

        lines = ['ГНС-ТТН5']

        if batches:
            for batch in batches:
                ttn = batch.ttn
                truck = batch.truck
                lines.append(f'{ttn.number};'
                             f'{ttn.date.strftime("%d.%m.%y")};'
                             f'{ttn.shipper};'
                             f'{truck.registration_number};')

                balloons = batch.balloon_list.all()
                total_gas_weight = 0
                total_balloon_weight = 0
                if balloons:
                    for balloon in balloons:
                        total_gas_weight += balloon.brutto - balloon.netto
                        total_balloon_weight += balloon.brutto

                lines.append(f'СПБТ;'
                             f'Баллоны 50 л;'
                             f'{batch.amount_of_rfid + batch.amount_of_50_liters};'
                             f'{total_gas_weight};'
                             f'{total_balloon_weight};')
                lines.append(f'СПБТ;'
                             f'Баллоны 27 л;'
                             f'{batch.amount_of_27_liters};'
                             f'0;'
                             f'0;')
                lines.append(f'СПБТ;'
                             f'Баллоны 12 л;'
                             f'{batch.amount_of_12_liters};'
                             f'0;'
                             f'0;')
                lines.append(f'СПБТ;'
                             f'Баллоны 5 л;'
                             f'{batch.amount_of_5_liters};'
                             f'0;'
                             f'0;')
        return '\n'.join(lines)
