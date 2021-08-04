from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from .forms import SignUpForm, CheckoutForm, CouponForm, RefundForm, ReviewForm, ProductSearchForm

from .models import Product, ShoppingCartOrder, ShoppingCartOrderItem, Address, Payment, Coupon, Refund, Review

import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class StartingPageView(ListView):
    template_name = 'my_site/index.html'
    model = Product
    ordering = ['id']
    context_object_name = 'products'

    def get_queryset(self):
        base_query = super().get_queryset()
        data = base_query[:5]
        return data


class AllProductView(ListView):
    template_name = 'my_site/all_products.html'
    model = Product
    ordering=['id']
    paginate_by = 9
    context_object_name = 'all_products'

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        fltr = self.kwargs['school']
        if fltr != 'all':
            qs = qs.filter(school=self.kwargs['school'])
        return qs


class ProductDetailView(DetailView):
    model = Product
    template_name = 'my_site/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['object']
        reviews = Review.objects.filter(product=product)
        context['reviews'] = reviews
        return context
     
    
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = ShoppingCartOrder.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(request, 'my_site/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(request,'You do not have an active order')
            return redirect('all_products', school='all')


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckOutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = ShoppingCartOrder.objects.get(user=request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=request.user, 
                address_type='S', 
                default=True)
            if shipping_address_qs.exists():
                context.update({
                    'default_shipping_address': shipping_address_qs[0]
                })

            billing_address_qs = Address.objects.filter(
                user=request.user, 
                address_type='B', 
                default=True)
            if billing_address_qs.exists():
                context.update({
                    'default_billing_address': billing_address_qs[0]
                })

            return render(request, 'my_site/checkout.html', context)
        except ObjectDoesNotExist:
            messages.info(request,'You do not have an active order')
            return redirect('checkout')
        

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST or None)

        try:
            order = ShoppingCartOrder.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print('using default data')
                    address_qs = Address.objects.filter(
                    user=request.user, 
                    address_type='S', 
                    default=True)
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(request, 'No default shipping address available')
                        return redirect(request,'checkout')
                else:
                    print('user is entering a new shipping address')

                    shipping_address = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address,
                            apartment = shipping_address2,
                            country = shipping_country,
                            zip_code = shipping_zip,
                            address_type = 'S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(request, 'Please fill in the required shipping address fields')

                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print('using default data')
                    address_qs = Address.objects.filter(
                    user=request.user, 
                    address_type='B', 
                    default=True)
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(request, 'No default billing address available')
                        return redirect(request,'checkout')
                else:
                    print('user is entering a new billing address')

                    billing_address = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address, billing_country, billing_zip]):
                        billing_address = Address(
                            user = self.request.user,
                            street_address = billing_address,
                            apartment = billing_address2,
                            country = billing_country,
                            zip_code = billing_zip,
                            address_type = 'B'
                        )
                        billing_address.save()
                        
                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(request, 'Please fill in the required billing address fields')    


                payment_option = form.cleaned_data.get('payment_option')
                
                if payment_option == 'S':
                    return redirect('payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('payment', payment_option='paypal')
                else:
                    messages.warning(request, 'Invalid payment option selected')
                    return redirect('checkout')
        except ObjectDoesNotExist:
            messages.warning(request,'You do not have an active order')
            return redirect('order_summary')

        
class PaymentView(View):
    def get(self, request, *args, **kwargs):
        order = ShoppingCartOrder.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(request,'my_site/payment.html', context)
        else:
            messages.warning(request,'You have not added a billing address')
            return redirect('checkout')


    def post(self, request, *args, **kwargs):
        order = ShoppingCartOrder.objects.get(user=self.request.user, ordered=False)
        token = request.POST.get('stripeToken')
        amount = int(order.get_total() * 100) #cents

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )

            #create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            #assign the payment to order
            order_items = order.items.all()
            #this would be a query set, .update() will update the entire qs for us
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, 'Your order was successful!')
            return redirect('/')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect('/')
            
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, 'Invalid Parameters')
            return redirect('/')
            
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, 'Not Authenticated')
            return redirect('/')
            
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, 'Network Error')
            return redirect('/')

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send yourself an email
             messages.warning(self.request, 'Something went wrong, you were not charge. Please try again')
             return redirect('/')
            
        except Exception as e:
            # Something else happened, completely unrelated to Stripe #send email to ourselves, means somethign went wrong w/ code
            messages.warning(self.request, 'Serious error has occured, we have been notifed of this issue')
            return redirect('/')


