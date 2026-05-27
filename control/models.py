from django.db import models

from references.models import City, MobileOperator, OperatingSystem, Organization


class DailyFormType(models.TextChoices):
    VPN = "vpn", "VPN"
    MESSENGER = "messenger", "Мессенджеры"


class DailyFormPlan(models.Model):
    date = models.DateField("Дата")
    form_type = models.CharField("Тип анкеты", max_length=20, choices=DailyFormType.choices)
    organization = models.ForeignKey(
        Organization,
        verbose_name="Организация",
        on_delete=models.PROTECT,
        related_name="daily_form_plans",
    )
    city = models.ForeignKey(
        City,
        verbose_name="Город",
        on_delete=models.PROTECT,
        related_name="daily_form_plans",
    )
    mobile_operator = models.ForeignKey(
        MobileOperator,
        verbose_name="Оператор / сим-карта",
        on_delete=models.PROTECT,
        related_name="daily_form_plans",
    )
    os = models.CharField("ОС", max_length=20, choices=OperatingSystem.choices)
    expected = models.BooleanField("Ожидается", default=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    class Meta:
        verbose_name = "плановая анкета"
        verbose_name_plural = "плановые анкеты"
        ordering = ("date", "form_type", "organization__name", "city__name", "mobile_operator__name", "os")
        constraints = [
            models.UniqueConstraint(
                fields=("date", "form_type", "organization", "city", "mobile_operator", "os"),
                name="unique_daily_form_plan",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_form_type_display()} {self.date:%d.%m.%Y}: "
            f"{self.organization} / {self.city} / {self.mobile_operator} / {self.os}"
        )
