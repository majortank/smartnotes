from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notes, Profile

from .forms import NotesForm

from django.db.models import Q




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
        return context


class NoteAccessMixin(LoginRequiredMixin):
    def get_queryset(self):
        user = self.request.user
        return Notes.objects.filter(
            Q(user=user) | Q(shared_with=user) | Q(shared_groups__members=user)
        ).distinct()


class NoteOwnerMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Notes.objects.filter(user=self.request.user)


class NotesDetailView(NoteAccessMixin, DetailView):
    model = Notes
    context_object_name = 'note'
    template_name = 'notes/notes_detail.html'


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


def online_users(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)

    cutoff = timezone.now() - timezone.timedelta(minutes=5)
    profiles = (
        Profile.objects.select_related("user")
        .filter(last_seen__gte=cutoff)
        .order_by("user__username")
    )

    data = [
        {
            "id": profile.user.id,
            "username": profile.user.username,
            "bio": profile.bio,
            "topics": profile.topics,
            "focus_areas": profile.focus_areas,
            "last_seen": profile.last_seen.isoformat() if profile.last_seen else None,
        }
        for profile in profiles
    ]

    return JsonResponse({"count": len(data), "users": data})
