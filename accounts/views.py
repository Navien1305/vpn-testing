from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.views.decorators.csrf import requires_csrf_token

from .decorators import admin_required
from .forms import LoginForm, RegistrationForm, UserApprovalForm
from .models import User


REGISTRATION_SENT_MESSAGE = "Регистрация отправлена. Дождитесь подтверждения администратора."


def add_message_once(request, level, text):
    existing_messages = list(get_messages(request))
    for item in existing_messages:
        if str(item) != text:
            messages.add_message(request, item.level, str(item), extra_tags=item.extra_tags)
    messages.add_message(request, level, text)


def login_view(request):
    if request.user.is_authenticated:
        if not request.user.is_approved and not request.user.is_superuser:
            return redirect("approval_pending")
        return redirect("dashboard")

    redirect_to = request.POST.get("next") or request.GET.get("next") or resolve_url("dashboard")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not user.is_approved and not user.is_superuser:
                return redirect("approval_pending")
            return redirect(redirect_to)
    else:
        form = LoginForm(request)
    return render(request, "registration/login.html", {"form": form, "next": redirect_to})


@requires_csrf_token
def csrf_failure(request, reason=""):
    if request.user.is_authenticated:
        if not request.user.is_approved and not request.user.is_superuser:
            messages.warning(request, "Ваш аккаунт ожидает подтверждения администратором.")
            return redirect("approval_pending")
        messages.warning(request, "Сессия формы устарела. Повторите действие.")
        return redirect("dashboard")

    messages.warning(request, "Сессия формы входа устарела. Откройте форму заново и повторите вход.")
    return redirect("login")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            add_message_once(request, messages.SUCCESS, REGISTRATION_SENT_MESSAGE)
            return redirect("login")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def approval_pending(request):
    if request.user.is_approved or request.user.is_superuser:
        return redirect("dashboard")
    return render(request, "accounts/approval_pending.html")


@admin_required
def user_list(request):
    users = User.objects.select_related("organization").order_by("is_approved", "username")
    return render(request, "accounts/user_list.html", {"users": users})


@admin_required
def approve_user(request, pk):
    user_obj = get_object_or_404(User.objects.select_related("organization"), pk=pk)
    if request.method == "POST":
        if request.POST.get("action") == "reject":
            user_obj.is_approved = False
            user_obj.is_active = False
            user_obj.save(update_fields=["is_approved", "is_active", "updated_at"])
            messages.warning(request, "Заявка пользователя отклонена.")
            return redirect("user_list")
        form = UserApprovalForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Пользователь обновлен.")
            return redirect("user_list")
    else:
        form = UserApprovalForm(instance=user_obj)
    return render(request, "accounts/approve_user.html", {"form": form, "user_obj": user_obj})


@admin_required
def delete_user(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj.pk == request.user.pk:
        messages.error(request, "Нельзя удалить текущего пользователя.")
        return redirect("user_list")
    if request.method == "POST":
        user_obj.delete()
        messages.warning(request, "Пользователь удален.")
        return redirect("user_list")
    return render(request, "accounts/delete_user.html", {"user_obj": user_obj})
