from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User
from .forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = [
        "email",
        "id_no",
        "first_name",
        "last_name",
        "middle_name",
        "role",
        "is_staff",
        "is_active",
    ]
    list_filter = ["is_staff", "is_active", "role"]
    search_fields = [
        "email",
        "id_no",
        "first_name",
        "last_name",
        "middle_name",
    ]
    ordering = ["email"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "id_no",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "security_question",
                    "security_answer",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    fieldsets = (
        (_("Login Credentials"), {"fields": ("username", "email", "password")}),
        (
            _("Personal Information"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "middle_name",
                    "id_no",
                    "role",
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "AccountStatus",
                    "failed_login_attempts",
                    "last_failed_login",
                )
            },
        ),
        (
            _("Security Information"),
            {
                "fields": (
                    "security_question",
                    "security_answer",
                )
            },
        ),
        (
            _("Permission and Groups"),
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "is_active",
                )
            },
        ),
        (
            _("Important Dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )
