from django.contrib.auth.models import AbstractUser
from django.db import models
import os
import uuid
from django_resized import ResizedImageField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core import validators
from users.errors import BIRTH_YEAR_ERROR_MSG


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