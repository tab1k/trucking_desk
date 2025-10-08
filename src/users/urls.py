from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'users'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')


urlpatterns = [
    # Auth endpoints
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout'),
    path('profile/', UserProfileAPIView.as_view(), name='profile'),
    
    # Router URLs
    path('', include(router.urls)),

]