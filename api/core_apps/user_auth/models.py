from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _ 
from .emails import send_account_locked_email
from .mangers import UserManager

class User(AbstractUser):
    class SecurityQuestion(models.TextChoices):
       MAIDEN_NAME =(
        "maiden_name", _("What is your mother's maiden name?"),
        )
       FAVORITE_COLOR = (
        "favorite_color", _("What is your favorite color?"),
       )
       BIRTH_CITY = (
        "birth_city", _("What is your birth city?"),
       )
       CHILDHOOD_FRIEND_NAME = (
        "childhood_friend_name", _("What is your childhood friend's name?"),
       )

    class AccountStatus(models.TextChoices):
        ACTIVE = (
            "active", _("active")
        )
        LOCKED = (
            "locked", _("locked")
        )
        INACTIVE = (
            "inactive", _("inactive")
        )   
    class RoleChoice(models.TextChoices):
        CUSTOMER = (
            "customer", _("customer")
        )
        ACCOUNT_EXECUTIVE = (
            "account_executive", _("account_executive")
        )
        TELLER = (   
            "teller", _("teller")
        ) 
        BRANCH_MANAGER = (
            "branch_manager", _("branch_manager")
        )  
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    username = models.CharField(_("username"), max_length=150,unique=True)   
    security_question = models.CharField(_("Security Question"), max_length=40,choices=SecurityQuestion.choices)    
    security_answer = models.CharField(_("Security Answer"), max_length=150) 
    email = models.EmailField(_("email address"),unique=True,db_index=True) 
    first_name = models.CharField(_("First Name"), max_length=150) 
    middle_name = models.CharField(_("Middle Name"), max_length=150) 
    last_name = models.CharField(_("Last Name"), max_length=150) 
    id_no = models.PositiveBigIntegerField(_("id Number"),unique=True)
    AccountStatus = models.CharField(max_length=20,choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    role = models.CharField(max_length=20,choices=RoleChoice.choices, default=RoleChoice.CUSTOMER)
    failed_login_attempts = models.PositiveIntegerField(_("Failed Login Attempts"), default=0)
    last_failed_login = models.DateTimeField(_("Last Failed Login"), null=True, blank=True)  
    otp = models.CharField(_("otp"), max_length=6) 
    otp_expiry_time = models.DateTimeField(_("Otp Expiry Time"), null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name","last_name","id_no","security_answer","security_question"]

    def set_otp(self,otp:str)->None:
        self.otp = otp
        self.otp_expiry_time = timezone.now() + timezone.timedelta(minutes=settings.OTP_EXPIRATION)
        self.save()
    def verify_otp(self,otp:str)->bool:
        if self.otp == otp and self.otp_expiry_time > timezone.now():
            self.otp =""
            self.otp_expiry_time = None
            self.save()
            return True
        else:
            return False
    def handle_failed_login_attempts(self)-> None:
        self.failed_login_attempts +=1
        self.last_failed_login = timezone.now()
        if self.failed_login_attempts >= settings.LOGIN_ATTEMPTS:
            self.AccountStatus = self.AccountStatus.LOCKED
            self.save()
            send_account_locked_email(self)
        else:
            self.save()
    def rest_failed_login_attempts(self)->None:
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.AccountStatus = self.AccountStatus.ACTIVE
        self.save()
    def unlock_account(self)->None:
        if  self.AccountStatus == self.AccountStatus.LOCKED:
            self.AccountStatus = self.AccountStatus.ACTIVE
            self.failed_login_attempts = 0
            self.last_failed_login = None
            self.save()
    @property
    def is_locked(self)->bool:
        if self.AccountStatus == self.AccountStatus.LOCKED:
            if self.last_failed_login and (timezone.now()-self.last_failed_login)> settings.LOCKOUT_DURATION:
                self.unlock_account()
            return False
        return True
    @property
    def full_name(self)->str:
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.title().strip()
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]  
    def has_role(self, *role)-> bool:
        return hasattr(self, "role") and self.role in role 
    
    def save(self, *args, **kwargs):
        if not self.username:
            from .mangers import generate_username
            self.username = generate_username()
        super().save(*args, **kwargs)

    def __str__(self)-> str:
        return f"{self.full_name} - {self.role}"

        
    
    

    

    
        

    