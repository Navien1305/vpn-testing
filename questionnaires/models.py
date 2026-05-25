from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from references.models import City, MobileOperator, OperatingSystem, Organization, VpnApp


class VpnFormStatus(models.TextChoices):
    DRAFT = "draft", "Черновик"
    SUBMITTED = "submitted", "Отправлена"
    CONFIRMED = "confirmed", "Подтверждена"
    RETURNED = "returned", "Возвращена"


class MeasurementStatus(models.TextChoices):
    DRAFT = "draft", "Черновик"
    SUBMITTED = "submitted", "Отправлен"
    CONFIRMED = "confirmed", "Подтвержден"
    RETURNED = "returned", "Возвращен"


class CheckStatus(models.TextChoices):
    WORKS = "works", "Доступен"
    NOT_WORKS = "not_works", "Не доступен"
    UNABLE_TO_CHECK = "unable_to_check", "Невозможно проверить"
    NOT_APPLICABLE = "-", "-"


class TesterDevice(models.Model):
    tester = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Тестировщик", on_delete=models.CASCADE, related_name="vpn_devices")
    name = models.CharField("Устройство", max_length=255)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "устройство тестировщика"
        verbose_name_plural = "устройства тестировщиков"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(fields=("tester", "name"), name="unique_tester_device"),
        ]

    def __str__(self):
        return self.name


class VpnTestForm(models.Model):
    date = models.DateField("Дата тестирования", default=timezone.localdate)
    organization = models.ForeignKey(Organization, verbose_name="Организация", on_delete=models.PROTECT, related_name="vpn_forms")
    tester = models.CharField("Тестировщик", max_length=255)
    city = models.ForeignKey(City, verbose_name="Город", on_delete=models.PROTECT, related_name="vpn_forms")
    mobile_operator = models.ForeignKey(MobileOperator, verbose_name="Оператор связи", on_delete=models.PROTECT, related_name="vpn_forms")
    os = models.CharField("ОС", max_length=20, choices=OperatingSystem.choices)
    device = models.CharField("Устройство", max_length=255)
    contact = models.CharField("Контакт", max_length=255)
    status = models.CharField("Статус", max_length=30, choices=VpnFormStatus.choices, default=VpnFormStatus.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Создал", on_delete=models.PROTECT, related_name="created_vpn_forms")
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Подтвердил",
        on_delete=models.PROTECT,
        related_name="confirmed_vpn_forms",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)
    submitted_at = models.DateTimeField("Отправлена", null=True, blank=True)
    confirmed_at = models.DateTimeField("Подтверждена", null=True, blank=True)

    class Meta:
        verbose_name = "VPN-анкета"
        verbose_name_plural = "VPN-анкеты"
        ordering = ("-date", "-created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("date", "organization", "city", "mobile_operator", "os"),
                name="unique_vpn_test_form",
            ),
        ]

    def __str__(self):
        return f"VPN {self.date:%d.%m.%Y} {self.organization} {self.city} {self.os}"


class VpnMeasurement(models.Model):
    class MeasurementNumber(models.IntegerChoices):
        FIRST = 1, "Первый замер"
        SECOND = 2, "Второй замер"

    form = models.ForeignKey(VpnTestForm, verbose_name="Анкета", on_delete=models.CASCADE, related_name="measurements")
    measurement_number = models.PositiveSmallIntegerField("Номер замера", choices=MeasurementNumber.choices)
    status = models.CharField("Статус", max_length=20, choices=MeasurementStatus.choices, default=MeasurementStatus.DRAFT)
    onelostbox_without_vpn_status = models.CharField(
        "onelostbox.com без VPN",
        max_length=30,
        choices=CheckStatus.choices,
        blank=True,
    )
    onelostbox_without_vpn_comment = models.TextField("Комментарий к onelostbox.com без VPN", blank=True)
    started_at = models.DateTimeField("Начат", default=timezone.now)
    submitted_at = models.DateTimeField("Отправлен", null=True, blank=True)
    confirmed_at = models.DateTimeField("Подтвержден", null=True, blank=True)
    returned_at = models.DateTimeField("Возвращен", null=True, blank=True)
    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Проверил",
        on_delete=models.PROTECT,
        related_name="checked_vpn_measurements",
        null=True,
        blank=True,
    )
    return_comment = models.TextField("Комментарий возврата", blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    class Meta:
        verbose_name = "замер VPN"
        verbose_name_plural = "замеры VPN"
        ordering = ("form", "measurement_number")
        constraints = [
            models.UniqueConstraint(fields=("form", "measurement_number"), name="unique_vpn_measurement_number"),
        ]

    def __str__(self):
        return f"{self.form} - {self.get_measurement_number_display()}"


class VpnMeasurementResult(models.Model):
    measurement = models.ForeignKey(VpnMeasurement, verbose_name="Замер", on_delete=models.CASCADE, related_name="results")
    vpn_app = models.ForeignKey(VpnApp, verbose_name="VPN-приложение", on_delete=models.PROTECT, related_name="measurement_results")
    vpn_unable_to_check = models.BooleanField("VPN невозможно проверить", default=False)
    web_without_vpn_status = models.CharField("onelostbox.com без VPN", max_length=30, choices=CheckStatus.choices, blank=True)
    web_with_vpn_status = models.CharField("onelostbox.com с VPN", max_length=30, choices=CheckStatus.choices, blank=True)
    instagram_status = models.CharField("Instagram", max_length=30, choices=CheckStatus.choices, blank=True)
    youtube_status = models.CharField("YouTube", max_length=30, choices=CheckStatus.choices, blank=True)
    comment = models.TextField("Комментарий", blank=True)
    measured_at = models.DateTimeField("Время замера", null=True, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    class Meta:
        verbose_name = "результат проверки VPN"
        verbose_name_plural = "результаты проверки VPN"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(fields=("measurement", "vpn_app"), name="unique_vpn_measurement_result"),
        ]

    def __str__(self):
        return f"{self.measurement}: {self.vpn_app}"

    def clean(self):
        if getattr(self, "_validated_by_result_form", False):
            return
        if self.vpn_unable_to_check:
            if not self.comment.strip():
                raise ValidationError("Если VPN невозможно проверить, комментарий обязателен.")
            return

        required_fields = [self.web_with_vpn_status, self.instagram_status, self.youtube_status]
        if any(not value for value in required_fields):
            raise ValidationError("Заполните все обязательные статусы проверки.")

    @property
    def is_filled(self):
        if self.vpn_unable_to_check:
            return bool(self.comment.strip())
        return all([self.web_with_vpn_status, self.instagram_status, self.youtube_status])

    def save(self, *args, **kwargs):
        if self.measured_at is None and any(
            [
                self.web_without_vpn_status,
                self.vpn_unable_to_check,
                self.web_with_vpn_status,
                self.instagram_status,
                self.youtube_status,
            ]
        ):
            self.measured_at = timezone.now()
        super().save(*args, **kwargs)
