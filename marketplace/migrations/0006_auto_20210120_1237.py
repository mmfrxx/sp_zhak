# Generated by Django 3.1.2 on 2021-01-20 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0005_purchases_purchase_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchases',
            name='purchase_status',
            field=models.CharField(choices=[('inProgress', 'In progress'), ('completed', 'Completed'), ('return', 'Applied for return'), ('returnCompleted', 'Returned')], default='In progress', max_length=16),
        ),
    ]