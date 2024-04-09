from django.http import HttpRequest, HttpResponse, HttpResponseServerError
import requests
from django.db import IntegrityError
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .models import  *
from .forms import *
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.http import FileResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import Decimal
from .services import sendVerificationEmail
from django.template.loader import render_to_string
from django.db import transaction
import logging
import paypalrestsdk




User = get_user_model()



# Create your views here.

def index(request):
    products = Product.objects.all().order_by('pk')  # Fetch all products
    products_paginator = Paginator(products, 10)
    testimonials = Testimonials.objects.all()
    cart_products = None
    if request.user.is_authenticated:
        cart_products = request.user.cartitem_set.all()
    page_number = request.GET.get('page')
    try:
        products_page_obj = products_paginator.page(page_number)
    except PageNotAnInteger:
        products_page_obj = products_paginator.page(1)
    except EmptyPage:
        products_page_obj = products_paginator.page(products_paginator.num_pages)
    
    context = {
        'products_page_obj': products_page_obj,
        'cart_products': cart_products,
        "testimonials": testimonials,
    }
    return render(request, 'index.html', context)




@transaction.atomic(durable=True, savepoint=False)
def register_vendor(request: HttpRequest):
    form = VendorRegistrationForm

    if request.method == "POST":
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # create vendor instance

            vendor = form.save(commit=False)
            vendor.is_vendor = True
            vendor.save()

            sendVerificationEmail(user_id=vendor.id, email=vendor.email)

            messages.success(request, f"""Account created for {
                             vendor.username}, Please check your email(Junk, Spam or Bin) and verify your account""")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return render(request, "vendor_register.html", {"form": form})


@transaction.atomic(durable=True, savepoint=False)
def verify_email(request: HttpRequest, token):
    account_token = get_object_or_404(AccountVerificationToken, id=token)

    if not account_token.has_expired:
        user = account_token.user

        if user.is_verified:
            return render(request, "account-verification-failure.html")

        user.is_verified = True
        user.save()

        return render(request, "account-verification-success.html")
    return render(request, "account-verification-failure.html")   



#def verify_email(request, user_id):
#    user = User.objects.get(id=user_id)
#    user.profile.email_verified = True
#    user.profile.save()
#    messages.success(request, 'Email verified successfully!')
#    return redirect('profile')




@transaction.atomic(durable=True, savepoint=False)
def register(request: HttpRequest):
    form = UserRegistrationForm

    if request.method == "POST":
        form = UserRegistrationForm(request.POST or None)
        if form.is_valid():
            # create vendor instance

            user = form.save()

            sendVerificationEmail(user_id=user.id, email=user.email)

            messages.success(request, f"""Account created for {
                             user.username}, Please check your email(Junk, Spam or Bin) and verify your account""")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return render(request, "register.html", {"form": form})


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    template_name = 'password_reset.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'password_reset_confirm.html'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
    


def user_logout(request):
    messages.success(request, f'You are logged Out.')
    logout(request)
    # Redirect to a specific page after logout
    return redirect('index')




def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    products = Product.objects.all().order_by('pk')
    cart_products = CartItem.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'product_details.html', {'product': product, 'cart_products': cart_products, 'products_page_obj': products})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_authenticated:
        quantity = request.GET.get('quantity', 1)  # Default quantity is 1 if not provided
        cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
        if not created:
            cart_item.quantity += int(quantity)  # Increase quantity by the provided amount
        cart_item.save()
        return redirect('cart')
    else:
        return redirect(reverse_lazy('login'))


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping_fee = Decimal('5.80')  # Adjust the shipping fee here
    total = subtotal + shipping_fee  # Add shipping fee to subtotal
    return render(request, 'cart.html', {'cart_items': cart_items, 'subtotal': subtotal, 'shipping_fee': shipping_fee, 'total': total})



def search(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(price__icontains=query)).order_by('id')
    else:
        products = Product.objects.all().order_by('id')
    
    # Pagination
    products_paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    try:
        products_page_obj = products_paginator.page(page_number)
    except PageNotAnInteger:
        products_page_obj = products_paginator.page(1)
    except EmptyPage:
        products_page_obj = products_paginator.page(products_paginator.num_pages)
    
    return render(request, 'search.html', {'products': products_page_obj, 'query': query, 'products_page_obj': products_page_obj})

# View for removing an item from the cart
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

