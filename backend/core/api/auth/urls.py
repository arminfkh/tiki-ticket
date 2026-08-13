from django.urls import path

from .login.views import login_with_otp, login_with_password, request_login_otp
from .signup.views import signup, verify_signup

app_name = "auth"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("signup/verify/", verify_signup, name="signup-verify"),
    path("login/", login_with_password, name="login-with-password"),
    path("login/otp/request/", request_login_otp, name="login-otp-request"),
    path("login/otp/verify/", login_with_otp, name="login-with-otp"),
]
