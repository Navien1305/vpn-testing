from django.urls import path

from . import views


urlpatterns = [
    path("", views.references_index, name="references_index"),
    path("organizations/", views.organization_list, name="organization_list"),
    path("organizations/create/", views.reference_create, {"reference_type": "organizations"}, name="organization_create"),
    path("organizations/<int:pk>/edit/", views.reference_update, {"reference_type": "organizations"}, name="organization_update"),
    path("cities/", views.city_list, name="city_list"),
    path("cities/create/", views.reference_create, {"reference_type": "cities"}, name="city_create"),
    path("cities/<int:pk>/edit/", views.reference_update, {"reference_type": "cities"}, name="city_update"),
    path("mobile-operators/", views.mobile_operator_list, name="mobile_operator_list"),
    path("mobile-operators/create/", views.reference_create, {"reference_type": "mobile-operators"}, name="mobile_operator_create"),
    path("mobile-operators/<int:pk>/edit/", views.reference_update, {"reference_type": "mobile-operators"}, name="mobile_operator_update"),
    path("vpn-apps/", views.vpn_app_list, name="vpn_app_list"),
    path("vpn-apps/import/", views.vpn_app_import, name="vpn_app_import"),
    path("vpn-apps/export/", views.vpn_app_export, name="vpn_app_export"),
    path("vpn-apps/delete-period/", views.vpn_period_delete, name="vpn_period_delete"),
    path("vpn-apps/create/", views.reference_create, {"reference_type": "vpn-apps"}, name="vpn_app_create"),
    path("vpn-apps/<int:pk>/edit/", views.reference_update, {"reference_type": "vpn-apps"}, name="vpn_app_update"),
    path("vpn-apps/<int:pk>/delete/", views.vpn_app_delete, name="vpn_app_delete"),
    path("messengers/", views.messenger_list, name="messenger_list"),
    path("messengers/create/", views.reference_create, {"reference_type": "messengers"}, name="messenger_create"),
    path("messengers/<int:pk>/edit/", views.reference_update, {"reference_type": "messengers"}, name="messenger_update"),
]
