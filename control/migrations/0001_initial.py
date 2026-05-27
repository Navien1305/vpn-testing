from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("references", "0008_organization_linked_mobile_operator"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyFormPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(verbose_name="Дата")),
                (
                    "form_type",
                    models.CharField(
                        choices=[("vpn", "VPN"), ("messenger", "Мессенджеры")],
                        max_length=20,
                        verbose_name="Тип анкеты",
                    ),
                ),
                (
                    "os",
                    models.CharField(
                        choices=[("Android", "Android"), ("iOS", "iOS")],
                        max_length=20,
                        verbose_name="ОС",
                    ),
                ),
                ("expected", models.BooleanField(default=True, verbose_name="Ожидается")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="daily_form_plans",
                        to="references.city",
                        verbose_name="Город",
                    ),
                ),
                (
                    "mobile_operator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="daily_form_plans",
                        to="references.mobileoperator",
                        verbose_name="Оператор / сим-карта",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="daily_form_plans",
                        to="references.organization",
                        verbose_name="Организация",
                    ),
                ),
            ],
            options={
                "verbose_name": "плановая анкета",
                "verbose_name_plural": "плановые анкеты",
                "ordering": (
                    "date",
                    "form_type",
                    "organization__name",
                    "city__name",
                    "mobile_operator__name",
                    "os",
                ),
            },
        ),
        migrations.AddConstraint(
            model_name="dailyformplan",
            constraint=models.UniqueConstraint(
                fields=("date", "form_type", "organization", "city", "mobile_operator", "os"),
                name="unique_daily_form_plan",
            ),
        ),
    ]
