from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notes, Profile, ShareGroup, ShareLink, NoteShareLog, Message
from django.contrib.auth.models import User

from .forms import NotesForm, ProfileForm

from django.db.models import Q
from django.views.decorators.http import require_http_methods




class NotesListView(LoginRequiredMixin, ListView):
    model = Notes
    context_object_name = 'notes'
    template_name = 'notes/notes_list.html'
    login_url = '/login'

    # def get_queryset(self):
    #     return Notes.objects.filter(Q(user=self.request.user) | Q(shared_with=self.request.user))
    def get_queryset(self):
        return self.request.user.notes.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shared_notes'] = Notes.objects.filter(
            Q(shared_with=self.request.user) | Q(shared_groups__members=self.request.user)
        ).exclude(user=self.request.user).distinct()
        context['shared_by'] = Notes.objects.filter(user=self.request.user)
        context['public_notes'] = Notes.objects.filter(is_public=True).select_related('user', 'category').prefetch_related('tags')
        context['community_profiles'] = Profile.objects.select_related('user').order_by('user__username')
        context['share_users'] = User.objects.exclude(pk=self.request.user.pk).order_by('username')
        context['share_groups'] = ShareGroup.objects.filter(owner=self.request.user).order_by('name')
        return context


class NoteAccessMixin(LoginRequiredMixin):
    def get_queryset(self):
        user = self.request.user
        return Notes.objects.filter(
            Q(user=user) | Q(shared_with=user) | Q(shared_groups__members=user) | Q(is_public=True)
        ).distinct()

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Notes.DoesNotExist:
            return render(
                request,
                "404.html",
                {
                    "title": "Note not found",
                    "message": "We could not find that note. It may have been removed or shared access ended.",
                },
                status=404,
            )
        return super().dispatch(request, *args, **kwargs)


class NoteOwnerMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Notes.objects.filter(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = Notes.objects.get(pk=kwargs.get("pk"))
        except Notes.DoesNotExist:
            return render(
                request,
                "404.html",
                {
                    "title": "Note not found",
                    "message": "We could not find that note. It may have been removed or shared access ended.",
                },
                status=404,
            )

        if self.object.user_id != request.user.id:
            return render(
                request,
                "403.html",
                {
                    "title": "You do not have access",
                    "message": "This note is private. Only the owner can edit or delete it.",
                },
                status=403,
            )

        return super().dispatch(request, *args, **kwargs)


class NotesDetailView(NoteAccessMixin, DetailView):
    model = Notes
    context_object_name = 'note'
    template_name = 'notes/notes_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = self.get_object()
        if note.user_id == self.request.user.id:
            context['share_users'] = User.objects.exclude(pk=self.request.user.pk).order_by('username')
            context['share_groups'] = ShareGroup.objects.filter(owner=self.request.user).order_by('name')
        return context


class NotesCreateView(LoginRequiredMixin, CreateView):
    model = Notes
    form_class = NotesForm
    success_url = '/smart/notes'
    login_url = '/admin'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        # Assuming `shared_with` is a field in your form
        shared_with_users = form.cleaned_data.get('shared_with')
        if shared_with_users is not None:
            self.object.shared_with.set(shared_with_users)
        tags = form.cleaned_data.get('tags')
        if tags:
            self.object.tags.set(tags)
        return HttpResponseRedirect(self.get_success_url())

class NotesUpdateView(NoteOwnerMixin, UpdateView):
    model = Notes
    form_class = NotesForm
    success_url = '/smart/notes'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        shared_with_users = form.cleaned_data.get('shared_with')
        if shared_with_users is not None:
            self.object.shared_with.set(shared_with_users)
        tags = form.cleaned_data.get('tags')
        if tags:
            self.object.tags.set(tags)
        return HttpResponseRedirect(self.get_success_url())

class NotesDeleteView(NoteOwnerMixin, DeleteView):
    model = Notes
    success_url = '/smart/notes'
    template_name = 'notes/notes_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note'] = self.get_object()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'notes/profile.html'
    success_url = '/smart/notes'

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class CommunityView(LoginRequiredMixin, TemplateView):
    template_name = 'notes/community.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profiles = {
            profile.user_id: profile
            for profile in Profile.objects.select_related('user').all()
        }
        users = User.objects.order_by('username')
        community_users = []
        for user in users:
            profile = profiles.get(user.id)
            community_users.append({
                'id': user.id,
                'username': user.username,
                'bio': profile.bio if profile else '',
                'topics': profile.topics if profile else '',
                'focus_areas': profile.focus_areas if profile else '',
                'is_online': profile.is_online() if profile else False,
            })

        context['community_users'] = community_users
        context['public_notes'] = Notes.objects.filter(is_public=True).select_related('user', 'category').prefetch_related('tags')
        context['shared_notes'] = Notes.objects.filter(
            Q(shared_with=self.request.user) | Q(shared_groups__members=self.request.user)
        ).exclude(user=self.request.user).distinct()
        context['unread_count'] = Message.objects.filter(recipient=self.request.user, is_read=False).count()
        return context


