from django.shortcuts import render
from .models import ChatRoom,ChatMessage
# Create your views here.
def index(request):
    chat_rooms = ChatRoom.objects.all()
    return render(request, 'chatapp/index.html', {'chat_rooms': chat_rooms})

def chatroom(request,slug):
    chatroom = ChatRoom.objects.get(slug=slug)
    messages = ChatMessage.objects.filter(room=chatroom).order_by('-date')[:30]
    messages = reversed(messages)
    return render(request, 'chatapp/room.html', {'chatroom': chatroom,'messages': messages})