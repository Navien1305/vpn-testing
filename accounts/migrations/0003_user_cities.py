from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_validate_contact"),
        ("references", "0005_deduplicate_organizations"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="cities",
            field=models.ManyToManyField(blank=True, related_name="users", to="references.city", verbose_name="Города"),
        ),
    ]
