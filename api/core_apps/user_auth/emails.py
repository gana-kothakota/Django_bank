from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from loguru import logger


def send_otp_email(email, otp):
    subject = _("your otp code for login")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_email = [email]

    context = {
        "otp": otp,
        "expiry_time": settings.OTP_EXPIRATION,
        "site_name": settings.SITE_NAME,
    }

    html_email = render_to_string("emails/otp_email.html", context)
    plain_email = strip_tags(html_email)

    msg = EmailMultiAlternatives(subject, plain_email, from_email, recipient_email)
    msg.attach_alternative(html_email, "text/html")

    try:
        msg.send()
        logger.info(f"Otp email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send otp email {email}: {str(e)}")


def send_account_locked_email(self):
    subject = _("your account has been locked")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_email = [self.email]

    lockout_duration = getattr(
        settings, "LOCKOUT_DURATION", getattr(settings, "lockout_duration", None)
    )
    if hasattr(lockout_duration, "total_seconds"):
        lockout_minutes = int(lockout_duration.total_seconds() // 60)
    else:
        lockout_minutes = int(lockout_duration) if lockout_duration else 1

    context = {
        "user": self,
        "lockout_duration": lockout_minutes,
        "site_name": settings.SITE_NAME,
    }

    html_content = render_to_string("emails/account_locked.html", context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_email)
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
        logger.info(f"account locked email sent to {self.email}")
    except Exception as e:
        logger.error(f"Failed to send account locked email {self.email}: {str(e)}")
