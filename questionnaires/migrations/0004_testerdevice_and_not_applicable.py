import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("questionnaires", "0003_result_vpn_unable_and_labels"),
    ]

    operations = [
        migrations.CreateModel(
            name="TesterDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Устройство")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                ("tester", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vpn_devices", to=settings.AUTH_USER_MODEL, verbose_name="Тестировщик")),
            ],
            options={
                "verbose_name": "устройство тестировщика",
                "verbose_name_plural": "устройства тестировщиков",
                "ordering": ("name",),
            },
        ),
        migrations.AlterField(
            model_name="vpnmeasurement",
            name="onelostbox_without_vpn_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить"), ("-", "-")], max_length=30, verbose_name="onelostbox.com без VPN"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="instagram_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить"), ("-", "-")], max_length=30, verbose_name="Instagram"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="web_with_vpn_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить"), ("-", "-")], max_length=30, verbose_name="onelostbox.com с VPN"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="web_without_vpn_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить"), ("-", "-")], max_length=30, verbose_name="onelostbox.com без VPN"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="youtube_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить"), ("-", "-")], max_length=30, verbose_name="YouTube"),
        ),
        migrations.AddConstraint(
            model_name="testerdevice",
            constraint=models.UniqueConstraint(fields=("tester", "name"), name="unique_tester_device"),
        ),
    ]
