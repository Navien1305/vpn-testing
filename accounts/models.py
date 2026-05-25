from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models



class UserRole(models.TextChoices):
    TESTER = "tester", "Тестировщик"
    COORDINATOR = "coordinator", "Координатор организации"
    READER = "reader", "Читатель"
    ADMIN = "admin", "Администратор"


class UserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("full_name", username)
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_approved", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    full_name = models.CharField("ФИО", max_length=255)
    organization = models.ForeignKey(
        "references.Organization",
        verbose_name="Организация",
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )
    cities = models.ManyToManyField(
        "references.City",
        verbose_name="Города",
        related_name="users",
        blank=True,
    )
    mobile_operators = models.ManyToManyField(
        "references.MobileOperator",
        verbose_name="Операторы связи",
        related_name="users",
        blank=True,
    )
    contact = models.CharField("Контакт для связи", max_length=255, blank=True)
    role = models.CharField("Роль", max_length=20, choices=UserRole.choices, default=UserRole.TESTER)
    is_approved = models.BooleanField("Подтвержден администратором", default=False)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    objects = UserManager()

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.full_name or self.username

    @property
    def is_admin_role(self):
        return self.is_superuser or self.role == UserRole.ADMIN
