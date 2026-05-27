from django.conf import settings
from django.db import models


class ExportType(models.TextChoices):
    EXCEL = "excel", "Excel"


class ExportStatus(models.TextChoices):
    SUCCESS = "success", "Успешно"
    FAILED = "failed", "Ошибка"


class ExportLog(models.Model):
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.PROTECT,
        related_name="export_logs",
        null=True,
        blank=True,
    )
    export_type = models.CharField("Тип экспорта", max_length=20, choices=ExportType.choices)
    date_from = models.DateField("Дата с", null=True, blank=True)
    date_to = models.DateField("Дата по", null=True, blank=True)
    filters_json = models.JSONField("Фильтры", default=dict, blank=True)
    file_name = models.CharField("Имя файла", max_length=255, blank=True)
    rows_vpn = models.PositiveIntegerField("Строк VPN", default=0)
    rows_messenger = models.PositiveIntegerField("Строк мессенджеров", default=0)
    status = models.CharField("Статус", max_length=20, choices=ExportStatus.choices)
    error_message = models.TextField("Ошибка", blank=True)

    class Meta:
        verbose_name = "лог экспорта"
        verbose_name_plural = "логи экспорта"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.get_export_type_display()} {self.created_at:%d.%m.%Y %H:%M}"
