# pylint: disable=F,I,E,R,C

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_remove_auth_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auth',
            name='scopes',
            field=models.ManyToManyField(related_name='auths', to='api.Scope'),
        ),
    ]
