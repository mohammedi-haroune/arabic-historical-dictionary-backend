# Generated by Django 2.1.2 on 2018-12-11 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20181211_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appears',
            name='meaning',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Meaning'),
        ),
    ]
