import accounts.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="contact",
            field=models.CharField(max_length=255, validators=[accounts.validators.validate_contact], verbose_name="Контакт для связи"),
        ),
    ]
