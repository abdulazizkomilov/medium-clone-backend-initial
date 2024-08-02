from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from users.errors import BIRTH_YEAR_ERROR_MSG


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):   # user uchun [serializer]() klasi
    first_name = serializers.CharField(required=True, min_length=1)
    last_name = serializers.CharField(required=True, min_length=1)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'middle_name', 'email', 'avatar', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):                # user create qilish uchun method
        user = User(
            email=validated_data.get('email', ''),
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            middle_name=validated_data.get('middle_name', '')
        )
        user.set_password(validated_data['password'])
        user.avatar = validated_data.get('avatar', '')
        user.save()
        return user



class LoginSerializer(serializers.Serializer):         # user login uchun [serializer]() klasi
    username = serializers.CharField() 
    password = serializers.CharField(write_only=True)

    def validate(self, data):                         # kelgan datani yaroqli ekanligini tekshirish uchun
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise serializers.ValidationError('Kirish maʼlumotlari notoʻgʻri')
        else:
            raise serializers.ValidationError('Foydalanuvchi nomi va parol ham talab qilinadi')

        data['user'] = user
        return data
        
        
 
class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()



class ValidationErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return instance
        return super().to_representation(instance)


class UserUpdateSerializer(serializers.ModelSerializer):		
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'email', 'avatar', 'birth_year']  # birth_year yangi qo'shildi
 
    def validate_birth_year(self, value):    # tug'ilgan yil oralig'ini tekshirish uchun to'rtinchi variant
        if not (settings.BIRTH_YEAR_MIN < value < settings.BIRTH_YEAR_MAX):
            raise serializers.ValidationError(BIRTH_YEAR_ERROR_MSG)
        return value

    def validate(self, data):                # tug'ilgan yil oralig'ini tekshirish uchun beshinchi variant
        birth_year = data.get('birth_year')
        if birth_year is not None:
            if not (settings.BIRTH_YEAR_MIN < birth_year < settings.BIRTH_YEAR_MAX):
                raise serializers.ValidationError({"birth_year": BIRTH_YEAR_ERROR_MSG})
        return data