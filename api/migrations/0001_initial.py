# Generated by Django 2.0.3 on 2018-04-25 03:58

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('reset_code', models.TextField()),
            ],
            options={
                'permissions': (('view_account', 'Can view account'), ('manage_account', 'Can manage account')),
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Auth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField()),
                ('code', models.TextField(null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owner', to='api.Account')),
            ],
            options={
                'permissions': (('view_auth', 'Can view auth'),),
            },
        ),
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('permission_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.Permission')),
                ('includes', models.ManyToManyField(blank=True, to='api.Scope')),
            ],
            options={
                'permissions': (('view_scope', 'Can view scope'),),
            },
            bases=('auth.permission',),
            managers=[
                ('objects', django.contrib.auth.models.PermissionManager()),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(auto_now_add=True)),
                ('length_time', models.PositiveIntegerField()),
                ('length_distance', models.PositiveIntegerField()),
                ('date_updated', models.DateField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Account')),
            ],
            options={
                'permissions': (('view_trip', 'Can view trip'),),
            },
        ),
        migrations.AddField(
            model_name='auth',
            name='scope',
            field=models.ManyToManyField(to='api.Scope'),
        ),
        migrations.AddField(
            model_name='auth',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to='api.Account'),
        ),
    ]
