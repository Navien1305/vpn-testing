from django.db import migrations


def fill_planning_metadata(apps, schema_editor):
    City = apps.get_model("references", "City")
    MobileOperator = apps.get_model("references", "MobileOperator")
    Organization = apps.get_model("references", "Organization")

    city_by_name = {city.name: city for city in City.objects.all()}
    operator_by_name = {operator.name: operator for operator in MobileOperator.objects.all()}

    university_cities = {
        "МТУСИ": "Москва",
        "ПГУТИ": "Самара",
        "СПбГУТ": "Санкт-Петербург",
        "СибГУТИ": "Новосибирск",
    }
    for organization_name, city_name in university_cities.items():
        city = city_by_name.get(city_name)
        if city:
            Organization.objects.filter(name=organization_name).update(city=city)

    operator_links = {
        "МТС": "МТС",
        "МегаФон": "МегаФон",
        "Билайн": "Билайн",
    }
    default_city = city_by_name.get("Москва")
    for organization_name, operator_name in operator_links.items():
        operator = operator_by_name.get(operator_name)
        updates = {}
        if default_city:
            updates["city"] = default_city
        if operator:
            updates["linked_mobile_operator"] = operator
        if updates:
            Organization.objects.filter(name=organization_name).update(**updates)


class Migration(migrations.Migration):

    dependencies = [
        ("references", "0008_organization_linked_mobile_operator"),
    ]

    operations = [
        migrations.RunPython(fill_planning_metadata, migrations.RunPython.noop),
    ]
