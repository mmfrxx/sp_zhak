# Generated by Django 3.1.2 on 2021-04-01 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_auto_20210120_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='purchases',
            name='purchase_status',
            field=models.CharField(choices=[('In Progress', 'In progress'), ('Complete', 'Complete'), ('For Return', 'For Return'), ('Returned', 'Returned'), ('In Cart', 'In Cart')], default='In progress', max_length=16),
        ),
    ]
