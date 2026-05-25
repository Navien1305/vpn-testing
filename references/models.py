from django.db import models


class OrganizationType(models.TextChoices):
    UNIVERSITY = "university", "Университет"
    MOBILE_OPERATOR = "mobile_operator", "Оператор связи"
    GRFC = "grfc", "ГРЧЦ"


class OperatingSystem(models.TextChoices):
    ANDROID = "Android", "Android"
    IOS = "iOS", "iOS"


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    class Meta:
        abstract = True


class City(models.Model):
    name = models.CharField("Название", max_length=120, unique=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "город"
        verbose_name_plural = "города"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Organization(TimeStampedModel):
    name = models.CharField("Название", max_length=255)
    type = models.CharField("Тип", max_length=30, choices=OrganizationType.choices, blank=True)
    city = models.ForeignKey(
        City,
        verbose_name="Город",
        on_delete=models.PROTECT,
        related_name="organizations",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "организация"
        verbose_name_plural = "организации"
        ordering = ("name",)

    def __str__(self):
        return self.name


class MobileOperator(models.Model):
    name = models.CharField("Название", max_length=120, unique=True)
    cities = models.ManyToManyField(City, verbose_name="Города", related_name="mobile_operators", blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "оператор связи"
        verbose_name_plural = "операторы связи"
        ordering = ("name",)

    def __str__(self):
        return self.name


class VpnApp(TimeStampedModel):
    name = models.CharField("Название", max_length=255)
    os = models.CharField("ОС", max_length=20, choices=OperatingSystem.choices)
    package_id = models.CharField("Package ID", max_length=255, blank=True)
    store_url = models.URLField("Ссылка в сторе", blank=True)

    class Meta:
        verbose_name = "VPN-приложение"
        verbose_name_plural = "VPN-приложения"
        ordering = ("os", "name")

    def __str__(self):
        return f"{self.name} ({self.os})"


class VpnAppPeriod(TimeStampedModel):
    vpn_app = models.ForeignKey(VpnApp, verbose_name="VPN-приложение", on_delete=models.CASCADE, related_name="periods")
    active_from = models.DateField("Активно с")
    active_to = models.DateField("Активно до")
    source_tag = models.CharField("Признак", max_length=100, blank=True)
    is_active = models.BooleanField("Активно", default=True)
    display_order = models.PositiveIntegerField("Порядок отображения", default=100)

    class Meta:
        verbose_name = "VPN-приложение на период"
        verbose_name_plural = "VPN-приложения на периоды"
        ordering = ("active_from", "vpn_app__os", "display_order", "vpn_app__name")
        constraints = [
            models.UniqueConstraint(
                fields=("vpn_app", "active_from", "active_to"),
                name="unique_vpn_app_period",
            ),
        ]

    def __str__(self):
        return f"{self.vpn_app} {self.active_from:%d.%m.%Y}-{self.active_to:%d.%m.%Y}"


class Messenger(TimeStampedModel):
    name = models.CharField("Название", max_length=255, unique=True)
    is_active = models.BooleanField("Активен", default=True)
    display_order = models.PositiveIntegerField("Порядок отображения", default=100)

    class Meta:
        verbose_name = "мессенджер"
        verbose_name_plural = "мессенджеры"
        ordering = ("display_order", "name")

    def __str__(self):
        return self.name
