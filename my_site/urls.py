from django.urls import path

from . import views

urlpatterns = [
    path('', views.StartingPageView.as_view(), name='starting_page'),
    path('products/<str:school>/', views.AllProductView.as_view(), name='all_products'),
    path('product/<slug>/', views.ProductDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add_to_cart'),
    path('add-coupon/', views.AddCouponView.as_view(), name='add_coupon'),
    path('add_single_item_to_cart/<slug>/', views.add_single_item_to_cart, name='add_single_item_to_cart'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order_summary'),
    path('remove-from-cart/<slug>', views.remove_from_cart, name='remove_from_cart'),
    path('remove-item-from-cart/<slug>/', views.remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('checkout/', views.CheckOutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
    path('request-refund/', views.RequestRefundView.as_view(), name='request_refund'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my_orders'),
    path('search/', views.product_search, name='product_search')
]