class MyOrdersView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = ShoppingCartOrder.objects.filter(user=self.request.user, ordered=True)
            form = ReviewForm(user=self.request.user)
            context = {
                'object': order,
                'form': form
            }
            return render(request, 'my_site/my_orders.html', context)
        except ObjectDoesNotExist:
            messages.warning(request, 'You do not have any orders')
            return redirect('all_products', school='all')

    def post (self, request, *args, **kwargs):
        form = ReviewForm(request.POST, user=self.request.user)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('starting_page')
        else:
            order = ShoppingCartOrder.objects.filter(user=self.request.user, ordered=True)
            form = ReviewForm(request.POST, user=self.request.user)
            context = {
                'object': order,
                'form': form
            }
            return render(request, 'my_site/my_orders.html', context)




class RequestRefundView(View):
    def get(self, request, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(request, 'my_site/request_refund.html', context)


    def post(self, request, *args, **kwargs):
        form = RefundForm(request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            #edit order
            try:
                order = ShoppingCartOrder.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                #store the refund for record keeping purposes
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(request, 'Your request was recieved')
                return redirect('request_refund')

            except ObjectDoesNotExist:
                messages.info(request, 'This order does not exist')
                return redirect('request_refund')


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item, created = ShoppingCartOrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order = ShoppingCartOrder.objects.filter(user=request.user, ordered=False)
    if order.exists():
        order = order[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,'This item quantity was updated')
            return redirect('product', slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request,'This item was added to your cart')
            return redirect('product', slug=slug)
    else:
        ordered_date = timezone.now()
        order = ShoppingCartOrder.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,'This item was added to your cart') 
        return redirect('product', slug=slug)



@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order = ShoppingCartOrder.objects.filter(user=request.user, ordered=False)
    if order.exists():
        order = order[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = ShoppingCartOrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request,'This item was removed from your cart')
            return redirect('order_summary')
        else:
            messages.info(request,'This item is not in your cart')
            return redirect('product', slug=slug)
    else:
        messages.info(request,'You do not have an active order')
        return redirect('product', slug=slug)



@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order = ShoppingCartOrder.objects.filter(user=request.user, ordered=False)
    if order.exists():
        order = order[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = ShoppingCartOrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False)[0]
            if order_item.quantity >1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request,'This item quantity was updated')
            return redirect('order_summary')
        else:
            #add nessage saying orderitem doesn't contain the item
            messages.info(request,'This item is not in your cart')
            return redirect('product', slug=slug)
    else:
        #add a message saying user doesn't have order
        messages.info(request,'You do not have an active order')
        return redirect('product', slug=slug)

@login_required
def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item, created = ShoppingCartOrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order = ShoppingCartOrder.objects.filter(user=request.user, ordered=False)
    if order.exists():
        order = order[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,'This item quantity was updated')
            return redirect('order_summary')
        else:
            order.items.add(order_item)
            messages.info(request,'This item was added to your cart')
            return redirect('order_summary')
    else:
        ordered_date = timezone.now()
        order = ShoppingCartOrder.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,'This item was added to your cart') 
        return redirect('order_summary')


def get_coupon(request, code):
    
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request,'This coupon does not exist')
        return redirect('checkout')


##############KEEP IN MIND, NO VALIDATION FOR THIS COUPON##########################################
#EXAMPLE: not keeping track of how many times it has been used, if its still active, things like that
class AddCouponView(View):
    def post(self, request, *args, **kwargs):
            form = CouponForm(request.POST or None)
            if form.is_valid():
                try:
                    code = form.cleaned_data.get('code')
                    order = ShoppingCartOrder.objects.get(user=request.user, ordered=False)
                    order.coupon = get_coupon(request, code)
                    order.save()
                    messages.success(request,'Sucessfully added coupon!')
                    return redirect('checkout')

                except ObjectDoesNotExist:
                    messages.info(request,'You do not have an active order')
                    return redirect('checkout')


def product_search(request):
    form = ProductSearchForm()
    q = ''
    results = []

    if 'q' in request.GET:
        form = ProductSearchForm(request.GET)
        if form.is_valid():
            q = form.cleaned_data['q']
            ##############postgres single search term
            # results = Product.objects.filter(name__search=q)
            ###############searching multiple fields
            # results = Product.objects.annotate(search=SearchVector('name', 'artist')).filter(search=q)
            ################improvement of above, words are passed through stemming algo, searching logical terms etc
            # results = Product.objects.annotate(search=SearchVector('name', 'artist')).filter(search=SearchQuery(q))
            ################rankings
            vector = SearchVector('name', weight='A') + \
                SearchVector('artist', weight='B')
            query = SearchQuery(q)
            results = Product.objects.annotate(rank=SearchRank(vector, query, cover_density=True)).order_by('-rank')

            results = Product.objects.annotate(search=SearchVector('name', 'artist')).filter(search=SearchQuery(q))

    return render(request, 'my_site/search.html',{
        # 'form': form,
        'q': q,
        'results': results
        })