# pylint: disable=F,I,E,R,C

from django.conf import settings
import django.contrib.auth.models
from django.core import validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [("auth", "0009_alter_user_last_name_max_length")]

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "user_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("reset_code", models.TextField(null=True)),
            ],
            options={"permissions": (("manage_account", "Can manage account"),)},
            bases=("auth.user",),
            managers=[("objects", django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name="Auth",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.TextField(null=True)),
                ("active", models.BooleanField(default=False)),
                ("date_created", models.DateField(auto_now_add=True)),
                (
                    "owner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="authorities",
                        to="api.Account",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Scope",
            fields=[
                (
                    "permission_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="auth.Permission",
                    ),
                )
            ],
            bases=("auth.permission",),
            managers=[("objects", django.contrib.auth.models.PermissionManager())],
        ),
        migrations.CreateModel(
            name="Trip",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_created", models.DateField(auto_now_add=True)),
                (
                    "length_time",
                    models.PositiveIntegerField(
                        validators=[validators.MinValueValidator(0)]
                    ),
                ),
                (
                    "length_distance",
                    models.PositiveIntegerField(
                        default=0, validators=[validators.MinValueValidator(0)]
                    ),
                ),
                ("date_updated", models.DateField(auto_now=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trips",
                        to="api.Account",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="auth",
            name="scopes",
            field=models.ManyToManyField(related_name="auths", to="api.Scope"),
        ),
        migrations.AddField(
            model_name="auth",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="authorised",
                to="api.Account",
            ),
        ),
    ]
