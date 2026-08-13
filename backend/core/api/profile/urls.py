from django.urls import path

from .views import update_user_profile

app_name = "profile"

urlpatterns = [path("", update_user_profile, name="profile-update")]
