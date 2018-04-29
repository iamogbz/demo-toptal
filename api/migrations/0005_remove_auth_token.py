# pylint: disable=F,I,E,R,C

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auth_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auth',
            name='token',
        ),
    ]
