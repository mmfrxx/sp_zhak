# Generated by Django 3.1.2 on 2021-01-20 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_auto_20210120_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchases',
            name='purchase_status',
            field=models.CharField(choices=[('inProgress', 'In progress'), ('completed', 'Completed'), ('waitingForReturn', 'Applied for return')], default='inProgress', max_length=16),
        ),
    ]