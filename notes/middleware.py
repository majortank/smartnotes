from datetime import timedelta
from django.utils import timezone

from .models import Profile


class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            now = timezone.now()
            if not profile.last_seen or now - profile.last_seen > timedelta(minutes=1):
                Profile.objects.filter(pk=profile.pk).update(last_seen=now)
        return response
