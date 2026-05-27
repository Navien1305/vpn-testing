# Generated manually for export logs.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ExportLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                (
                    "export_type",
                    models.CharField(choices=[("excel", "Excel")], max_length=20, verbose_name="Тип экспорта"),
                ),
                ("date_from", models.DateField(blank=True, null=True, verbose_name="Дата с")),
                ("date_to", models.DateField(blank=True, null=True, verbose_name="Дата по")),
                ("filters_json", models.JSONField(blank=True, default=dict, verbose_name="Фильтры")),
                ("file_name", models.CharField(blank=True, max_length=255, verbose_name="Имя файла")),
                ("rows_vpn", models.PositiveIntegerField(default=0, verbose_name="Строк VPN")),
                ("rows_messenger", models.PositiveIntegerField(default=0, verbose_name="Строк мессенджеров")),
                (
                    "status",
                    models.CharField(
                        choices=[("success", "Успешно"), ("failed", "Ошибка")],
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                ("error_message", models.TextField(blank=True, verbose_name="Ошибка")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="export_logs",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "лог экспорта",
                "verbose_name_plural": "логи экспорта",
                "ordering": ("-created_at",),
            },
        ),
    ]
