"""
given an email, OTP, and purpose, it chooses the appropriate subject/body
and uses Django SMTP to send the email.
It converts SMTP/network failures into your own EmailDeliveryError.
"""

from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail

from .otp_service import (
    OTP_PURPOSE_PASSWORD_RESET,
    OTP_PURPOSE_SIGNUP,
    OTP_PURPOSE_LOGIN,
)


class EmailDeliveryError(Exception):
    """
    Raised when an authentication email cannot be delivered.
    """


def send_otp_email(email: str, otp: str, purpose: str) -> None:
    if purpose == OTP_PURPOSE_SIGNUP:
        subject = "Verify your email"
        message = (
            f"Your signup verification code is: {otp}\n\n"
            f"This code expires in "
            f"{settings.OTP_TTL_SECONDS // 60} minutes."
        )

    elif purpose == OTP_PURPOSE_PASSWORD_RESET:
        subject = "Reset your password"
        message = (
            f"Your password reset code is: {otp}\n\n"
            f"This code expires in "
            f"{settings.OTP_TTL_SECONDS // 60} minutes."
        )

    elif purpose == OTP_PURPOSE_LOGIN:
        subject = "Your login verification code"

        message = (
            f"Your login verification code is: {otp}\n\n"
            f"This code expires in "
            f"{settings.OTP_TTL_SECONDS // 60} minutes."
        )

    else:
        raise ValueError("Unsupported OTP purpose.")

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

    except (SMTPException, OSError) as exc:
        raise EmailDeliveryError("The verification email could not be sent.") from exc
