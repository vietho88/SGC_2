# Generated by Django 3.0.8 on 2020-11-04 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Service', '0004_typeproduct_is_show'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
    ]
