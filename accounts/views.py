from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View

from .forms import SignUpForm, UserEditForm

class MyLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome {self.request.user}')
        return response


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse('starting_page'))
    else:
        form = SignUpForm()
    return render(request, 'registration/sign_up.html', {
        'form': form
    })


class EditProfileInformationView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = UserEditForm(initial={
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
            'email': self.request.user.email
        })
        context = {
            'form':form
        }
        return render(request, 'accounts/update.html', context)

    def post(self, request, *args, **kwargs):
        form = UserEditForm(instance=request.user, data=request.POST)
        context = {
            'form': form
        }
        if form.is_valid():
            form.save()
            messages.success(request,'Profile Successfully Updated')
            return redirect('/')
        else:
            return render(request, 'accounts/update.html', context)
    
