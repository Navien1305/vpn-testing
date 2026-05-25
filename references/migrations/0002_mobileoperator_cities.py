from django.db import migrations, models


def assign_all_cities_to_existing_operators(apps, schema_editor):
    City = apps.get_model("references", "City")
    MobileOperator = apps.get_model("references", "MobileOperator")

    city_ids = list(City.objects.values_list("id", flat=True))
    for operator in MobileOperator.objects.all():
        operator.cities.set(city_ids)


class Migration(migrations.Migration):
    dependencies = [
        ("references", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="mobileoperator",
            name="cities",
            field=models.ManyToManyField(blank=True, related_name="mobile_operators", to="references.city", verbose_name="Города"),
        ),
        migrations.RunPython(assign_all_cities_to_existing_operators, migrations.RunPython.noop),
    ]
