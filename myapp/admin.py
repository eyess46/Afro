from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserBaseAdmin
from django.utils.translation import gettext_lazy as _
from .models import *


@admin.register(User)
class UserAdmin(UserBaseAdmin):
    list_display = ["id", "username", "email", "is_verified", "country"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email",
         "phone_number", "is_verified", "country", "address", "id_card", "profile_picture")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "is_vendor"
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(AccountVerificationToken)
class AccountVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "has_expired"]
    
# Register your models here.
admin.site.register(Product)
admin.site.register(ShippingAddress)
admin.site.register(ContactForm)
admin.site.register(CartItem)
admin.site.register(Payment)
admin.site.register(OrderSummary)
admin.site.register(Subscriber)
admin.site.register(Testimonials)





