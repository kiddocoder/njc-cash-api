from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.Role import RoleViewSet

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')

urlpatterns = [
    path('', include(router.urls)),
]
