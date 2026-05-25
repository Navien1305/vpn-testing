from django.db import migrations, models
import django.db.models.deletion


def copy_existing_vpn_periods(apps, schema_editor):
    VpnApp = apps.get_model("references", "VpnApp")
    VpnAppPeriod = apps.get_model("references", "VpnAppPeriod")

    for app in VpnApp.objects.all():
        if not app.active_from or not app.active_to:
            continue
        VpnAppPeriod.objects.get_or_create(
            vpn_app=app,
            active_from=app.active_from,
            active_to=app.active_to,
            defaults={
                "is_active": app.is_active,
                "display_order": app.display_order,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("references", "0002_mobileoperator_cities"),
    ]

    operations = [
        migrations.CreateModel(
            name="VpnAppPeriod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
                ("active_from", models.DateField(verbose_name="Активно с")),
                ("active_to", models.DateField(verbose_name="Активно до")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активно")),
                ("display_order", models.PositiveIntegerField(default=100, verbose_name="Порядок отображения")),
                (
                    "vpn_app",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="periods",
                        to="references.vpnapp",
                        verbose_name="VPN-приложение",
                    ),
                ),
            ],
            options={
                "verbose_name": "VPN-приложение на период",
                "verbose_name_plural": "VPN-приложения на периоды",
                "ordering": ("active_from", "vpn_app__os", "display_order", "vpn_app__name"),
            },
        ),
        migrations.RunPython(copy_existing_vpn_periods, migrations.RunPython.noop),
        migrations.RemoveField(model_name="vpnapp", name="active_from"),
        migrations.RemoveField(model_name="vpnapp", name="active_to"),
        migrations.RemoveField(model_name="vpnapp", name="display_order"),
        migrations.RemoveField(model_name="vpnapp", name="is_active"),
        migrations.AddConstraint(
            model_name="vpnappperiod",
            constraint=models.UniqueConstraint(fields=("vpn_app", "active_from", "active_to"), name="unique_vpn_app_period"),
        ),
        migrations.AlterModelOptions(
            name="vpnapp",
            options={"ordering": ("os", "name"), "verbose_name": "VPN-приложение", "verbose_name_plural": "VPN-приложения"},
        ),
    ]
