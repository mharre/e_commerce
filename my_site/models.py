from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField

from decimal import *


ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping')
)


class Artist(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=120)
    shortened_name = models.CharField(max_length=50)
    date_of_creation = models.CharField(max_length=20, null=True)
    history = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    discount_price = models.FloatField(blank=True, null=True)
    school = models.CharField(max_length=50)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='images', null=True)
    slug = models.SlugField()
    
    

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.shortened_name)
        super().save(*args, **kwargs)

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={
            'slug': self.slug
        })



#this is to link between the product and the shopping cart order itself, once added to cart an order becomes this class
class ShoppingCartOrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.item.name}'

    def get_total_order_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_order_price()

    class Meta:
        verbose_name_plural = 'Order Item(link between)'

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip_code = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.IntegerField()

    def __str__(self):
        return self.code


class ShoppingCartOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(ShoppingCartOrderItem) 
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    #need related name because foreign key is on the same model (Address)
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    recieved = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    # 1. Item added to cart
    # 2. Add a billing address(failed checkout)
    # 3. Payment (preprocessing, processing, packaging etc)
    # 4. Being delievered
    # 5. Recieved 
    # 6. Refunds

    def __str__(self):
        return str(self.user)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount 
        return total

    class Meta:
        verbose_name_plural = 'Order'


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(Decimal('0.1')), MaxValueValidator(Decimal('5.0'))])
    comment = models.TextField(validators=[MinLengthValidator(10)])
    date = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.user) 


class Refund(models.Model):
    order = models.ForeignKey(ShoppingCartOrder, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f'{self.pk}'


