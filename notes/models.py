from django.db import models
from django.utils import timezone
import re
import uuid
import markdown
import bleach
from django.contrib.auth.models import User

ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {
    "p",
    "br",
    "pre",
    "code",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "blockquote",
    "ul",
    "ol",
    "li",
    "strong",
    "em",
    "u",
    "s",
    "a",
    "span",
    "div",
}

ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "a": ["href", "title", "rel", "target"],
    "span": ["class"],
    "div": ["class"],
    "code": ["class"],
    "pre": ["class"],
}


def sanitize_html(html):
    cleaned = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    return bleach.linkify(cleaned)

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    topics = models.TextField(blank=True)
    focus_areas = models.TextField(blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    def is_online(self):
        if not self.last_seen:
            return False
        return timezone.now() - self.last_seen <= timezone.timedelta(minutes=5)


class ShareGroup(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_share_groups")
    members = models.ManyToManyField(User, related_name="share_groups", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Notes(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    shared_with = models.ManyToManyField(User, related_name='shared_notes', blank=True)
    shared_groups = models.ManyToManyField(ShareGroup, related_name="notes", blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    tags = models.ManyToManyField(Tag, related_name='notes', blank=True)

    def __str__(self):
        return self.title

    @property
    def rendered_text(self):
        if not self.text:
            return ""
        if re.search(r"</?[a-z][\s\S]*>", self.text):
            html = self.text
        else:
            html = markdown.markdown(self.text, extensions=["fenced_code", "tables", "sane_lists"])
        return sanitize_html(html)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'


class ShareLink(models.Model):
    note = models.ForeignKey(Notes, on_delete=models.CASCADE, related_name="share_links")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_share_links")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    can_edit = models.BooleanField(default=False)

    def is_active(self):
        if self.expires_at is None:
            return True
        return self.expires_at > timezone.now()


class NoteShareLog(models.Model):
    ACTION_CHOICES = [
        ("share_user", "Share to user"),
        ("share_group", "Share to group"),
        ("share_link", "Share by link"),
        ("revoke_user", "Revoke user share"),
        ("revoke_group", "Revoke group share"),
        ("revoke_link", "Revoke link"),
        ("view_link", "Viewed via link"),
    ]

    note = models.ForeignKey(Notes, on_delete=models.CASCADE, related_name="share_logs")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="share_actions")
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="share_received")
    target_group = models.ForeignKey(ShareGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="share_logs")
    share_link = models.ForeignKey(ShareLink, on_delete=models.SET_NULL, null=True, blank=True, related_name="share_logs")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
