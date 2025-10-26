from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.Customer import CustomerViewSet
from api.views.Account import AccountViewSet

router = DefaultRouter()

router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'customers', CustomerViewSet, basename='customer')

urlpatterns = [
    path('', include(router.urls)),
]
