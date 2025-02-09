import time
import logging

logger = logging.getLogger(__name__)

class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Запись времени начала обработки запроса
        start_time = time.time()

        # Обработка запроса
        response = self.get_response(request)

        # Запись времени окончания обработки запроса
        end_time = time.time()
        duration = end_time - start_time

        logger.info(f"Request to {request.path} took {duration:.4f} seconds")

        return response