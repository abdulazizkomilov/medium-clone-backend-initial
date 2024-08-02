from django.contrib.auth.models import AbstractUser
from django.db import models
import os
import uuid
from django_resized import ResizedImageField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core import validators
from users.errors import BIRTH_YEAR_ERROR_MSG
from django.contrib.postgres.indexes import HashIndex
from django.contrib.auth import get_user_model


def file_upload(instance, filename):
    """ This function is used to upload the user's avatar. """
    ext = filename.split('.')[-1]
    filename = f'{instance.username}.{ext}'
    return os.path.join('users/avatars/', filename)



class CustomUser(AbstractUser):
    """  This model represents a custom user. """
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    avatar = ResizedImageField(size=[300, 300], crop=['top', 'left'], upload_to=file_upload, blank=True)
    birth_year = models.IntegerField(
		        validators=[  # tug'ilgan yil oralig'ini tekshirish uchun birinchi variant
		            validators.MinValueValidator(settings.BIRTH_YEAR_MIN),
		            validators.MaxValueValidator(settings.BIRTH_YEAR_MAX)
		        ],
		        null=True,
		        blank=True
		    )
    
    class Meta:
        db_table = "user"  # database table name
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]  # descending order by date joined
        constraints = [
                    models.CheckConstraint(  # tug'ilgan yil oralig'ini tekshirish uchun uchunchi variant
                        check=models.Q(birth_year__gt=settings.BIRTH_YEAR_MIN) & models.Q(
                            birth_year__lt=settings.BIRTH_YEAR_MAX),
                        name='check_birth_year_range'
                    )
                ]
        indexes = [
                HashIndex(fields=['first_name'], name='%(class)s_first_name_hash_idx'),
                HashIndex(fields=['last_name'], name='%(class)s_last_name_hash_idx'),
                HashIndex(fields=['middle_name'], name='%(class)s_middle_name_hash_idx'),
                models.Index(fields=['username'], name='%(class)s_username_idx'),
            ]

    def clean(self):  # tug'ilgan yil oralig'ini tekshirish uchun ikkinchi variant
        super().clean()
        if self.birth_year and not (settings.BIRTH_YEAR_MIN < self.birth_year < settings.BIRTH_YEAR_MAX):
            raise ValidationError(BIRTH_YEAR_ERROR_MSG)
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """ This method returns the full name of the user"""
        if self.full_name:
            return self.full_name
        else:
            return self.email or self.username
    
    @property
    def full_name(self):
        """ Returns the user's full name. """
        return f"{self.last_name} {self.first_name} {self.middle_name}"
    


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

User = get_user_model()


class Recommendation(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="recommendations"
    )
    more = models.ManyToManyField(
        'articles.Topic', limit_choices_to={'is_active': True}, related_name="more_recommended", blank=True
    )
    less = models.ManyToManyField(
        'articles.Topic', limit_choices_to={'is_active': True}, related_name="less_recommended", blank=True
    )

    class Meta:
        db_table = "recommendation"
        verbose_name = "Recommendation"
        verbose_name_plural = "Recommendations"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user} - {self.more}"
    

class ReadingHistory(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_active': True}, related_name="reading_history"
    )
    article = models.ForeignKey(
        'articles.Article', on_delete=models.CASCADE, related_name="reading_history"
    )

    class Meta:
        db_table = "reading_history"
        verbose_name = "Reading History"
        verbose_name_plural = "Reading Histories"
        ordering = ['-created_at']

    