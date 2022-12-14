# Generated by Django 4.1 on 2022-10-04 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steam', '0002_item_max_profit_item_min_profit_alter_item_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='market_count',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='market_id',
            field=models.BigIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='market_min_price',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='market_position',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='market_profit',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='market_time',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
