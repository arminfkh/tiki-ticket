from django.urls import path

from .views import submit_report

app_name = "reports"

urlpatterns = [path("", submit_report, name="report-submit")]
