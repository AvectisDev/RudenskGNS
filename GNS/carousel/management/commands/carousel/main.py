import logging.config
import os
import struct
import time
from dataclasses import dataclass

import django
import serial


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GNS.settings')
django.setup()

from django.core.exceptions import ValidationError

from carousel.services import (
    CarouselPostNotFoundError,
    UnsupportedCarouselRequestError,
    get_carousel_settings_data,
    process_carousel_data_direct,
)
from core.redis_queue import (
    get_reader_balloon_queue_key,
    increment_metric,
    pop_json_from_queue,
)


os.makedirs(
    os.path.join(django.conf.settings.LOGS_DIR, 'carousel'),
    exist_ok=True,
)
logging.config.dictConfig(django.conf.settings.LOGGING)
logger = logging.getLogger('carousel')

CAROUSEL_NUMBER = int(os.getenv('CAROUSEL_NUMBER', '1'))
CAROUSEL_ENV_PREFIX = f'CAROUSEL_{CAROUSEL_NUMBER}'

DEFAULT_CAROUSEL_CONFIG = {
    1: {'port': 'COM3', 'reader': 8},
    2: {'port': 'COM4', 'reader': 9},
    3: {'port': 'COM5', 'reader': 10},
}
default_config = DEFAULT_CAROUSEL_CONFIG.get(
    CAROUSEL_NUMBER,
    DEFAULT_CAROUSEL_CONFIG[1],
)

PORT = os.getenv(
    f'{CAROUSEL_ENV_PREFIX}_COM_PORT',
    default_config['port'],
)
BAUD_RATE = int(os.getenv(
    f'{CAROUSEL_ENV_PREFIX}_BAUD_RATE',
    '9600',
))
RFID_READER_NUMBER = int(os.getenv(
    f'{CAROUSEL_ENV_PREFIX}_RFID_READER',
    str(default_config['reader']),
))
BALLOON_QUEUE_KEY = get_reader_balloon_queue_key(RFID_READER_NUMBER)

REQUEST_CACHE_SECONDS = 2.0


@dataclass(frozen=True)
class CachedRequest:
    expires_at: float
    response_packet: bytes | None


recent_requests: dict[tuple[str, int, int], CachedRequest] = {}


@dataclass(frozen=True)
class PostSettings:
    available: bool
    read_only: bool
    weight_correction: float | None
    min_balloon_weight: float | None
    max_balloon_weight: float | None
    max_passport_weight_diff: float | None


def record_post_error(
    post_number: int | None,
    request_type: str | None,
    error_code: str,
    message: str,
    metric_name: str = 'post_errors',
) -> None:
    logger.error(
        "Карусель=%s пост=%s тип=%s ошибка=%s: %s",
        CAROUSEL_NUMBER,
        post_number,
        request_type,
        error_code,
        message,
    )
    try:
        increment_metric(CAROUSEL_NUMBER, metric_name)
    except Exception as error:
        logger.error(f"Не удалось обновить метрику {metric_name}: {error}")


def get_and_remove_last_balloon(
    post_number: int,
    request_type: str,
) -> tuple[dict | None, bool]:
    """Атомарно извлекает самый старый паспорт из Redis-очереди."""
    try:
        balloon, queue_size = pop_json_from_queue(BALLOON_QUEUE_KEY)
        logger.debug(
            f"Карусель={CAROUSEL_NUMBER} очередь={BALLOON_QUEUE_KEY} "
            f"размер={queue_size}"
        )
        return balloon, True
    except Exception as error:
        record_post_error(
            post_number,
            request_type,
            'queue_read_error',
            str(error),
            metric_name='queue_errors',
        )
        return None, False


def put_carousel_data(data: dict) -> bool:
    """Сохраняет показания напрямую через сервис Django."""
    try:
        logger.info(f"Данные с поста переданы в Django: {data}")
        process_carousel_data_direct(data)
        logger.info("Данные с поста успешно сохранены")
        return True
    except (
        ValidationError,
        CarouselPostNotFoundError,
        UnsupportedCarouselRequestError,
    ) as error:
        record_post_error(
            data.get('post_number'),
            data.get('request_type'),
            'persistence_validation_error',
            str(error),
        )
    except Exception as error:
        record_post_error(
            data.get('post_number'),
            data.get('request_type'),
            'persistence_error',
            str(error),
        )
        logger.exception("Ошибка сохранения данных с поста наполнения")
    return False


def calc_crc(message: bytes) -> int:
    """Вычисляет CRC-16/AUG-CCITT."""
    poly = 0x1021
    reg = 0xFFFF
    message += b'\x00\x00'
    for byte in message:
        mask = 0x80
        while mask > 0:
            reg <<= 1
            if byte & mask:
                reg += 1
            mask >>= 1
            if reg > 0xFFFF:
                reg &= 0xFFFF
                reg ^= poly
    return reg


