# Generated by Django 3.1.2 on 2021-02-07 18:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('description', models.CharField(db_index=True, max_length=255)),
                ('category', models.CharField(max_length=255)),
                ('photo', models.ImageField(blank=True, help_text='Upload your photo for Product', null=True, upload_to='')),
                ('price', models.IntegerField(default=0)),
                ('sizes_available', multiselectfield.db.fields.MultiSelectField(choices=[('xs', 'XS'), ('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL')], max_length=12, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Purchases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chosen_size', models.CharField(max_length=255, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('purchase_status', models.CharField(choices=[('inProgress', 'In progress'), ('completed', 'Completed'), ('return', 'Applied for return'), ('returnCompleted', 'Returned')], default='In progress', max_length=16)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
