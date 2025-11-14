import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from chat.models.ChatMessage import ChatMessage
from chat.models.Conversation import Conversation
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat messaging
    Supports sending/receiving messages, typing indicators, and read receipts
    """
    
    async def connect(self):
        # Get conversation ID from URL route
        self.conversation_id = self.scope['url_route']['kwargs'].get('conversation_id')
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
            
        # Create conversation room group name
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send user joined notification
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )
            
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            await self.handle_chat_message(data)
        elif message_type == 'typing':
            await self.handle_typing_indicator(data)
        elif message_type == 'read_receipt':
            await self.handle_read_receipt(data)
        elif message_type == 'edit_message':
            await self.handle_edit_message(data)
        elif message_type == 'delete_message':
            await self.handle_delete_message(data)

    async def handle_chat_message(self, data):
        """Handle new chat message"""
        text = data.get('text', '')
        attachments = data.get('attachments', [])
        reply_to_id = data.get('reply_to_message_id')
        message_type = data.get('message_type', 'TEXT')
        
        # Save message to database
        message = await self.create_message(
            text=text,
            attachments=attachments,
            reply_to_id=reply_to_id,
            message_type=message_type
        )
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'text': message.text,
                    'sender_id': self.user.id,
                    'sender_name': f"{self.user.first_name} {self.user.last_name}",
                    'message_type': message.type,
                    'attachments': message.attachments,
                    'reply_to_message_id': message.reply_to_message_id,
                    'created_at': message.created_at.isoformat(),
                    'delivery_status': message.delivery_status,
                }
            }
        )

    async def handle_typing_indicator(self, data):
        """Handle typing indicator"""
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing,
            }
        )

    async def handle_read_receipt(self, data):
        """Handle read receipt for messages"""
        message_id = data.get('message_id')
        
        if message_id:
            await self.mark_message_read(message_id)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'user_id': self.user.id,
                    'read_at': timezone.now().isoformat(),
                }
            )

    async def handle_edit_message(self, data):
        """Handle message editing"""
        message_id = data.get('message_id')
        new_text = data.get('text', '')
        
        if message_id:
            await self.edit_message(message_id, new_text)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_edited',
                    'message_id': message_id,
                    'text': new_text,
                    'edited_at': timezone.now().isoformat(),
                }
            )

    async def handle_delete_message(self, data):
        """Handle message deletion"""
        message_id = data.get('message_id')
        
        if message_id:
            await self.delete_message(message_id)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id,
                }
            )

    # Event handlers for group messages
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))

    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket"""
        # Don't send typing indicator back to the user who is typing
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    async def read_receipt(self, event):
        """Send read receipt to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'read_at': event['read_at'],
        }))

    async def message_edited(self, event):
        """Send message edit notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'message_id': event['message_id'],
            'text': event['text'],
            'edited_at': event['edited_at'],
        }))

    async def message_deleted(self, event):
        """Send message delete notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
        }))

    async def user_joined(self, event):
        """Send user joined notification to WebSocket"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
            }))

    async def user_left(self, event):
        """Send user left notification to WebSocket"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'username': event['username'],
            }))

    # Database operations
    @database_sync_to_async
    def create_message(self, text, attachments, reply_to_id, message_type):
        """Create a new chat message in the database"""
        conversation = Conversation.objects.get(id=self.conversation_id)
        
        reply_to_message = None
        if reply_to_id:
            try:
                reply_to_message = ChatMessage.objects.get(id=reply_to_id)
            except ChatMessage.DoesNotExist:
                pass
        
        message = ChatMessage.objects.create(
            conversation=conversation,
            sender=self.user,
            text=text,
            type=message_type,
            attachments=attachments,
            reply_to_message=reply_to_message,
        )
        
        # Update conversation's last message
        conversation.last_message = message
        conversation.save()
        
        return message

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """Mark a message as read"""
        try:
            message = ChatMessage.objects.get(id=message_id)
            read_receipts = message.read_receipts or []
            
            # Add read receipt if not already present
            if not any(r.get('user_id') == self.user.id for r in read_receipts):
                read_receipts.append({
                    'user_id': self.user.id,
                    'read_at': timezone.now().isoformat(),
                })
                message.read_receipts = read_receipts
                message.delivery_status = 'READ'
                message.save()
        except ChatMessage.DoesNotExist:
            pass

    @database_sync_to_async
    def edit_message(self, message_id, new_text):
        """Edit an existing message"""
        try:
            message = ChatMessage.objects.get(id=message_id, sender=self.user)
            message.text = new_text
            message.edited = True
            message.edited_at = timezone.now()
            message.save()
        except ChatMessage.DoesNotExist:
            pass

    @database_sync_to_async
    def delete_message(self, message_id):
        """Soft delete a message"""
        try:
            message = ChatMessage.objects.get(id=message_id, sender=self.user)
            message.deleted = True
            message.save()
        except ChatMessage.DoesNotExist:
            pass
