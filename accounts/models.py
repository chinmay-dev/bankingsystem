from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.username


class AccountTransactions(models.Model):
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    amount = models.FloatField(null=True)
    TRANSACTION_CHOICES = (
        ('Deposit', 'Deposit'),
        ('Withdraw', 'Withdraw')
    )
    transaction_type = models.CharField(max_length=200, null=True, choices=TRANSACTION_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
