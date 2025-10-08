from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# urls.py
schema_view = get_schema_view(
    openapi.Info(
        title="🚛 Trucking Desk API",  # Эмодзи в заголовке!
        default_version='v1',
        description="""
        ## 🎯 Добро пожаловать в API системы грузоперевозок!
        
        ### Доступные роли:
        - **👤 Отправитель** - создает заказы на перевозку
        - **🚚 Водитель** - принимает и выполняет заказы  
        - **👑 Администратор** - управление системой
        
        ### 🔐 Аутентификация:
        Используйте JWT токены. Получите токен через `/api/v1/auth/login/`
        
        ### 📚 Основные разделы:
        - **Authentication** - регистрация, вход, управление профилем
        - **Cargo** - заказы на перевозку
        - **Subscriptions** - подписки для водителей
        - **Locations** - города и маршруты
        - **Reviews** - отзывы о водителях и отправителях
        
        [📞 Поддержка](mailto:support@trucking.ru) | [📖 Документация](https://docs.trucking.ru)
        """,
        terms_of_service="https://trucking.ru/terms/",
        contact=openapi.Contact(
            name="Support Team",
            email="support@trucking.ru",
            url="https://trucking.ru/contact"
        ),
        license=openapi.License(
            name="Commercial License",
            url="https://trucking.ru/license"
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)