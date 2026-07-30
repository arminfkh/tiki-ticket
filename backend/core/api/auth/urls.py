from django.urls import path

from .views import signup

app_name = "auth"

urlpatterns = [
    path("signup/", signup, name="signup"),
]
