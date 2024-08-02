import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import redis
from decouple import config
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from users.enums import TokenType

# redis uchun malumotlarni olamiz
REDIS_HOST = config("REDIS_HOST", None)
REDIS_PORT = config("REDIS_PORT", None)
REDIS_DB = config("REDIS_DB", None)
User = get_user_model()

class TokenService:
    @classmethod
    def get_redis_client(cls) -> redis.Redis:
        return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    @classmethod
    def get_valid_tokens(cls, user_id: int, token_type: TokenType) -> set:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:{token_type}"
        valid_tokens = redis_client.smembers(token_key)
        return valid_tokens

    @classmethod
    def add_token_to_redis(
            cls,
            user_id: int,
            token: str,
            token_type: TokenType,
            expire_time: datetime.timedelta,
    ) -> None:
        redis_client = cls.get_redis_client()

        token_key = f"user:{user_id}:{token_type}"

        valid_tokens = cls.get_valid_tokens(user_id, token_type)
        if valid_tokens:
            cls.delete_tokens(user_id, token_type)
        redis_client.sadd(token_key, token)
        redis_client.expire(token_key, expire_time)

    @classmethod
    def delete_tokens(cls, user_id: int, token_type: TokenType) -> None:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:{token_type}"
        valid_tokens = redis_client.smembers(token_key)
        if valid_tokens is not None:
            redis_client.delete(token_key)

class UserService:

    @classmethod
    def create_tokens(
            cls,
            user: User,
            access: str = None,
            refresh: str = None,
            is_force_add_to_redis: bool = False
    ) -> dict[str, str]:
        if not access or not refresh:
            refresh = RefreshToken.for_user(user)
            access = str(getattr(refresh, "access_token"))
            refresh = str(refresh)
        valid_access_tokens = TokenService.get_valid_tokens(
            user_id=user.id, token_type=TokenType.ACCESS
        )
        if valid_access_tokens or is_force_add_to_redis:
            TokenService.add_token_to_redis(
                user.id,
                access,
                TokenType.ACCESS,
                settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME"),
            )

        valid_refresh_tokens = TokenService.get_valid_tokens(
            user_id=user.id, token_type=TokenType.REFRESH
        )
        if valid_refresh_tokens or is_force_add_to_redis:
            TokenService.add_token_to_redis(
                user.id,
                refresh,
                TokenType.REFRESH,
                settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME"),
            )
        return {"access": access, "refresh": refresh}
    

class SendEmailService:
    @staticmethod
    def send_email(email, otp_code):
        subject = 'Welcome to Our Service!'
        message = render_to_string('emails/email_template.html', {
            'email': email,
            'otp_code': otp_code
        })

        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email]
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)