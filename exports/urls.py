from django.urls import path

from . import views


urlpatterns = [
    path("", views.export_index, name="export_index"),
    path("excel/", views.export_excel, name="export_excel"),
]
