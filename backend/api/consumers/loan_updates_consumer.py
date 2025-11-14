import json
from channels.generic.websocket import AsyncWebsocketConsumer


class LoanUpdatesConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time loan updates
    Notifies users about loan status changes, approvals, payments, etc.
    """
    
    async def connect(self):
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Create user-specific loan updates group
        self.loan_updates_group_name = f'loan_updates_{self.user.id}'
        
        # Join loan updates group
        await self.channel_layer.group_add(
            self.loan_updates_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'loan_updates_group_name'):
            await self.channel_layer.group_discard(
                self.loan_updates_group_name,
                self.channel_name
            )

    # Event handlers
    async def loan_status_changed(self, event):
        """Send loan status change to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'loan_status_changed',
            'loan_id': event['loan_id'],
            'status': event['status'],
            'message': event.get('message', ''),
            'updated_at': event['updated_at'],
        }))

    async def loan_approved(self, event):
        """Send loan approval notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'loan_approved',
            'loan_id': event['loan_id'],
            'amount': event['amount'],
            'message': event.get('message', ''),
        }))

    async def loan_disbursed(self, event):
        """Send loan disbursement notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'loan_disbursed',
            'loan_id': event['loan_id'],
            'amount': event['amount'],
            'account_number': event.get('account_number', ''),
        }))

    async def payment_received(self, event):
        """Send payment received notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'payment_received',
            'loan_id': event['loan_id'],
            'payment_id': event['payment_id'],
            'amount': event['amount'],
            'remaining_balance': event['remaining_balance'],
        }))

    async def payment_due_reminder(self, event):
        """Send payment due reminder to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'payment_due_reminder',
            'loan_id': event['loan_id'],
            'due_date': event['due_date'],
            'amount': event['amount'],
        }))
