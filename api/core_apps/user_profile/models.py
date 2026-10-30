from typing import Any 
from cloudinary.models import CloudinaryField 
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField 
from phonenumber_field.modelfields import PhoneNumberField 

from core_apps.common.models import TimeStampedModel


class Profile(TimeStampedModel):
    class Salutation(models.TextChoices):
        MR = 'MR', _('Mr')
        MRS = 'MRS', _('Mrs')
        MS = 'MS', _('Ms')
        DR = 'DR', _('Dr')

    class Gender(models.TextChoices):
        MALE = 'MALE', _('Male')
        FEMALE = 'FEMALE', _('Female')
        OTHER = 'OTHER', _('Other')

    class MaritalStatus(models.TextChoices):
        SINGLE = 'SINGLE', _('Single')
        MARRIED = 'MARRIED', _('Married')
        DIVORCED = 'DIVORCED', _('Divorced')
        WIDOWED = 'WIDOWED', _('Widowed')
        SEPARATED = 'SEPARATED', _('Separated')  
    
    class IdentificationMeans(models.TextChoices):
        PASSPORT = 'PASSPORT', _('Passport')
        NATIONAL_ID = 'NATIONAL_ID', _('National ID')
        DRIVING_LICENSE = 'DRIVING_LICENSE', _('Driving License')
        OTHER = 'OTHER', _('Other')

    class EmploymentStatus(models.TextChoices):
        EMPLOYED = 'EMPLOYED', _('Employed')
        SELF_EMPLOYED = 'SELF_EMPLOYED', _('Self Employed')
        UNEMPLOYED = 'UNEMPLOYED', _('Unemployed')
        RETIRED = 'RETIRED', _('Retired')
        STUDENT = 'STUDENT', _('Student')  

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    title = models.CharField(_("Title"), max_length=10, choices=Salutation.choices, null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=10, choices=Gender.choices, null=True, blank=True)
    marital_status = models.CharField(_("Marital Status"), max_length=10, choices=MaritalStatus.choices, null=True, blank=True)
    birth_date = models.DateField(_("Date of Birth"), default=settings.DEFAULT_DATE)
    country_of_birth = CountryField(_("Country of Birth"), default=settings.DEFAULT_COUNTRY)
    place_of_birth = models.CharField(_("Place of Birth"), max_length=100, null=True, blank=True)
    means_of_identification = models.CharField(_("Means of Identification"), max_length=20, choices=IdentificationMeans.choices, null=True, blank=True)
    id_issue_date = models.DateField(_("ID Issue Date"), null=True, blank=True, default=settings.DEFAULT_DATE)
    id_expiry_date = models.DateField(_("ID Expiry Date"), null=True, blank=True, default=settings.DEFAULT_EXPIRY_DATE)
    id_number = models.CharField(_("ID Number"), max_length=100, null=True, blank=True)
    passport_number = models.CharField(_("Passport Number"), max_length=100, null=True, blank=True)
    nationality = models.CharField(_("Nationality"), max_length=100, null=True, blank=True, default="india")
    phone_number = PhoneNumberField(_("Phone Number"), null=True, blank=True)
    address = models.CharField(_("Address"), max_length=100, null=True, blank=True)
    city = models.CharField(_("City"), max_length=100, null=True, blank=True)
    country = CountryField(_("Country"), default=settings.DEFAULT_COUNTRY)
    employment_status = models.CharField(_("Employment Status"), max_length=20, choices=EmploymentStatus.choices, null=True, blank=True)
    annual_income = models.CharField(_("Annual Income"), max_length=20, null=True, blank=True)
    date_of_employment = models.DateField(_("Date of Employment"), null=True, blank=True, default=settings.DEFAULT_DATE)
    employment_type = models.CharField(_("Employment Type"), max_length=20, null=True, blank=True)  
    employer_city = models.CharField(_("Employer City"), max_length=100, null=True, blank=True) 
    employer_country = CountryField(_("Employer Country"), default=settings.DEFAULT_COUNTRY)
    employer_state = models.CharField(_("Employer State"), max_length=100, null=True, blank=True) 
    photo = CloudinaryField(_("photo"), blank=True, null=True)
    photo_url = models.URLField(_("photo URL"), blank=True, null=True)
    id_phot = CloudinaryField(_("ID Photo"), blank=True, null=True)
    id_phot_url = models.URLField(_("ID Photo URL"), blank=True, null=True)
    signature_photo = CloudinaryField(_("Signature Photo"), blank=True, null=True)
    signature_photo_url = models.URLField(_("Signature Photo URL"), blank=True, null=True)

    def clean(self) -> None:
        super().clean()
        if self.id_expiry_date and self.id_issue_date:
            if self.id_expiry_date <= self.id_issue_date:
                raise ValidationError(_("ID Expiry Date must be greater than ID Issue Date"))

    def save(self, *args, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
    
    def is_complete_with_next_of_kin(self) -> bool:
        required_fields = [
            self.title,
            self.gender,
            self.marital_status,    
            self.birth_date,
            self.country_of_birth,
            self.place_of_birth,
            self.means_of_identification,
            self.id_issue_date,
            self.id_expiry_date,
            self.id_number,
            self.passport_number,
            self.nationality,
            self.phone_number,
            self.address,
            self.city,
            self.country,
            self.photo,
            self.id_phot,
            self.signature_photo,
        ]

        return all(required_fields) and self.next_of_kin.exists()

    def __str__(self) -> str:
        return f"{self.user.full_name}'s Profile"   


class NextOfKin(TimeStampedModel):
    class Salutation(models.TextChoices):
        MR = 'MR', _('Mr')
        MRS = 'MRS', _('Mrs')
        MS = 'MS', _('Ms')
        DR = 'DR', _('Dr')

    class Gender(models.TextChoices):
        MALE = 'MALE', _('Male')
        FEMALE = 'FEMALE', _('Female')
        OTHER = 'OTHER', _('Other')

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="next_of_kin")
    title = models.CharField(_("Title"), max_length=10, choices=Salutation.choices, null=True, blank=True)
    first_name = models.CharField(_("First Name"), max_length=100, null=True, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=100, null=True, blank=True)
    middle_name = models.CharField(_("Middle Name"), max_length=100, null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=10, choices=Gender.choices, null=True, blank=True)
    date_of_birth = models.DateField(_("Date of Birth"), default=settings.DEFAULT_DATE)
    email_address = models.EmailField(_("Email Address"), null=True, blank=True, db_index=True)    
    phone_number = PhoneNumberField(_("Phone Number"), null=True, blank=True) 
    address = models.CharField(_("Address"), max_length=100, null=True, blank=True)
    city = models.CharField(_("City"), max_length=100, null=True, blank=True)
    state = models.CharField(_("State"), max_length=100, null=True, blank=True)
    country = CountryField(_("Country"), default=settings.DEFAULT_COUNTRY)
    is_primary = models.BooleanField(_("Is Primary"), default=False)

    def clean(self) -> None:
        super().clean()
        if self.is_primary:
            primary_next_of_kin = NextOfKin.objects.filter(profile=self.profile, is_primary=True).exclude(pk=self.pk)
            if primary_next_of_kin.exists():
                raise ValidationError(_("Primary Next of Kin already exists"))
    
    def save(self, *args, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}'s Next of Kin" 

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "is_primary"],
                name="unique_primary_next_of_kin",
                condition=models.Q(is_primary=True) 
            )  
        ]