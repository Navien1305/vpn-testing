from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import UserRole


def approved_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_approved or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return redirect("approval_pending")

    return wrapper


def role_required(*roles):
    def decorator(view_func):
        @approved_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return wrapper

    return decorator


admin_required = role_required(UserRole.ADMIN)
