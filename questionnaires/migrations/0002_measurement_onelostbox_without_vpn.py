from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questionnaires", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="vpnmeasurement",
            name="onelostbox_without_vpn_status",
            field=models.CharField(blank=True, choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="onelostbox.com без VPN"),
        ),
        migrations.AddField(
            model_name="vpnmeasurement",
            name="onelostbox_without_vpn_comment",
            field=models.TextField(blank=True, verbose_name="Комментарий к onelostbox.com без VPN"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="web_with_vpn_status",
            field=models.CharField(blank=True, choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="onelostbox.com с VPN"),
        ),
        migrations.AlterField(
            model_name="vpnmeasurementresult",
            name="web_without_vpn_status",
            field=models.CharField(blank=True, choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="onelostbox.com без VPN"),
        ),
    ]
