from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from .permissions import IsAdminOrSelf
from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserLoginResponseSerializer,
)



class UserRegistrationAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя с JWT"""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save()
        # Дополнительная логика при регистрации
        # - отправить email приветствия
        # - создать профиль
        # - начислить бонусы
        return user
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = serializer.instance
        refresh = RefreshToken.for_user(user)

        data = serializer.data
        data.update({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

class UserLoginAPIView(APIView):
    """Аутентификация пользователя и получение JWT токенов"""
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: UserLoginResponseSerializer,
            400: 'Необходимо указать номер телефона и пароль',
            401: 'Неверные учетные данные',
        },
    )
    
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        
        if not phone_number or not password:
            return Response(
                {'error': 'Необходимо указать номер телефона и пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=phone_number, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        else:
            return Response(
                {'error': 'Неверные учетные данные'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class UserLogoutAPIView(APIView):
    """Выход пользователя (добавление refresh токена в черный список)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Добавляем в черный список
            
            return Response({'message': 'Успешный выход из системы'})
        except Exception as e:
            return Response(
                {'error': 'Неверный токен'},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """Получение и обновление профиля пользователя"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserViewSet(ModelViewSet):
    """ViewSet для управления пользователями"""
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSelf]

    def get_queryset(self):
        user = self.request.user
        if IsAdminOrSelf._is_admin(user):
            return User.objects.order_by('id')
        return User.objects.filter(pk=user.pk).order_by('id')
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
