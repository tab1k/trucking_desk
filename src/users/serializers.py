# src/users/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для добавления дополнительных данных в JWT токен"""
    username_field = 'phone_number'
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['role'] = user.role
        token['is_subscription_active'] = user.is_subscription_active
        token['email'] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        data.update({
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'role': self.user.role,
                'is_subscription_active': self.user.is_subscription_active,
                'phone_number': self.user.phone_number,
            }
        })
        
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['phone_number', 'email', 'password', 'password_confirm', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        phone_number = validated_data.get('phone_number')
        user = User.objects.create_user(
            username=phone_number,
            **validated_data
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number',
                  'is_subscription_active', 'referral_code', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'referral_code', 'username']


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(help_text='+77000000000')
    password = serializers.CharField(write_only=True, help_text='Пароль пользователя')


class UserLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()

    class Meta:
        ref_name = 'UserLoginResponse'
        swagger_schema_fields = {
            'example': {
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'user': {
                    'id': 1,
                    'username': '+77000000000',
                    'email': 'user@example.com',
                    'role': 'SENDER',
                    'phone_number': '+77000000000',
                    'is_subscription_active': False,
                    'referral_code': 'AB12CD34',
                    'date_joined': '2025-01-01T12:00:00Z'
                }
            }
        }
