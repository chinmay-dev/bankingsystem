# Generated by Django 3.1.6 on 2021-02-13 04:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_transactions'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.customer'),
        ),
    ]
