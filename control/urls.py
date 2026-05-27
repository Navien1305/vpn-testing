from django.urls import path

from . import views
from exports import views as export_views


urlpatterns = [
    path("", views.control_index, name="control_index"),
    path("<str:date_value>/export/", export_views.export_excel_from_control, name="control_export_excel"),
    path("<str:date_value>/", views.control_detail, name="control_detail"),
    path("<str:date_value>/generate/", views.control_generate, name="control_generate"),
    path("<str:date_value>/missing/", views.control_detail, {"status_key": "missing"}, name="control_missing"),
    path("<str:date_value>/drafts/", views.control_detail, {"status_key": "drafts"}, name="control_drafts"),
    path("<str:date_value>/submitted/", views.control_detail, {"status_key": "submitted"}, name="control_submitted"),
    path("<str:date_value>/confirmed/", views.control_detail, {"status_key": "confirmed"}, name="control_confirmed"),
    path("<str:date_value>/returned/", views.control_detail, {"status_key": "returned"}, name="control_returned"),
]
