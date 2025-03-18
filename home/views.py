from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView


from django.shortcuts import redirect

from django.contrib.auth import logout

from .forms import LoginForm, RegisterForm


class HomeView(TemplateView):
    template_name = 'home/welcome.html'

    extra_context = {'today': datetime.today()}

class AuthorizedView(LoginRequiredMixin,TemplateView):
    template_name = 'home/authorized.html'

    login_url = '/admin/login/'

class LoginInterfaceView(LoginView):
    template_name = 'home/login.html'

    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/smart/notes')
        return super().get(request, *args, **kwargs)
    def form_invalid(self, form):
        # Customize how errors are handled here
        return self.render_to_response(self.get_context_data(form=form, errors=form.errors))

def logout_view(request):
    logout(request)
    return redirect('/login')

# class LogoutInterfaceView(LogoutView):
#     next_page = '/login'


class RegisterInterfaceView(CreateView):
    template_name = 'home/register.html'
    form_class = RegisterForm
    success_url = '/smart/notes'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/smart/notes')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        email = form.cleaned_data.get('email')
        self.object.email = email
        self.object.save()
        return response