class InboxView(LoginRequiredMixin, ListView):
    model = Message
    context_object_name = 'messages'
    template_name = 'notes/inbox.html'

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user).select_related('sender').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Message.objects.filter(recipient=self.request.user, is_read=False).update(is_read=True)
        return context


def online_users(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    cutoff = timezone.now() - timezone.timedelta(minutes=5)
    profiles = {
        profile.user_id: profile
        for profile in Profile.objects.select_related("user").all()
    }

    data = []
    online_count = 0

    for user in User.objects.order_by("username"):
        profile = profiles.get(user.id)
        last_seen = profile.last_seen if profile else None
        is_online = bool(last_seen and last_seen >= cutoff)
        if is_online:
            online_count += 1

        data.append(
            {
                "id": user.id,
                "username": user.username,
                "bio": profile.bio if profile else "",
                "topics": profile.topics if profile else "",
                "focus_areas": profile.focus_areas if profile else "",
                "last_seen": last_seen.isoformat() if last_seen else None,
                "status": "online" if is_online else "offline",
                "is_online": is_online,
            }
        )

    return JsonResponse(
        {"count": len(data), "online_count": online_count, "users": data}
    )


@require_http_methods(["GET", "POST"])
def share_links(request, note_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    try:
        note = Notes.objects.get(pk=note_id, user=request.user)
    except Notes.DoesNotExist:
        return JsonResponse({"detail": "Not found."}, status=404)

    if request.method == "GET":
        links = note.share_links.order_by("-created_at")
        data = [
            {
                "id": link.id,
                "token": str(link.token),
                "created_at": link.created_at.isoformat(),
                "expires_at": link.expires_at.isoformat() if link.expires_at else None,
                "can_edit": link.can_edit,
                "is_active": link.is_active(),
            }
            for link in links
        ]
        return JsonResponse({"count": len(data), "links": data})

    expires_minutes = request.POST.get("expires_minutes")
    can_edit = request.POST.get("can_edit") == "true"
    expires_at = None
    if expires_minutes:
        try:
            expires_at = timezone.now() + timezone.timedelta(minutes=int(expires_minutes))
        except ValueError:
            return JsonResponse({"detail": "Invalid expires_minutes."}, status=400)

    link = ShareLink.objects.create(
        note=note,
        created_by=request.user,
        expires_at=expires_at,
        can_edit=can_edit,
    )
    NoteShareLog.objects.create(
        note=note,
        actor=request.user,
        share_link=link,
        action="share_link",
    )
    if request.POST.get("redirect") == "true":
        messages.success(request, f"Share link created: {link.token}")
        return redirect(request.META.get("HTTP_REFERER", "/smart/notes"))
    return JsonResponse(
        {
            "id": link.id,
            "token": str(link.token),
            "created_at": link.created_at.isoformat(),
            "expires_at": link.expires_at.isoformat() if link.expires_at else None,
            "can_edit": link.can_edit,
            "is_active": link.is_active(),
        },
        status=201,
    )


@require_http_methods(["POST"])
def revoke_share_link(request, note_id, link_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    try:
        note = Notes.objects.get(pk=note_id, user=request.user)
    except Notes.DoesNotExist:
        return JsonResponse({"detail": "Not found."}, status=404)

    try:
        link = ShareLink.objects.get(pk=link_id, note=note)
    except ShareLink.DoesNotExist:
        return JsonResponse({"detail": "Not found."}, status=404)

    NoteShareLog.objects.create(
        note=note,
        actor=request.user,
        share_link=link,
        action="revoke_link",
    )
    link.delete()
    if request.POST.get("redirect") == "true":
        messages.success(request, "Share link revoked.")
        return redirect(request.META.get("HTTP_REFERER", "/smart/notes"))
    return JsonResponse({"detail": "revoked"})


@require_http_methods(["POST"])
def share_user(request, note_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    try:
        note = Notes.objects.get(pk=note_id, user=request.user)
    except Notes.DoesNotExist:
        return JsonResponse({"detail": "Not found."}, status=404)

    action = request.POST.get("action")
    user_id = request.POST.get("user_id")
    if action not in {"add", "remove"}:
        return JsonResponse({"detail": "Invalid action."}, status=400)
    if not user_id:
        return JsonResponse({"detail": "user_id is required."}, status=400)

    try:
        target = User.objects.get(pk=int(user_id))
    except (User.DoesNotExist, ValueError):
        return JsonResponse({"detail": "User not found."}, status=404)

    if action == "add":
        note.shared_with.add(target)
        NoteShareLog.objects.create(
            note=note,
            actor=request.user,
            target_user=target,
            action="share_user",
        )
        if request.POST.get("redirect") == "true":
            messages.success(request, f"Shared with {target.username}.")
            return redirect(request.META.get("HTTP_REFERER", "/smart/notes"))
        return JsonResponse({"detail": "added"})

    note.shared_with.remove(target)
    NoteShareLog.objects.create(
        note=note,
        actor=request.user,
        target_user=target,
        action="revoke_user",
    )
    if request.POST.get("redirect") == "true":
        messages.success(request, f"Revoked {target.username}.")
        return redirect(request.META.get("HTTP_REFERER", "/smart/notes"))
    return JsonResponse({"detail": "removed"})


@require_http_methods(["POST"])
def share_group(request, note_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    try:
        note = Notes.objects.get(pk=note_id, user=request.user)
    except Notes.DoesNotExist:
        return JsonResponse({"detail": "Not found."}, status=404)

    action = request.POST.get("action")
    group_id = request.POST.get("group_id")
    if action not in {"add", "remove"}:
        return JsonResponse({"detail": "Invalid action."}, status=400)
    if not group_id:
        return JsonResponse({"detail": "group_id is required."}, status=400)

    try:
        group = ShareGroup.objects.get(pk=int(group_id), owner=request.user)
    except (ShareGroup.DoesNotExist, ValueError):
        return JsonResponse({"detail": "Group not found."}, status=404)

    if action == "add":
        note.shared_groups.add(group)
        NoteShareLog.objects.create(
            note=note,
            actor=request.user,
            target_group=group,
            action="share_group",
        )
        if request.POST.get("redirect") == "true":
            messages.success(request, f"Shared with group {group.name}.")
            return redirect(request.META.get("HTTP_REFERER", "/smart/notes"))
        return JsonResponse({"detail": "added"})

    note.shared_groups.remove(group)
    NoteShareLog.objects.create(
        note=note,
        actor=request.user,
        target_group=group,
        action="revoke_group",
    )
    if request.POST.get("redirect") == "true":
        messages.success(request, f"Revoked group {group.name}.")
        return redirect(request.META.get("HTTP_REFERER", "/smart/notes"))
    return JsonResponse({"detail": "removed"})


@require_http_methods(["GET", "POST"])
def share_groups(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    if request.method == "GET":
        groups = ShareGroup.objects.filter(owner=request.user).order_by("name")
        data = [
            {
                "id": group.id,
                "name": group.name,
                "members": list(group.members.values("id", "username")),
                "created_at": group.created_at.isoformat(),
            }
            for group in groups
        ]
        return JsonResponse({"count": len(data), "groups": data})

    name = (request.POST.get("name") or "").strip()
    if not name:
        return JsonResponse({"detail": "Name is required."}, status=400)

    group = ShareGroup.objects.create(name=name, owner=request.user)
    return JsonResponse(
        {
            "id": group.id,
            "name": group.name,
            "members": [],
            "created_at": group.created_at.isoformat(),
        },
        status=201,
    )


@require_http_methods(["POST"])
def share_group_members(request, group_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    try:
        group = ShareGroup.objects.get(pk=group_id, owner=request.user)
    except ShareGroup.DoesNotExist:
        return JsonResponse({"detail": "Not found."}, status=404)

    action = request.POST.get("action")
    user_id = request.POST.get("user_id")
    if action not in {"add", "remove"}:
        return JsonResponse({"detail": "Invalid action."}, status=400)
    if not user_id:
        return JsonResponse({"detail": "user_id is required."}, status=400)

    try:
        member = User.objects.get(pk=int(user_id))
    except (User.DoesNotExist, ValueError):
        return JsonResponse({"detail": "User not found."}, status=404)

    if action == "add":
        group.members.add(member)
        return JsonResponse({"detail": "added"})

    group.members.remove(member)
    return JsonResponse({"detail": "removed"})


@require_http_methods(["POST"])
def send_message(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    recipient_id = request.POST.get("recipient_id")
    body = (request.POST.get("body") or "").strip()
    subject = (request.POST.get("subject") or "").strip()
    intent = request.POST.get("intent")

    if not recipient_id:
        messages.error(request, "Please choose someone to contact.")
        return redirect(request.META.get("HTTP_REFERER", "/smart/community"))
    if not body:
        messages.error(request, "Please write a message before sending.")
        return redirect(request.META.get("HTTP_REFERER", "/smart/community"))

    try:
        recipient = User.objects.get(pk=int(recipient_id))
    except (User.DoesNotExist, ValueError):
        messages.error(request, "That person could not be found.")
        return redirect(request.META.get("HTTP_REFERER", "/smart/community"))

    if recipient.id == request.user.id:
        messages.error(request, "You cannot send a message to yourself.")
        return redirect(request.META.get("HTTP_REFERER", "/smart/community"))

    if intent == "request":
        if subject:
            subject = f"Note request: {subject}"
        else:
            subject = "Note request"

    Message.objects.create(
        sender=request.user,
        recipient=recipient,
        subject=subject,
        body=body,
    )
    messages.success(request, f"Message sent to {recipient.username}.")
    return redirect(request.META.get("HTTP_REFERER", "/smart/community"))
