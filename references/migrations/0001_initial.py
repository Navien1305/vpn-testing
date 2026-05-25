from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="Название")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
            ],
            options={
                "verbose_name": "город",
                "verbose_name_plural": "города",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Messenger",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="Название")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("display_order", models.PositiveIntegerField(default=100, verbose_name="Порядок отображения")),
            ],
            options={
                "verbose_name": "мессенджер",
                "verbose_name_plural": "мессенджеры",
                "ordering": ("display_order", "name"),
            },
        ),
        migrations.CreateModel(
            name="MobileOperator",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="Название")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
            ],
            options={
                "verbose_name": "оператор связи",
                "verbose_name_plural": "операторы связи",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("university", "Университет"),
                            ("mobile_operator", "Оператор связи"),
                            ("grfc", "ГРЧЦ"),
                        ],
                        max_length=30,
                        verbose_name="Тип",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Активна")),
                (
                    "city",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="organizations",
                        to="references.city",
                        verbose_name="Город",
                    ),
                ),
            ],
            options={
                "verbose_name": "организация",
                "verbose_name_plural": "организации",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="VpnApp",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                ("os", models.CharField(choices=[("Android", "Android"), ("iOS", "iOS")], max_length=20, verbose_name="ОС")),
                ("package_id", models.CharField(blank=True, max_length=255, verbose_name="Package ID")),
                ("store_url", models.URLField(blank=True, verbose_name="Ссылка в сторе")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активно")),
                ("active_from", models.DateField(blank=True, null=True, verbose_name="Активно с")),
                ("active_to", models.DateField(blank=True, null=True, verbose_name="Активно до")),
                ("display_order", models.PositiveIntegerField(default=100, verbose_name="Порядок отображения")),
            ],
            options={
                "verbose_name": "VPN-приложение",
                "verbose_name_plural": "VPN-приложения",
                "ordering": ("display_order", "name"),
            },
        ),
    ]
