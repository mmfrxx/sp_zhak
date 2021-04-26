# Generated by Django 3.1.2 on 2021-01-17 14:40

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sizes_available',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('xs', 'XS'), ('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL')], default='xs', max_length=12),
        ),
    ]
