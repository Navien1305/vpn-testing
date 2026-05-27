from django.db import migrations, models
import django.db.models.deletion


def link_operator_organizations(apps, schema_editor):
    Organization = apps.get_model("references", "Organization")
    MobileOperator = apps.get_model("references", "MobileOperator")

    links = {
        "МТС": "МТС",
        "МегаФон": "МегаФон",
        "Билайн": "Билайн",
    }
    for organization_name, operator_name in links.items():
        operator = MobileOperator.objects.filter(name=operator_name).first()
        if operator:
            Organization.objects.filter(name=organization_name).update(linked_mobile_operator=operator)


class Migration(migrations.Migration):

    dependencies = [
        ("references", "0007_vpnapp_store_url_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="linked_mobile_operator",
            field=models.ForeignKey(
                blank=True,
                help_text="Используется для организаций-операторов при генерации ежедневного плана.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="linked_organizations",
                to="references.mobileoperator",
                verbose_name="Связанная сим-карта",
            ),
        ),
        migrations.RunPython(link_operator_organizations, migrations.RunPython.noop),
    ]
