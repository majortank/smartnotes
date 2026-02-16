from .models import Message


def unread_message_count(request):
    if not request.user.is_authenticated:
        return {"unread_count": 0}
    count = Message.objects.filter(recipient=request.user, is_read=False).count()
    return {"unread_count": count}