# View for the checkout process
def checkout(request):
    try:
        if request.user.is_authenticated:
            cart_items = request.user.cartitem_set.all()
        else:
            cart = request.session.get('cart', {})
            product_ids = cart.keys()
            cart_items = Product.objects.filter(id__in=product_ids)
            for item in cart_items:
                item.quantity = cart[str(item.id)]['quantity']
        
        subtotal = sum(Decimal(item.product.price) * item.quantity for item in cart_items)  # Calculate subtotal

        if request.method == 'POST':
            # Handle checkout logic here
            
            # Placeholder behavior for unregistered users (guest checkout)
            # You may need to adjust this logic based on your payment gateway integration
            if not request.user.is_authenticated:
                # Redirect to registration page
                return redirect('buyer_register')

        shipping_fee = Decimal('5.80')  # Shipping fee
        total = subtotal + shipping_fee  # Add shipping fee to total

        return render(request, 'checkout.html', {'cart_items': cart_items, 'subtotal': subtotal, 'shipping_fee': shipping_fee, 'total': total})
    except Exception as e:
        return HttpResponseServerError(f"An error occurred: {e}")


def paypal_checkout(request):
    total = request.GET.get('total', 0)

    # Configure PayPal SDK with your credentials
    paypalrestsdk.configure({
        'mode': 'sandbox',  # Change to 'live' for production
        'client_id': settings.PAYPAL_CLIENT_ID,
        'client_secret': settings.PAYPAL_CLIENT_SECRET,
    })

    # Create a PayPal payment object
    payment = paypalrestsdk.Payment({
        'intent': 'sale',
        'payer': {
            'payment_method': 'paypal',
        },
        'redirect_urls': {
            'return_url': 'http://localhost:8000/checkout/paypal_success',  # Change to your success URL
            'cancel_url': 'http://localhost:8000/checkout/paypal_cancel',  # Change to your cancel URL
        },
        'transactions': [{
            'amount': {
                'total': total,
                'currency': 'USD',  # Change currency if needed
            },
        }],
    })

    # Create the payment on PayPal
    if payment.create():
        # Redirect user to PayPal for payment approval
        for link in payment.links:
            if link.method == 'REDIRECT':
                return redirect(link.href)
    else:
        return HttpResponseServerError("Failed to create PayPal payment") 

def order_success(request):
    return render(request, 'order_success.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        print(name, email, subject, message)
        ContactForm.objects.create(name=name, email=email, subject=subject, message=message,)
        messages.success(request, f'Your Message Has Been Sent Successfully!')
        return redirect('index')
    else:
        return render(request, 'contact.html')


@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the vendor associated with the logged-in user
            vendor = request.user

            # Process the form data if it's valid
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            quantity = form.cleaned_data['quantity']
            image = form.cleaned_data['image']

            # Save the uploaded image and other form data to the database
            product = Product.objects.create(
                vendor=vendor,
                name=name,
                description=description,
                price=price,
                quantity=quantity,
                image=image
            )
            messages.success(request, f'Your product sent to the shop Successfully!')

            # Redirect to the vendor profile page or any other desired page
            return redirect('profile')  # Adjust the URL name as needed
    else:
        form = ImageUploadForm()
    
    # Render the form template with the form object
    return render(request, 'upload_image.html', {'form': form})


def about(request):
    return render(request, 'about.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms(request):
    return render(request, 'terms.html')


def shop(request):
    products = Product.objects.all().order_by('pk')  # Fetch all products
    return render(request, 'shop.html', {'products_page_obj': products})

@login_required
def profile(request):
    # Retrieve the logged-in user (vendor)
    vendor = request.user

    # You can now access all attributes of the vendor
    # For example:
    vendor_email = vendor.email
    vendor_username = vendor.username
    vendor_country = vendor.country
    vendor_products = Product.objects.filter(vendor=request.user)
    # Add other attributes as needed

    # You can pass the vendor object or specific attributes to the template context
    context = {
        'vendor': vendor,
        'products': vendor_products,
        # Add other context data as needed
    }
    return render(request, 'profile.html', context)


def paypal_success(request):
    # This view is called when the user successfully completes the PayPal payment
    # You can perform any necessary actions here, such as updating the order status
    # and displaying a success message to the user
    return render(request, 'paypal_success.html')

def paypal_cancel(request):
    # This view is called when the user cancels the PayPal payment
    # You can redirect the user to a specific page or display a message
    return render(request, 'paypal_cancel.html')