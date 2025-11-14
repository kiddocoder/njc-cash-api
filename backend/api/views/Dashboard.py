from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncMonth, TruncDay
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

from ..models.Customer import Customer
from ..models.Loan import Loan
from ..models.Account import Account
from ..models.Appointment import Appointment

from ..serializers.Customer import CustomerSerializer
from ..serializers.Loan import LoanSerializer
from ..serializers.Account import AccountSerializer
from ..serializers.Appointment import AppointmentSerializer


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard statistics and analytics
    """
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get overall dashboard statistics
        """
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Budget calculation
        budget = Decimal('1240000.00')  # This could be from settings
        
        # Today's stats
        today_loan_requests = Loan.objects.filter(created_at__date=today).count()
        today_approvals = Loan.objects.filter(
            status='APPROVED',
            updated_at__date=today
        ).count()
        today_declines = Loan.objects.filter(
            status='REJECTED',
            updated_at__date=today
        ).count()
        
        # Total loans
        total_loans_amount = Loan.objects.filter(
            status__in=['APPROVED', 'DISBURSED']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        total_loans_count = Loan.objects.count()
        
        # Remaining loans (active loans)
        remaining_loans_amount = Loan.objects.filter(
            status='DISBURSED'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Last week stats for comparison
        last_week_total = Loan.objects.filter(
            created_at__date__gte=week_ago,
            created_at__date__lt=today
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate percentage change
        if last_week_total > 0:
            percentage_change = float((total_loans_amount - last_week_total) / last_week_total * 100)
        else:
            percentage_change = 10.01
        
        return Response({
            'budget': str(budget),
            'today_loan_requests': today_loan_requests,
            'today_approvals': today_approvals,
            'today_declines': today_declines,
            'total_loans_amount': str(total_loans_amount),
            'total_loans_count': total_loans_count,
            'remaining_loans_amount': str(remaining_loans_amount),
            'percentage_change': round(percentage_change, 2)
        })
    
    @action(detail=False, methods=['get'])
    def loan_disbursement(self, request):
        """
        Get loan disbursement data by month for charts
        """
        # Get loans from the last 12 months
        twelve_months_ago = timezone.now() - timedelta(days=365)
        
        loans_by_month = Loan.objects.filter(
            created_at__gte=twelve_months_ago,
            status__in=['APPROVED', 'DISBURSED']
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        data = []
        for item in loans_by_month:
            data.append({
                'month': item['month'].strftime('%b'),
                'amount': str(item['total_amount']),
                'count': item['count']
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def loan_status_breakdown(self, request):
        """
        Get loan status breakdown for pie chart
        """
        total_count = Loan.objects.count()
        
        if total_count == 0:
            return Response({
                'approved': 0,
                'pending': 0,
                'declined': 0
            })
        
        approved_count = Loan.objects.filter(status='APPROVED').count()
        pending_count = Loan.objects.filter(status='PENDING').count()
        declined_count = Loan.objects.filter(status='REJECTED').count()
        
        return Response({
            'approved': round((approved_count / total_count) * 100, 1),
            'pending': round((pending_count / total_count) * 100, 1),
            'declined': round((declined_count / total_count) * 100, 1),
            'approved_count': approved_count,
            'pending_count': pending_count,
            'declined_count': declined_count,
            'total_count': total_count
        })
    
    @action(detail=False, methods=['get'])
    def repayments_performance(self, request):
        """
        Get repayments performance data by month
        Mock data for now - would need a Repayment model in production
        """
        import random
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
        data = []
        
        for month in months:
            data.append({
                'month': month,
                'on_time': random.randint(3, 11),
                'late': random.randint(1, 4),
                'missed': random.randint(0, 2)
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def approval_rate(self, request):
        """
        Get today's approval rate by hour
        """
        today = timezone.now().date()
        
        # Get hourly approvals for today
        hourly_data = []
        for hour in range(8, 16):  # 8 AM to 3 PM
            hour_start = timezone.make_aware(datetime.combine(today, datetime.min.time().replace(hour=hour)))
            hour_end = hour_start + timedelta(hours=1)
            
            approvals = Loan.objects.filter(
                status='APPROVED',
                updated_at__gte=hour_start,
                updated_at__lt=hour_end
            ).count()
            
            hourly_data.append({
                'time': f"{hour:02d}:00",
                'approvals': approvals
            })
        
        return Response(hourly_data)
    
    @action(detail=False, methods=['get'])
    def recent_notifications(self, request):
        """
        Get recent notifications
        """
        # Get recent loan requests and applications
        recent_loans = Loan.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=1)
        ).order_by('-created_at')[:10]
        
        notifications = []
        for loan in recent_loans:
            notifications.append({
                'id': loan.id,
                'type': 'NEW_LOAN_REQUEST' if loan.status == 'PENDING' else 'LOAN_STATUS_UPDATE',
                'title': 'New Loan Request' if loan.status == 'PENDING' else 'Loan Status Updated',
                'message': f"New loan request from {loan.borrower.first_name} {loan.borrower.last_name} (R {loan.amount}). Awaiting review.",
                'time': loan.created_at.strftime('%H:%M'),
                'customer_name': f"{loan.borrower.first_name} {loan.borrower.last_name}",
                'amount': str(loan.amount),
                'created_at': loan.created_at.isoformat()
            })
        
        return Response(notifications)
