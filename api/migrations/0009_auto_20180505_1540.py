# pylint: disable=F,I,E,R,C

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20180504_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auth',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authorities', to='api.Account'),
        ),
        migrations.AlterField(
            model_name='auth',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authorised', to='api.Account'),
        ),
    ]
