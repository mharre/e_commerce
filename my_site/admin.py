from django.contrib import admin

from .models import Artist, Product, Review, ShoppingCartOrderItem, ShoppingCartOrder, Payment, Coupon, Refund, Address

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_creation', 'price', 'artist')
    prepopulated_fields = {'slug': ('shortened_name',)}


def make_refund_accepted(ModelAdmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class ShoppingCartOrderAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'ordered', 
        'being_delivered',
        'recieved', 
        'refund_requested', 
        'refund_granted',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon'
    )
    list_display_links = (
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon'
    )
    list_filter = ('user', 
        'ordered', 
        'being_delivered', 
        'recieved', 
        'refund_requested', 
        'refund_granted'
    )
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'street_address',
        'apartment',
        'country',
        'zip_code',
        'address_type',
        'default'
    )
    list_filter = (
        'default',
        'address_type',
        'country'
    )
    search_fields = [
        'user',
        'street_address',
        'apartment',
        'zip'
    ]

class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'product',
        'comment',
        'rating'
    )


admin.site.register(Artist)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ShoppingCartOrderItem)
admin.site.register(ShoppingCartOrder, ShoppingCartOrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)