from django.shortcuts import render

from accounts.decorators import approved_required, role_required
from accounts.models import UserRole


def home(request):
    return render(request, "core/home.html")


@approved_required
def dashboard(request):
    return render(request, "core/dashboard.html")


@role_required(UserRole.COORDINATOR, UserRole.ADMIN)
def organization_dashboard(request):
    return render(request, "core/organization_dashboard.html")
