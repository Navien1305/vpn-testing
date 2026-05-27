from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaires", "0006_messenger_forms"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vpntestform",
            name="status",
            field=models.CharField(
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
    ]