def validate_frame_crc(frame: bytes) -> tuple[bool, int, int]:
    """Проверяет CRC16/SPI-FUJITSU первых шести байт кадра."""
    if len(frame) != 8:
        return False, 0, 0
    received_crc = int.from_bytes(frame[6:8], byteorder='big')
    calculated_crc = calc_crc(frame[:6])
    return received_crc == calculated_crc, received_crc, calculated_crc


def build_response_packet(
    request_type: int,
    post_number: int,
    full_weight: int,
) -> bytes:
    if request_type == 0x7A:
        response_type = 0x5A
    elif request_type == 0x70:
        response_type = 0x50
    else:
        raise ValueError(
            f'Нельзя сформировать ответ для типа 0x{request_type:02X}'
        )

    payload = struct.pack(
        '>BBBHB',
        response_type,
        post_number,
        0xFF,
        full_weight,
        0xFF,
    )
    return payload + struct.pack('>H', calc_crc(payload))


def check_settings(post_number: int) -> PostSettings:
    """Читает настройки текущей карусели из базы данных."""
    post_settings = get_carousel_settings_data(CAROUSEL_NUMBER)
    if not post_settings:
        return PostSettings(
            available=False,
            read_only=True,
            weight_correction=0.0,
            min_balloon_weight=None,
            max_balloon_weight=None,
            max_passport_weight_diff=None,
        )

    weight_correction = 0.0
    if post_settings.get('use_weight_management'):
        if post_settings.get('use_common_correction'):
            weight_correction = post_settings.get('weight_correction_value')
        else:
            weight_correction = post_settings.get(
                f'post_{post_number}_correction'
            )

    return PostSettings(
        available=True,
        read_only=bool(post_settings.get('read_only')),
        weight_correction=weight_correction,
        min_balloon_weight=post_settings.get('min_balloon_weight'),
        max_balloon_weight=post_settings.get('max_balloon_weight'),
        max_passport_weight_diff=post_settings.get(
            'max_passport_weight_diff'
        ),
    )


def check_balloon_size(weight: int) -> int:
    """Определяет объём баллона по его весу."""
    return 50


def get_cached_request(
    request_type: str,
    post_number: int,
    weight: int,
) -> tuple[bool, bytes | None]:
    """Возвращает сохранённый ответ на повторный запрос контроллера."""
    now = time.monotonic()
    expired_keys = [
        key for key, request in recent_requests.items()
        if request.expires_at <= now
    ]
    for key in expired_keys:
        recent_requests.pop(key, None)

    request_key = (request_type, post_number, weight)
    cached_request = recent_requests.get(request_key)
    if cached_request is None:
        return False, None

    logger.debug(
        f"Повторный запрос {request_key}: используется сохранённый ответ"
    )
    return True, cached_request.response_packet


def cache_request_result(
    request_type: str,
    post_number: int,
    weight: int,
    response_packet: bytes | None,
) -> None:
    request_key = (request_type, post_number, weight)
    recent_requests[request_key] = CachedRequest(
        expires_at=time.monotonic() + REQUEST_CACHE_SECONDS,
        response_packet=response_packet,
    )


def request_processing(
    request_type: str,
    post_number: int,
    weight: int,
) -> tuple[bool, int, dict]:
    """Обрабатывает запрос от поста наполнения."""
    response_required = False
    full_weight = 0
    process_data = {
        'carousel_number': CAROUSEL_NUMBER,
        'request_type': request_type,
        'post_number': post_number,
        'size': check_balloon_size(weight),
    }

    if request_type == '0x7a':
        balloon, queue_available = get_and_remove_last_balloon(
            post_number,
            request_type,
        )

        if balloon is None:
            if queue_available:
                record_post_error(
                    post_number,
                    request_type,
                    'empty_balloon_queue',
                    f'В очереди {BALLOON_QUEUE_KEY} нет паспорта баллона',
                    metric_name='empty_queue',
                )
            process_data.update({
                'is_empty': True,
                'empty_weight': weight / 1000,
            })
            return response_required, full_weight, process_data

        filling_status = bool(balloon.get('filling_status'))
        netto = balloon.get('netto')
        brutto = balloon.get('brutto')

        if not filling_status:
            record_post_error(
                post_number,
                request_type,
                'balloon_not_ready',
                'Паспорт баллона не разрешает наполнение',
                metric_name='passport_errors',
            )
        elif netto is None or brutto is None:
            record_post_error(
                post_number,
                request_type,
                'incomplete_passport',
                f'Неполный паспорт: netto={netto}, brutto={brutto}',
                metric_name='passport_errors',
            )
        else:
            post_settings = check_settings(post_number)
            if not post_settings.available:
                record_post_error(
                    post_number,
                    request_type,
                    'settings_missing',
                    f'Настройки карусели {CAROUSEL_NUMBER} отсутствуют',
                    metric_name='settings_errors',
                )
            elif not post_settings.read_only:
                weight_is_valid = True

                if (
                    post_settings.min_balloon_weight is not None
                    and netto < post_settings.min_balloon_weight
                ) or (
                    post_settings.max_balloon_weight is not None
                    and brutto > post_settings.max_balloon_weight
                ):
                    weight_is_valid = False
                    record_post_error(
                        post_number,
                        request_type,
                        'weight_out_of_range',
                        f'Паспортные веса вне диапазона: '
                        f'netto={netto}, brutto={brutto}',
                        metric_name='weight_rejections',
                    )

                max_passport_diff = (
                    post_settings.max_passport_weight_diff
                )
                if max_passport_diff is None:
                    weight_is_valid = False
                    record_post_error(
                        post_number,
                        request_type,
                        'invalid_settings',
                        'Не задан max_passport_weight_diff',
                        metric_name='settings_errors',
                    )
                elif abs(brutto - netto) > max_passport_diff:
                    weight_is_valid = False
                    record_post_error(
                        post_number,
                        request_type,
                        'passport_weight_diff',
                        f'Разница brutto/netto {abs(brutto - netto)} '
                        f'превышает {max_passport_diff}',
                        metric_name='weight_rejections',
                    )

                if post_settings.weight_correction is None:
                    weight_is_valid = False
                    record_post_error(
                        post_number,
                        request_type,
                        'invalid_post_correction',
                        'Не задан корректор веса для поста',
                        metric_name='settings_errors',
                    )

                if weight_is_valid:
                    response_required = True
                    full_weight = int(
                        (brutto + post_settings.weight_correction) * 1000
                    )
                    logger.debug(
                        f"Полный вес по паспорту: {brutto} кг. "
                        f"Коррекция: {post_settings.weight_correction} кг"
                    )

        process_data.update({
            'is_empty': True,
            'empty_weight': weight / 1000,
            'nfc_tag': balloon.get('nfc_tag'),
            'serial_number': balloon.get('serial_number'),
            'netto': balloon.get('netto'),
            'brutto': balloon.get('brutto'),
            'filling_status': balloon.get('filling_status'),
        })

    elif request_type == '0x70':
        process_data['full_weight'] = weight / 1000
    else:
        record_post_error(
            post_number,
            request_type,
            'unknown_request_type',
            f'Неизвестный тип запроса {request_type}',
        )
        process_data = {}

    return response_required, full_weight, process_data


