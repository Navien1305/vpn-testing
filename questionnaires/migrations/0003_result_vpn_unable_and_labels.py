from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questionnaires", "0002_measurement_onelostbox_without_vpn"),
    ]

    operations = [
        migrations.AddField(
            model_name="vpnmeasurementresult",
            name="vpn_unable_to_check",
            field=models.BooleanField(default=False, verbose_name="VPN невозможно проверить"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurement",
            name="onelostbox_without_vpn_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="onelostbox.com без VPN"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="instagram_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="Instagram"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="web_with_vpn_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="onelostbox.com с VPN"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="web_without_vpn_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="onelostbox.com без VPN"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="youtube_status",
            field=models.CharField(blank=True, choices=[("works", "Доступен"), ("not_works", "Не доступен"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="YouTube"),
        ),
    ]
