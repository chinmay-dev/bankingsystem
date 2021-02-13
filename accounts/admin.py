from django.contrib import admin

from .models import Customer, AccountTransactions

admin.site.register(Customer)
admin.site.register(AccountTransactions)
