from django.urls import path

from . import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("approval-pending/", views.approval_pending, name="approval_pending"),
    path("users/", views.user_list, name="user_list"),
    path("users/<int:pk>/approve/", views.approve_user, name="approve_user"),
    path("users/<int:pk>/delete/", views.delete_user, name="delete_user"),
]
