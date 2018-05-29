# Generated by Django 2.0.5 on 2018-05-27 16:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0003_auto_20180527_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notary',
            name='id',
            field=models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notary',
            name='license',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]