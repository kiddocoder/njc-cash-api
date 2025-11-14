"""
Utility functions for sending WebSocket events from anywhere in the application
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_chat_message(conversation_id, message_data):
    """
    Send a chat message to all participants in a conversation via WebSocket
    
    Args:
        conversation_id: ID of the conversation
        message_data: Serialized message data
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{conversation_id}',
        {
            'type': 'chat_message',
            'message': message_data
        }
    )
    
def send_notification_to_user(user_id, notification_data):
    """
    Send a notification to a specific user via WebSocket
    
    Args:
        user_id: ID of the user to send notification to
        notification_data: Dictionary containing notification details
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'notification',
            'notification': notification_data
        }
    )


def send_unread_count_update(user_id, count):
    """
    Send unread notification count update to a user
    
    Args:
        user_id: ID of the user
        count: Number of unread notifications
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'unread_count',
            'count': count
        }
    )


def send_loan_status_update(user_id, loan_id, status, message=''):
    """
    Send loan status update to a user via WebSocket
    
    Args:
        user_id: ID of the user (customer)
        loan_id: ID of the loan
        status: New loan status
        message: Optional message about the update
    """
    from django.utils import timezone
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'loan_updates_{user_id}',
        {
            'type': 'loan_status_changed',
            'loan_id': loan_id,
            'status': status,
            'message': message,
            'updated_at': timezone.now().isoformat()
        }
    )


def send_loan_approval(user_id, loan_id, amount, message=''):
    """
    Send loan approval notification to a user
    
    Args:
        user_id: ID of the user (customer)
        loan_id: ID of the approved loan
        amount: Loan amount
        message: Optional approval message
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'loan_updates_{user_id}',
        {
            'type': 'loan_approved',
            'loan_id': loan_id,
            'amount': str(amount),
            'message': message
        }
    )


def send_loan_disbursement(user_id, loan_id, amount, account_number=''):
    """
    Send loan disbursement notification to a user
    
    Args:
        user_id: ID of the user (customer)
        loan_id: ID of the disbursed loan
        amount: Disbursed amount
        account_number: Account where funds were sent
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'loan_updates_{user_id}',
        {
            'type': 'loan_disbursed',
            'loan_id': loan_id,
            'amount': str(amount),
            'account_number': account_number
        }
    )


def send_payment_received(user_id, loan_id, payment_id, amount, remaining_balance):
    """
    Send payment received notification to a user
    
    Args:
        user_id: ID of the user (customer)
        loan_id: ID of the loan
        payment_id: ID of the payment
        amount: Payment amount
        remaining_balance: Remaining loan balance after payment
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'loan_updates_{user_id}',
        {
            'type': 'payment_received',
            'loan_id': loan_id,
            'payment_id': payment_id,
            'amount': str(amount),
            'remaining_balance': str(remaining_balance)
        }
    )


def send_payment_due_reminder(user_id, loan_id, due_date, amount):
    """
    Send payment due reminder to a user
    
    Args:
        user_id: ID of the user (customer)
        loan_id: ID of the loan
        due_date: Payment due date
        amount: Amount due
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'loan_updates_{user_id}',
        {
            'type': 'payment_due_reminder',
            'loan_id': loan_id,
            'due_date': due_date.isoformat() if hasattr(due_date, 'isoformat') else str(due_date),
            'amount': str(amount)
        }
    )

def trigger_loan_status_change(loan, status, message=''):
    """
    Trigger loan status change and send notifications
    
    Args:
        loan: Loan instance
        status: New loan status
        message: Optional message about the status change
    """
    from api.models import Notification
    from django.utils import timezone
    
    # Get customer/user from the loan
    user_id = loan.customer.user.id if hasattr(loan.customer, 'user') else loan.customer.id
    
    # Send WebSocket notification
    send_loan_status_update(user_id, loan.id, status, message)
    
    # Create a notification record in the database
    notification_type_map = {
        'APPROVED': 'loan_approved',
        'REJECTED': 'loan_rejected',
        'DISBURSED': 'loan_disbursed',
        'PENDING': 'loan_pending',
        'ACTIVE': 'loan_active',
        'COMPLETED': 'loan_completed',
        'DEFAULTED': 'loan_defaulted',
    }
    
    notification_title_map = {
        'APPROVED': 'Loan Approved',
        'REJECTED': 'Loan Rejected',
        'DISBURSED': 'Loan Disbursed',
        'PENDING': 'Loan Pending Review',
        'ACTIVE': 'Loan Activated',
        'COMPLETED': 'Loan Completed',
        'DEFAULTED': 'Loan Defaulted',
    }
    
    try:
        Notification.objects.create(
            user_id=user_id,
            notification_type=notification_type_map.get(status, 'loan_update'),
            title=notification_title_map.get(status, 'Loan Status Update'),
            message=message or f'Your loan status has been updated to {status}',
            related_loan_id=loan.id,
            is_read=False
        )
        
        # Send unread count update
        from api.models import Notification
        unread_count = Notification.objects.filter(user_id=user_id, is_read=False).count()
        send_unread_count_update(user_id, unread_count)
    except Exception as e:
        # Log error but don't fail the status change
        print(f"Error creating notification: {e}")
