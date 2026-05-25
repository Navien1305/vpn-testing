from django.urls import path

from . import views


urlpatterns = [
    path("forms/", views.vpn_form_list, name="vpn_form_list"),
    path("forms/create/", views.vpn_form_create, name="vpn_form_create"),
    path("forms/<int:pk>/", views.vpn_form_detail, name="vpn_form_detail"),
    path("forms/<int:pk>/delete/", views.vpn_form_delete, name="vpn_form_delete"),
    path("forms/<int:pk>/start/<int:number>/", views.vpn_measurement_start, name="vpn_measurement_start"),
    path("forms/<int:pk>/submit-single/", views.vpn_form_submit_single_measurement, name="vpn_form_submit_single"),
    path("forms/<int:pk>/review/", views.vpn_form_review, name="vpn_form_review"),
    path("forms/<int:pk>/confirm/", views.vpn_form_confirm, name="vpn_form_confirm"),
    path("forms/<int:pk>/return/", views.vpn_form_return, name="vpn_form_return"),
    path("measurements/<int:pk>/baseline/", views.vpn_measurement_baseline, name="vpn_measurement_baseline"),
    path("measurements/<int:pk>/fill/<int:result_id>/", views.vpn_measurement_fill, name="vpn_measurement_fill"),
    path("measurements/<int:pk>/complete/", views.vpn_measurement_complete, name="vpn_measurement_complete"),
    path("measurements/<int:pk>/summary/", views.vpn_measurement_summary, name="vpn_measurement_summary"),
    path("measurements/<int:pk>/submit/", views.vpn_measurement_submit, name="vpn_measurement_submit"),
    path("measurements/<int:pk>/confirm/", views.vpn_measurement_confirm, name="vpn_measurement_confirm"),
    path("measurements/<int:pk>/return/", views.vpn_measurement_return, name="vpn_measurement_return"),
    path("review/", views.vpn_review_list, name="vpn_review_list"),
]
