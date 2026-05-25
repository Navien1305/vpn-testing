from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("organization/", views.organization_dashboard, name="organization_dashboard"),
]
