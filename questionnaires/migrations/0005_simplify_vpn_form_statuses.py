from django.db import migrations, models


def move_partially_submitted_to_submitted(apps, schema_editor):
    VpnTestForm = apps.get_model("questionnaires", "VpnTestForm")
    VpnTestForm.objects.filter(status="partially_submitted").update(status="submitted")


class Migration(migrations.Migration):
    dependencies = [
        ("questionnaires", "0004_testerdevice_and_not_applicable"),
    ]

    operations = [
        migrations.RunPython(move_partially_submitted_to_submitted, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="vpntestform",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Черновик"),
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
