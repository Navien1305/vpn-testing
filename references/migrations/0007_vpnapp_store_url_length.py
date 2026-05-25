from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("references", "0006_organization_type_optional"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vpnapp",
            name="store_url",
            field=models.URLField(blank=True, max_length=1000, verbose_name="Ссылка в сторе"),
        ),
    ]
