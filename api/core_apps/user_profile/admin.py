from django.contrib import admin
from cloudinary.forms import CloudinaryFileField 
from django import forms 
from django.utils.html import format_html 
from django.utils.translation import gettext_lazy as _
from .models import NextOfKin, Profile


class ProfileAdminForm(forms.ModelForm):
    photo = CloudinaryFileField(
        options={
            "crop": "thumb",
            "width": 200,
            "height": 200,
            "folder": "bank_photo",
        },
        required=False,
    )
    
    class Meta:
        model = Profile
        fields = (
            "user",
            "title",
            "gender",
            "marital_status",
            "birth_date",
            "country_of_birth",
            "place_of_birth",
            "means_of_identification",
            "id_issue_date",
            "id_expiry_date",
            "id_number",
            "passport_number",
            "nationality",
            "phone_number",
            "address",
            "city",
            "country",
            "employment_status",
            "annual_income",
            "date_of_employment",
            "employment_type",  
            "employer_city", 
            "employer_country",
            "employer_state",
            "photo",
            "id_phot",
            "signature_photo",
        )


class NextOfKinInline(admin.StackedInline):
    model = NextOfKin
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ('user', 'full_name', 'phone_number', 'country', 'city', 'display_photo')
    list_display_links = ["user"]
    list_filter = ["gender", "marital_status", "means_of_identification", "employment_status"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "phone_number", "country", "city", "address", "place_of_birth"]
    readonly_fields = ["user"]
    inlines = [NextOfKinInline]
    
    fieldsets = (
        ("Personal Information", {
            "fields": (
                "user",
                "title",
                "gender",
                "marital_status",
                "birth_date",
                "country_of_birth",
                "place_of_birth",
                "means_of_identification",
                "id_issue_date",
                "id_expiry_date",
                "id_number",
                "passport_number",
                "nationality",
            )
        }),
        ("Contact Information", {
            "fields": (
                "phone_number",
                "address",
                "city",
                "country",
            )
        }),
        ("Employment Information", {
            "fields": (
                "employment_status",
                "annual_income",
                "date_of_employment",
                "employment_type",  
                "employer_city", 
                "employer_country",
                "employer_state",
            )
        }),
        ("Media & Documents", {
            "fields": (
                "photo",
                "id_phot",
                "signature_photo",
            )
        }),
    )   

    @admin.display(description=_("Full Name"))
    def full_name(self, obj) -> str:
        return obj.user.full_name if obj.user else "-"

    @admin.display(description=_("Email"))
    def email(self, obj) -> str:
        return obj.user.email if obj.user else "-"

    @admin.display(description=_("Photo"))
    def display_photo(self, obj) -> str:
        if obj.photo:
            return format_html("<img src='{}' width='50' height='50' style='border-radius: 50%; object-fit: cover;'>", obj.photo.url)
        return "-"


@admin.register(NextOfKin)
class NextOfKinAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'profile', 'phone_number', 'email_address', 'country', 'is_primary')
    list_display_links = ["full_name"]
    list_filter = ["gender", "country", "is_primary"]
    search_fields = ["first_name", "last_name", "email_address", "phone_number", "profile__user__email"]

    @admin.display(description=_("Full Name"))
    def full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}".strip()