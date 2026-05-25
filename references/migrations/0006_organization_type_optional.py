from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("references", "0005_deduplicate_organizations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organization",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("university", "Университет"),
                    ("mobile_operator", "Оператор связи"),
                    ("grfc", "ГРЧЦ"),
                ],
                max_length=30,
                verbose_name="Тип",
            ),
        ),
    ]
