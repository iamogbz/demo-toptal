# pylint: disable=F,I,E,R,C

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20180426_0357'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auth',
            old_name='scope',
            new_name='scopes',
        ),
    ]
