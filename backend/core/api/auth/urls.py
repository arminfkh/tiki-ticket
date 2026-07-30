from django.urls import path

from .views import signup, request_otp, verify_otp

app_name = "auth"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("otp/request/", request_otp, name="otp-request"),
    path("otp/verify/", verify_otp, name="otp-verify"),
]
