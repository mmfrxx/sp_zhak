# Generated by Django 3.1.2 on 2021-04-28 13:32

from django.db import migrations, models
import django_s3_storage.storage


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='photo',
            field=models.ImageField(null=True, storage=django_s3_storage.storage.S3Storage(aws_s3_bucket_name='seniorp'), upload_to=''),
        ),
    ]