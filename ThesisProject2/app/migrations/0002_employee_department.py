# Generated by Django 4.1.7 on 2023-05-06 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='department',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
