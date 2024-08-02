from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _

class OTPException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('OTP verification failed.')
    default_code = 'otp_failed'