from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_user_contact_optional"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="contact",
            field=models.CharField(blank=True, max_length=255, verbose_name="Контакт для связи"),
        ),
    ]
