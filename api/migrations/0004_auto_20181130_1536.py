# Generated by Django 2.1.2 on 2018-11-30 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20181130_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='author',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='category',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='description',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]