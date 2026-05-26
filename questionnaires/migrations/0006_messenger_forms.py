import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questionnaires", "0005_simplify_vpn_form_statuses"),
        ("references", "0006_organization_type_optional"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MessengerTestForm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(default=django.utils.timezone.localdate, verbose_name="Дата тестирования")),
                ("tester", models.CharField(max_length=255, verbose_name="Тестировщик")),
                ("os", models.CharField(choices=[("Android", "Android"), ("iOS", "iOS")], max_length=20, verbose_name="ОС")),
                ("device", models.CharField(max_length=255, verbose_name="Устройство")),
                ("contact", models.CharField(blank=True, max_length=255, verbose_name="Контакт")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Черновик"),
                            ("submitted", "Отправлена"),
                            ("confirmed", "Подтверждена"),
                            ("returned", "Возвращена"),
                        ],
                        default="draft",
                        max_length=30,
                        verbose_name="Статус",
                    ),
                ),
                ("return_comment", models.TextField(blank=True, verbose_name="Комментарий возврата")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлена")),
                ("submitted_at", models.DateTimeField(blank=True, null=True, verbose_name="Отправлена")),
                ("confirmed_at", models.DateTimeField(blank=True, null=True, verbose_name="Подтверждена")),
                ("returned_at", models.DateTimeField(blank=True, null=True, verbose_name="Возвращена")),
                ("city", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="messenger_forms", to="references.city", verbose_name="Город")),
                (
                    "confirmed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="confirmed_messenger_forms",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Подтвердил",
                    ),
                ),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_messenger_forms", to=settings.AUTH_USER_MODEL, verbose_name="Создал")),
                ("mobile_operator", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="messenger_forms", to="references.mobileoperator", verbose_name="Оператор связи")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="messenger_forms", to="references.organization", verbose_name="Организация")),
            ],
            options={
                "verbose_name": "анкета мессенджеров",
                "verbose_name_plural": "анкеты мессенджеров",
                "ordering": ("-date", "-created_at"),
            },
        ),
        migrations.CreateModel(
            name="MessengerTestResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("measured_at", models.DateTimeField(blank=True, null=True, verbose_name="Время замера")),
                (
                    "service_availability_status",
                    models.CharField(
                        blank=True,
                        choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")],
                        max_length=30,
                        verbose_name="Доступность сервиса",
                    ),
                ),
                (
                    "message_send_status",
                    models.CharField(
                        blank=True,
                        choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")],
                        max_length=30,
                        verbose_name="Отправка сообщения",
                    ),
                ),
                ("message_sent_at", models.TimeField(blank=True, null=True, verbose_name="Время отправки сообщения")),
                ("file_size_mb", models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name="Объем файла, МБ")),
                ("file_send_speed_sec", models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name="Скорость отправки файла, секунд")),
                (
                    "audio_call_status",
                    models.CharField(
                        blank=True,
                        choices=[("works", "Работает"), ("not_works", "Не работает"), ("unable_to_check", "Невозможно проверить")],
                        max_length=30,
                        verbose_name="Аудиозвонок",
                    ),
                ),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
                ("form", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="questionnaires.messengertestform", verbose_name="Анкета")),
                ("messenger", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="test_results", to="references.messenger", verbose_name="Мессенджер")),
            ],
            options={
                "verbose_name": "результат проверки мессенджера",
                "verbose_name_plural": "результаты проверки мессенджеров",
                "ordering": ("id",),
            },
        ),
        migrations.AddConstraint(
            model_name="messengertestform",
            constraint=models.UniqueConstraint(fields=("date", "organization", "city", "mobile_operator", "os"), name="unique_messenger_test_form"),
        ),
        migrations.AddConstraint(
            model_name="messengertestresult",
            constraint=models.UniqueConstraint(fields=("form", "messenger"), name="unique_messenger_test_result"),
        ),
    ]
