from rest_framework.routers import DefaultRouter

from .views import CargoRequestViewSet

app_name = 'cargo'

router = DefaultRouter()
router.register(r'requests', CargoRequestViewSet, basename='cargo-request')

urlpatterns = router.urls
