# pylint: disable=F,I,E,R,C

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='reset_code',
            field=models.TextField(null=True),
        ),
    ]
