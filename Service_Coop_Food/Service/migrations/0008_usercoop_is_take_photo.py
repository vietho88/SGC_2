# Generated by Django 3.0.8 on 2020-11-27 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0007_permission_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercoop',
            name='is_take_photo',
            field=models.BooleanField(default=True, null=True),
        ),
    ]
