from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User


class MyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = forms.widgets.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            })
        self.fields['password'].widget = forms.widgets.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            })


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(min_length= 4, max_length=30, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    last_name = forms.CharField(min_length= 4, max_length=30, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={
            'class': 'form-control'
        }
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Password Confirmation'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'

        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

        self.fields['password1'].widget = forms.widgets.PasswordInput(attrs={
            'class': 'form-control'
        })
        self.fields['password2'].widget = forms.widgets.PasswordInput(attrs={
            'class': 'form-control'
        })

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2' )
        help_texts = {
            'username': None,
        }
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            )
        }


class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(min_length= 4, max_length=30, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    last_name = forms.CharField(min_length= 4, max_length=30, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={
            'class': 'form-control'
        }
    ))


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'This email already exists')
        return email


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False


class PwdChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Old Password'
    }))
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Password'
    }))
    new_password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Password'
    }))
    
    