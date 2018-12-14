# Generated by Django 2.1.2 on 2018-12-11 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20181208_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='appears',
            name='word_position',
            field=models.BigIntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='corpus',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='corpus',
            name='path',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='appears',
            unique_together={('position', 'word_position', 'document')},
        ),
        migrations.AlterOrderWithRespectTo(
            name='document',
            order_with_respect_to=None,
        ),
    ]
