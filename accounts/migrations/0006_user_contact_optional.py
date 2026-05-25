import accounts.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_user_mobile_operators"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="contact",
            field=models.CharField(
                blank=True,
                max_length=255,
                validators=[accounts.validators.validate_contact],
                verbose_name="Контакт для связи",
            ),
        ),
    ]
