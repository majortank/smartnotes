from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notes, Comment
from .forms import NotesForm, CommentForm
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib import messages


class NotesListView(LoginRequiredMixin, ListView):
    model = Notes
    context_object_name = 'notes'
    template_name = 'notes/notes_list.html'
    login_url = '/login'

    def get_queryset(self):
        return self.request.user.notes.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shared_notes'] = Notes.objects.filter(shared_with=self.request.user)
        context['shared_by'] = Notes.objects.filter(user=self.request.user)
        return context
    

class NotesDetailView(DetailView):
    model = Notes
    context_object_name = 'note'
    template_name = 'notes/notes_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(note=self.object)
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.note = self.object
            comment.user = request.user
            comment.save()
            self.send_comment_notification(comment)
            messages.success(request, 'Your comment has been added.')
            return redirect('notes.detail', pk=self.object.pk)
        else:
            context = self.get_context_data()
            context['comment_form'] = form
            return self.render_to_response(context)

    def send_comment_notification(self, comment):
        note_owner = comment.note.user
        if note_owner.email:
            send_mail(
                'New Comment on Your Shared Note',
                f'User {comment.user.username} commented on your note "{comment.note.title}".',
                'noreply@smartnotes.com',
                [note_owner.email],
                fail_silently=True,
            )


class NotesCreateView(LoginRequiredMixin, CreateView):
    model = Notes
    form_class = NotesForm
    success_url = '/smart/notes'
    login_url = '/admin'

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

class NotesUpdateView(UpdateView):
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

class NotesDeleteView(DeleteView):
    model = Notes
    success_url = '/smart/notes'
    template_name = 'notes/notes_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note'] = self.get_object()
        return context
