# Generated by Django 2.1.2 on 2018-11-30 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'ordering': ('term',)},
        ),
        migrations.RemoveField(
            model_name='period',
            name='end',
        ),
        migrations.RemoveField(
            model_name='period',
            name='start',
        ),
        migrations.AddField(
            model_name='period',
            name='description',
            field=models.CharField(default='لا توجد', max_length=255),
        ),
        migrations.AlterField(
            model_name='period',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]