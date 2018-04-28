# pylint: disable=F,I,E,R,C

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20180428_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='auth',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