def serial_exchange() -> None:
    """Обрабатывает восьмибайтовые кадры от постов наполнения."""
    ser = None
    try:
        logger.info(
            f"Запуск карусели {CAROUSEL_NUMBER}: порт={PORT}, "
            f"скорость={BAUD_RATE}, RFID={RFID_READER_NUMBER}"
        )
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        logger.info(f"Соединение установлено на порту {PORT}")

        while True:
            data = ser.read(8)

            if len(data) == 8:
                request_type = data[0]
                post_number = data[1]
                service_byte = data[2]
                weight = (data[3] << 8) | data[4]
                fill_flag = data[5]
                request_type_text = hex(request_type)

                crc_is_valid, received_crc, calculated_crc = (
                    validate_frame_crc(data)
                )
                if not crc_is_valid:
                    record_post_error(
                        post_number,
                        request_type_text,
                        'invalid_crc',
                        f'Кадр={data.hex().upper()}, '
                        f'получен CRC={received_crc:04X}, '
                        f'рассчитан CRC={calculated_crc:04X}',
                        metric_name='crc_errors',
                    )
                    continue

                logger.info(
                    f"Парсинг: тип={request_type_text}, "
                    f"пост={post_number}, служебный байт={service_byte:02X}, "
                    f"масса={weight}, флаг={fill_flag:02X}"
                )

                is_duplicate, cached_response = get_cached_request(
                    request_type_text,
                    post_number,
                    weight,
                )
                if is_duplicate:
                    if cached_response is not None:
                        ser.write(cached_response)
                        logger.debug(
                            "Повторно отправлен ответ на пост: "
                            f"{cached_response.hex().upper()}"
                        )
                    continue

                response_required, full_weight, process_data = (
                    request_processing(
                        request_type_text,
                        post_number,
                        weight,
                    )
                )

                response_packet = None
                if response_required:
                    response_packet = build_response_packet(
                        request_type,
                        post_number,
                        full_weight,
                    )

                cache_request_result(
                    request_type_text,
                    post_number,
                    weight,
                    response_packet,
                )

                if response_packet is not None:
                    ser.write(response_packet)
                    logger.debug(
                        f"Отправлен ответ на пост: "
                        f"{response_packet.hex().upper()}"
                    )

                if process_data:
                    put_carousel_data(process_data)
            elif data:
                record_post_error(
                    None,
                    None,
                    'invalid_frame_length',
                    f'Получено {len(data)} байт: {data.hex().upper()}',
                    metric_name='frame_errors',
                )
    finally:
        if ser:
            ser.close()
            logger.debug("Соединение закрыто")


def main() -> None:
    while True:
        try:
            serial_exchange()
        except serial.SerialException as error:
            logger.error(
                f"Ошибка COM-порта {PORT}: {error}. Перезапуск через 5 секунд"
            )
            time.sleep(5)
        except Exception:
            logger.exception(
                "Ошибка в serial_exchange. Перезапуск через 5 секунд"
            )
            time.sleep(5)


if __name__ == '__main__':
    main()
