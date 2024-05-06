from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notes

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
        context['shared_notes'] = Notes.objects.filter(shared_with=self.request.user)
        return context
    

class NotesDetailView(DetailView):
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
        return HttpResponseRedirect(self.get_success_url())

class NotesUpdateView(UpdateView):
    model = Notes
    form_class = NotesForm
    success_url = '/smart/notes'

class NotesDeleteView(DeleteView):
    model = Notes
    success_url = '/smart/notes'
    template_name = 'notes/notes_delete.html'