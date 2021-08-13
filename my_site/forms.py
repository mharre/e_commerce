from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .models import Review, ShoppingCartOrderItem, Product

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
    

class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ReviewForm, self).__init__(*args, **kwargs)
        ordered_product_ids = ShoppingCartOrderItem.objects.filter(user=user, ordered=True).values_list('item_id', flat=True)

        self.fields['product'].queryset = Product.objects.filter(id__in=ordered_product_ids)

    class Meta:
        model = Review
        exclude = ['user', 'date']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5.0....'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control'
            })
        }
        error_messages = {
            'rating': {
                'max_digits': 'Please ensure that the rating is a decimal number and only 2 digits long',
                'max_whole_digits': 'Please ensure that the rating is a decimal number with only 1 digit before the decimal point'
            },
            'comment': {
                'min_length': 'Please ensure your comment has at least %(limit_value)d characters (it has %(show_value)d)'
            }
        }
    

class ProductSearchForm(forms.Form):
    q = forms.CharField()      

        
    
   