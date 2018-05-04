# pylint: disable=F,I,E,R,C

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20180429_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trips', to='api.Account'),
        ),
    ]
