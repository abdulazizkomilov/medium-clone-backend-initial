from django.utils import translation
from loguru import logger

class CustomLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if language:
            language = language.split(',')[0]
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()
        response = self.get_response(request)
        translation.deactivate()
        return response
    

class CustomLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if language:
            logger.info(f"Accepted languages: {language}")
            language = language.split(',')[0]
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()
            logger.info(f"Language activated: {language}")
        response = self.get_response(request)
        translation.deactivate()
        return response

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = self.get_client_ip(request)
        
        logger.info(f"Request: {request.method} {request.path} | IP: {ip_address}")

        response = self.get_response(request)

        logger.info(f"Response: {response.status_code} {response.reason_phrase} for {request.path} | IP: {ip_address}")

        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip