from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TransactionTestCase

from .management.commands.carousel import main as carousel_main
from .models import Carousel, CarouselSettings
from .services import (
    CarouselPostNotFoundError,
    UnsupportedCarouselRequestError,
    get_carousel_settings_data,
    process_carousel_data,
)


class CarouselRequestProcessingTests(SimpleTestCase):
    def setUp(self):
        carousel_main.recent_requests.clear()

    def test_duplicate_request_reuses_response_from_memory(self):
        found, response = carousel_main.get_cached_request(
            '0x7a', 1, 18000
        )
        self.assertFalse(found)
        self.assertIsNone(response)

        carousel_main.cache_request_result(
            '0x7a', 1, 18000, b'response'
        )
        found, response = carousel_main.get_cached_request(
            '0x7a', 1, 18000
        )
        self.assertTrue(found)
        self.assertEqual(response, b'response')

    def test_crc_matches_protocol_examples(self):
        examples = (
            '7A141036B0000D53',
            '701410ABE0029FC4',
            '5A14FFA410FF7D88',
            '5014FFA410FFFB8A',
        )

        for frame_hex in examples:
            with self.subTest(frame=frame_hex):
                valid, received, calculated = (
                    carousel_main.validate_frame_crc(
                        bytes.fromhex(frame_hex)
                    )
                )
                self.assertTrue(valid)
                self.assertEqual(received, calculated)

    def test_response_packet_matches_protocol_example(self):
        response = carousel_main.build_response_packet(
            request_type=0x7A,
            post_number=20,
            full_weight=42000,
        )
        self.assertEqual(response.hex().upper(), '5A14FFA410FF7D88')

    @patch.object(carousel_main, 'get_and_remove_last_balloon')
    @patch.object(carousel_main, 'check_settings')
    def test_read_only_saves_data_without_response(
        self,
        check_settings,
        get_balloon,
    ):
        get_balloon.return_value = ({
            'nfc_tag': 'test-tag',
            'serial_number': '123',
            'netto': 18.0,
            'brutto': 39.0,
            'filling_status': True,
        }, True)
        check_settings.return_value = carousel_main.PostSettings(
            available=True,
            read_only=True,
            weight_correction=0.0,
            min_balloon_weight=17.0,
            max_balloon_weight=47.0,
            max_passport_weight_diff=22.0,
        )

        response_required, full_weight, data = (
            carousel_main.request_processing('0x7a', 1, 18500)
        )

        self.assertFalse(response_required)
        self.assertEqual(full_weight, 0)
        self.assertEqual(data['nfc_tag'], 'test-tag')
        self.assertEqual(data['empty_weight'], 18.5)

    @patch.object(carousel_main, 'get_and_remove_last_balloon')
    @patch.object(carousel_main, 'check_settings')
    def test_active_mode_returns_corrected_passport_weight(
        self,
        check_settings,
        get_balloon,
    ):
        get_balloon.return_value = ({
            'nfc_tag': 'test-tag',
            'serial_number': '123',
            'netto': 18.0,
            'brutto': 39.0,
            'filling_status': True,
        }, True)
        check_settings.return_value = carousel_main.PostSettings(
            available=True,
            read_only=False,
            weight_correction=0.2,
            min_balloon_weight=17.0,
            max_balloon_weight=47.0,
            max_passport_weight_diff=22.0,
        )

        response_required, full_weight, _ = (
            carousel_main.request_processing('0x7a', 1, 18500)
        )

        self.assertTrue(response_required)
        self.assertEqual(full_weight, 39200)

    @patch.object(carousel_main, 'record_post_error')
    @patch.object(carousel_main, 'get_and_remove_last_balloon')
    @patch.object(carousel_main, 'check_settings')
    def test_missing_settings_fails_safely(
        self,
        check_settings,
        get_balloon,
        record_error,
    ):
        get_balloon.return_value = ({
            'netto': 18.0,
            'brutto': 39.0,
            'filling_status': True,
        }, True)
        check_settings.return_value = carousel_main.PostSettings(
            available=False,
            read_only=True,
            weight_correction=0.0,
            min_balloon_weight=None,
            max_balloon_weight=None,
            max_passport_weight_diff=None,
        )

        response_required, full_weight, _ = (
            carousel_main.request_processing('0x7a', 1, 18500)
        )

        self.assertFalse(response_required)
        self.assertEqual(full_weight, 0)
        record_error.assert_called_once()


class ProcessCarouselDataTests(TransactionTestCase):
    def test_request_0x7a_creates_record_for_selected_carousel(self):
        carousel_post = process_carousel_data({
            'request_type': '0x7a',
            'carousel_number': 2,
            'post_number': 7,
            'is_empty': True,
            'empty_weight': 18.2,
            'nfc_tag': 'test-tag',
            'serial_number': '123',
            'size': 50,
            'netto': 18.0,
            'brutto': 39.0,
            'filling_status': True,
        })

        self.assertEqual(carousel_post.carousel_number, 2)
        self.assertEqual(carousel_post.post_number, 7)
        self.assertEqual(carousel_post.nfc_tag, 'test-tag')

    def test_request_0x70_updates_only_matching_carousel(self):
        other_carousel_post = Carousel.objects.create(
            carousel_number=1,
            post_number=3,
            is_empty=True,
        )
        target_post = Carousel.objects.create(
            carousel_number=2,
            post_number=3,
            is_empty=True,
        )

        updated_post = process_carousel_data({
            'request_type': '0x70',
            'carousel_number': 2,
            'post_number': 3,
            'full_weight': 40.5,
        })

        other_carousel_post.refresh_from_db()
        target_post.refresh_from_db()
        self.assertEqual(updated_post.pk, target_post.pk)
        self.assertTrue(other_carousel_post.is_empty)
        self.assertFalse(target_post.is_empty)
        self.assertEqual(target_post.full_weight, 40.5)

    def test_request_0x70_raises_for_missing_carousel_post(self):
        Carousel.objects.create(
            carousel_number=1,
            post_number=20,
            is_empty=True,
        )

        with self.assertRaises(CarouselPostNotFoundError):
            process_carousel_data({
                'request_type': '0x70',
                'carousel_number': 3,
                'post_number': 20,
                'full_weight': 40.5,
            })

    def test_settings_are_selected_by_carousel_number(self):
        CarouselSettings.objects.create(
            carousel_number=1,
            read_only=True,
            user=None,
        )
        CarouselSettings.objects.create(
            carousel_number=2,
            read_only=False,
            user=None,
        )

        settings_data = get_carousel_settings_data(2)

        self.assertIsNotNone(settings_data)
        self.assertEqual(settings_data['carousel_number'], 2)
        self.assertFalse(settings_data['read_only'])

    def test_missing_request_type_is_invalid(self):
        with self.assertRaises(ValidationError):
            process_carousel_data({'post_number': 1})

    def test_invalid_carousel_number_is_rejected(self):
        with self.assertRaises(ValidationError):
            process_carousel_data({
                'request_type': '0x7a',
                'carousel_number': 4,
                'post_number': 1,
            })

    def test_unknown_request_type_is_invalid(self):
        with self.assertRaises(UnsupportedCarouselRequestError):
            process_carousel_data({
                'request_type': 'unknown',
                'post_number': 1,
            })
