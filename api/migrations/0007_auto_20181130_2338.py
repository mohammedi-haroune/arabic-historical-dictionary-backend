# Generated by Django 2.1.2 on 2018-11-30 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20181130_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='birth_date',
            field=models.CharField(default='غير معروف', max_length=255),
        ),
        migrations.AddField(
            model_name='document',
            name='death_date',
            field=models.CharField(default='غير معروف', max_length=255),
        ),
    ]
