from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("references", "0003_split_vpn_apps_by_period"),
    ]

    operations = [
        migrations.AddField(
            model_name="vpnappperiod",
            name="source_tag",
            field=models.CharField(blank=True, max_length=100, verbose_name="Признак"),
        ),
    ]
