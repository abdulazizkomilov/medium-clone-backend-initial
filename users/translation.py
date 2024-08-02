from modeltranslation.translator import TranslationOptions, register
from .models import CustomUser

@register(CustomUser)
class CustomUserTranslationOptions(TranslationOptions):
    fields = ('first_name', 'last_name', 'middle_name',)

# translator.register(CustomUser, CustomUserTranslationOptions) register qilish uchun 2-usul**
