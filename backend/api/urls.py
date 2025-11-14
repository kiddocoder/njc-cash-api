from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.Customer import CustomerViewSet
from .views.Account import AccountViewSet
from .views.Loan import LoanViewSet
from .views.Appointment import AppointmentViewSet
from .views.Transaction import TransactionViewSet
from .views.Repayment import RepaymentViewSet
from .views.PaymentMethod import PaymentMethodViewSet
from .views.Payment import PaymentViewSet
from .views.Notification import NotificationViewSet
from .views.NotificationPreference import NotificationPreferenceViewSet
from .views.UserSession import UserSessionViewSet
from .views.Blacklist import (
    BlacklistViewSet, CreditBureauCheckViewSet,
    DocumentVerificationViewSet, AuditLogViewSet, BiometricDataViewSet
)
from .views.EwalletPayment import EwalletPaymentViewSet
from .views.Dashboard import DashboardViewSet

router = DefaultRouter()

router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'repayments', RepaymentViewSet, basename='repayment')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notification-preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'user-sessions', UserSessionViewSet, basename='user-session')
router.register(r'blacklist', BlacklistViewSet, basename='blacklist')
router.register(r'credit-bureau-checks', CreditBureauCheckViewSet, basename='credit-bureau-check')
router.register(r'document-verifications', DocumentVerificationViewSet, basename='document-verification')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'biometric-data', BiometricDataViewSet, basename='biometric-data')
router.register(r'ewallet-payments', EwalletPaymentViewSet, basename='ewallet-payment')

urlpatterns = [
    path('', include(router.urls)),
]
