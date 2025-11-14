from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.Customer import CustomerViewSet
from api.views.Account import AccountViewSet
from api.views.Loan import LoanViewSet
from api.views.Appointment import AppointmentViewSet

router = DefaultRouter()

router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
