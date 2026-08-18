import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, ChatMessage
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room_slug = data['room']


        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'room': room_slug,
            }
        )


        await self.save_message(username, room_slug, message)

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        room = event['room']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'room': room,
        }))

    @sync_to_async
    def save_message(self, username, room_slug, message):
        try:
            user = User.objects.get(username=username)
            room = ChatRoom.objects.get(slug=room_slug)
            ChatMessage.objects.create(
                user=user,
                room=room,
                message_content=message
            )
        except User.DoesNotExist:
            print(f"User '{username}' not found")
        except ChatRoom.DoesNotExist:
            print(f"Room '{room_slug}' not found")
        except Exception as e:
            print(f"Error saving message: {e}")