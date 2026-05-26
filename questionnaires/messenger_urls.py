from django.urls import path

from . import views


urlpatterns = [
    path("forms/", views.messenger_form_list, name="messenger_form_list"),
    path("forms/create/", views.messenger_form_create, name="messenger_form_create"),
    path("forms/from-vpn/<int:vpn_pk>/", views.messenger_form_create_from_vpn, name="messenger_form_create_from_vpn"),
    path("forms/<int:pk>/", views.messenger_form_detail, name="messenger_form_detail"),
    path("forms/<int:pk>/start/", views.messenger_form_start, name="messenger_form_start"),
    path("forms/<int:pk>/fill/<int:result_id>/", views.messenger_form_fill, name="messenger_form_fill"),
    path("forms/<int:pk>/complete/", views.messenger_form_complete, name="messenger_form_complete"),
    path("forms/<int:pk>/submit/", views.messenger_form_submit, name="messenger_form_submit"),
    path("forms/<int:pk>/review/", views.messenger_form_review, name="messenger_form_review"),
    path("forms/<int:pk>/confirm/", views.messenger_form_confirm, name="messenger_form_confirm"),
    path("forms/<int:pk>/return/", views.messenger_form_return, name="messenger_form_return"),
    path("review/", views.messenger_review_list, name="messenger_review_list"),
]
