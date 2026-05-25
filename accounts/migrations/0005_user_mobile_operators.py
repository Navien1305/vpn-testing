from django.db import migrations, models


def copy_mobile_operator_to_many_to_many(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    through_model = User.mobile_operators.through
    rows = []
    for user in User.objects.exclude(mobile_operator_id=None).only("id", "mobile_operator_id"):
        rows.append(through_model(user_id=user.id, mobileoperator_id=user.mobile_operator_id))
    through_model.objects.bulk_create(rows, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_user_mobile_operator"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="mobile_operators",
            field=models.ManyToManyField(blank=True, related_name="users", to="references.mobileoperator", verbose_name="Операторы связи"),
        ),
        migrations.RunPython(copy_mobile_operator_to_many_to_many, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="user",
            name="mobile_operator",
        ),
    ]
