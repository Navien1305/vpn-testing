import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0007_remove_contact_model_validator"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined"),
        ),
    ]
