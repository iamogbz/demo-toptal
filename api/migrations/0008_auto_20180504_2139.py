# pylint: disable=F,I,E,R,C

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20180504_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='length_distance',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='trip',
            name='length_time',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
