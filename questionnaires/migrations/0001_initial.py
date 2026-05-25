import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("references", "0005_deduplicate_organizations"),
    ]

    operations = [
        migrations.CreateModel(
            name="VpnTestForm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(default=django.utils.timezone.localdate, verbose_name="Дата тестирования")),
                ("tester", models.CharField(max_length=255, verbose_name="Тестировщик")),
                ("os", models.CharField(choices=[("Android", "Android"), ("iOS", "iOS")], max_length=20, verbose_name="ОС")),
                ("device", models.CharField(max_length=255, verbose_name="Устройство")),
                ("contact", models.CharField(max_length=255, verbose_name="Контакт")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Черновик"),
                            ("partially_submitted", "Частично отправлена"),
                            ("submitted", "Отправлена"),
                            ("confirmed", "Подтверждена"),
                            ("returned", "Возвращена"),
                        ],
                        default="draft",
                        max_length=30,
                        verbose_name="Статус",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлена")),
                ("submitted_at", models.DateTimeField(blank=True, null=True, verbose_name="Отправлена")),
                ("confirmed_at", models.DateTimeField(blank=True, null=True, verbose_name="Подтверждена")),
                ("city", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vpn_forms", to="references.city", verbose_name="Город")),
                ("confirmed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="confirmed_vpn_forms", to=settings.AUTH_USER_MODEL, verbose_name="Подтвердил")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_vpn_forms", to=settings.AUTH_USER_MODEL, verbose_name="Создал")),
                ("mobile_operator", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vpn_forms", to="references.mobileoperator", verbose_name="Оператор связи")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vpn_forms", to="references.organization", verbose_name="Организация")),
            ],
            options={
                "verbose_name": "VPN-анкета",
                "verbose_name_plural": "VPN-анкеты",
                "ordering": ("-date", "-created_at"),
            },
        ),
        migrations.CreateModel(
            name="VpnMeasurement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("measurement_number", models.PositiveSmallIntegerField(choices=[(1, "Первый замер"), (2, "Второй замер")], verbose_name="Номер замера")),
                ("status", models.CharField(choices=[("draft", "Черновик"), ("submitted", "Отправлен"), ("confirmed", "Подтвержден"), ("returned", "Возвращен")], default="draft", max_length=20, verbose_name="Статус")),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Начат")),
                ("submitted_at", models.DateTimeField(blank=True, null=True, verbose_name="Отправлен")),
                ("confirmed_at", models.DateTimeField(blank=True, null=True, verbose_name="Подтвержден")),
                ("returned_at", models.DateTimeField(blank=True, null=True, verbose_name="Возвращен")),
                ("return_comment", models.TextField(blank=True, verbose_name="Комментарий возврата")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
                ("checked_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="checked_vpn_measurements", to=settings.AUTH_USER_MODEL, verbose_name="Проверил")),
                ("form", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="measurements", to="questionnaires.vpntestform", verbose_name="Анкета")),
            ],
            options={
                "verbose_name": "замер VPN",
                "verbose_name_plural": "замеры VPN",
                "ordering": ("form", "measurement_number"),
            },
        ),
        migrations.CreateModel(
            name="VpnMeasurementResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("web_without_vpn_status", models.CharField(blank=True, choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="Web без VPN")),
                ("web_with_vpn_status", models.CharField(blank=True, choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="Web через VPN")),
                ("instagram_status", models.CharField(blank=True, choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="Instagram")),
                ("youtube_status", models.CharField(blank=True, choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")], max_length=30, verbose_name="YouTube")),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
                ("measured_at", models.DateTimeField(blank=True, null=True, verbose_name="Время замера")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
                ("measurement", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="questionnaires.vpnmeasurement", verbose_name="Замер")),
                ("vpn_app", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="measurement_results", to="references.vpnapp", verbose_name="VPN-приложение")),
            ],
            options={
                "verbose_name": "результат проверки VPN",
                "verbose_name_plural": "результаты проверки VPN",
                "ordering": ("id",),
            },
        ),
        migrations.AddConstraint(
            model_name="vpntestform",
            constraint=models.UniqueConstraint(fields=("date", "organization", "city", "mobile_operator", "os"), name="unique_vpn_test_form"),
        ),
        migrations.AddConstraint(
            model_name="vpnmeasurement",
            constraint=models.UniqueConstraint(fields=("form", "measurement_number"), name="unique_vpn_measurement_number"),
        ),
        migrations.AddConstraint(
            model_name="vpnmeasurementresult",
            constraint=models.UniqueConstraint(fields=("measurement", "vpn_app"), name="unique_vpn_measurement_result"),
        ),
    ]
