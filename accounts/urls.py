from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from . import forms

app_name='accounts'

urlpatterns = [
    path('login/', views.MyLoginView.as_view(authentication_form=forms.MyAuthenticationForm), name='login'),
    path('register/', views.signup, name='sign_up'),
    path('profile/edit', views.EditProfileInformationView.as_view(), name='edit'),
    path('password_change/', auth_views.PasswordChangeView.as_view(form_class=forms.PwdChangeForm), name='password_change')
]