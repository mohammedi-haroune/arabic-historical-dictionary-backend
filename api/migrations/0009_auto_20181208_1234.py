# Generated by Django 2.1.2 on 2018-12-08 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20181206_2355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dictionary',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='meaning',
            unique_together={('posTag', 'entry')},
        ),
        migrations.AlterOrderWithRespectTo(
            name='document',
            order_with_respect_to='period',
        ),
        migrations.AlterOrderWithRespectTo(
            name='meaning',
            order_with_respect_to='posTag',
        ),
        migrations.AlterOrderWithRespectTo(
            name='period',
            order_with_respect_to='name',
        ),
    ]