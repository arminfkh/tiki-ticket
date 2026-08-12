from django.urls import path

from .views import login, request_otp, signup, verify_otp

app_name = "auth"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login, name="login"),
    path("otp/request/", request_otp, name="otp-request"),
    path("otp/verify/", verify_otp, name="otp-verify"),
]
