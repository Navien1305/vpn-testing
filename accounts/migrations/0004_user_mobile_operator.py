from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_cities"),
        ("references", "0005_deduplicate_organizations"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="mobile_operator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="references.mobileoperator",
                verbose_name="Оператор связи",
            ),
        ),
    ]
