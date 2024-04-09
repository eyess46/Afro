from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .models import *




User = get_user_model()


class VendorRegistrationForm(UserCreationForm):
    id_card = forms.ImageField(required=True)  # Add this line to handle ID card upload
    profile_picture = forms.ImageField(required=True)  # Add this line to handle profile picture upload

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'country', 'address', 'email',
                  'phone_number', 'id_card', 'profile_picture', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_vendor = True
        
        # Save ID card and profile picture
        if commit:
            user.id_card = self.cleaned_data['id_card']
            user.profile_picture = self.cleaned_data['profile_picture']
            user.save()
        return user


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
    


# Form for product posting
class ImageUploadForm(forms.Form):
    name = forms.CharField(label='Name', max_length=200)
    description = forms.CharField(label='Description', widget=forms.Textarea)
    price = forms.DecimalField(label='Price', max_digits=10, decimal_places=2)
    quantity = forms.IntegerField(label='Quantity', initial=0)
    image = forms.ImageField(label='Upload Image', required=True, widget=forms.FileInput(attrs={'accept': 'image/*'}))

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['first_name', 'last_name', 'address', 'city', 'country', 'zip_code', 'mobile', 'email']

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254, label='Email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'autofocus': True}))
    new_password2 = forms.CharField(label='New password confirmation', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))