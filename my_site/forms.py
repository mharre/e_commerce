from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(
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

class MyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = forms.widgets.TextInput(attrs={
                'class': 'form-control'
            })
        self.fields['password'].widget = forms.widgets.PasswordInput(attrs={
                'class': 'form-control'
            }) 

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='Choose...').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
        }))
    shipping_zip = forms.CharField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='Choose...').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
        }))
    billing_zip = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo Code',
        'aria-label': "Recipient's username",
        'aria-describedby': "basic-addon2"
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 4
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    

    

        

        
    
   