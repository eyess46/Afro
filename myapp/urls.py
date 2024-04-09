from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import search
from .views import user_logout




urlpatterns = [
    path('', views.index, name='index'),
    path("register/", views.register, name="register"),
    path("register-as-vendor/", views.register_vendor, name="register_vendor"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path('logout/', views.user_logout, name='logout'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),


    path('vendor/profile/', views.profile, name='profile'),
    path('vendor/product/upload/', views.upload_image, name='upload_image'),
    path('product/<int:product_id>/', views.product_details, name='product_details'),  

    # Email verification
    path("verify-email/<uuid:token>/", views.verify_email, name="verify_email"),
    # Cart-related URLs
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # Checkout process
    path('profile/', views.profile, name='profile'),

    path('checkout/', views.checkout, name='checkout'),
    path('checkout/paypal_checkout/', views.paypal_checkout, name='paypal_checkout'),
    path('paypal_checkout/success/', views.paypal_success, name='paypal_success'),
    path('paypal_checkout/cancel/', views.paypal_cancel, name='paypal_cancel'),

    # Other URLs
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('shop/', views.shop, name='shop'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('paypal_checkout/success/', views.paypal_success, name='paypal_success'),
    path('paypal_checkout/cancel/', views.paypal_cancel, name='paypal_cancel'),

]
