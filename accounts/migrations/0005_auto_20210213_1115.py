# Generated by Django 3.1.6 on 2021-02-13 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20210213_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounttransactions',
            name='transaction_type',
            field=models.CharField(choices=[('Deposit', 'Cr.'), ('Withdraw', 'Dr.')], max_length=200, null=True),
        ),
    ]
