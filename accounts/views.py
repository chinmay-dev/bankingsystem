from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
import datetime
from django_pandas.io import read_frame
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from django.core.mail import send_mail

from .decorators import unauthenticated_user, allowed_users, admin_only
from .models import *
from .forms import AccountTransactionsForm, CreateUserForm


@login_required(login_url='login')
@admin_only
def home(request):
    customers = Customer.objects.all()
    return render(request, 'accounts/dashboard.html', {'customers': customers})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def manager(request, pk):
    if request.method == 'GET' and request.GET.get('start_date') is not None:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        end_date = end_date + datetime.timedelta(days=1)
        customer_id = request.GET.get('customer_id')
        queryset = AccountTransactions.objects.filter(customer__id=customer_id).filter(date_created__range=[start_date, end_date]).order_by('date_created')
        if queryset:
            customer_name = queryset[0].customer.name
            df = read_frame(queryset, fieldnames=['date_created', 'amount', 'transaction_type'])
            df.rename(columns={'date_created': 'Transaction date', 'amount': 'Amount', 'transaction_type': 'Transaction type'}, inplace=True)
            df['Amount'] = df['Amount'].abs()
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Transactions', index=False)
                writer.save()
                response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename="' + customer_name + '(' + start_date + '_to_' + request.GET.get('end_date') + ')' + '.xls"'
                return response
        else:
            messages.info(request, 'No transactions to download')
    context = {'customer_id': pk}
    return render(request, 'accounts/manager.html', context)


def get_account_balance(customer):
    return AccountTransactions.objects.filter(customer=customer).aggregate(Sum('amount'))


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    transactions = customer.accounttransactions_set.all()
    account_balance = get_account_balance(pk)
    context = {'customer': customer, 'transactions': transactions, 'account_balance': account_balance}
    return render(request, 'accounts/enquiry.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def transact(request, pk):
    customer = Customer.objects.get(id=pk)
    account_balance = get_account_balance(pk)
    form = AccountTransactionsForm(initial={'customer': customer})
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        amount = request.POST.get('amount')
        if transaction_type == 'Withdraw' and account_balance['amount__sum'] and float(amount) < account_balance['amount__sum']:
            _mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['amount'] = -float(request.POST['amount'])
            request.POST._mutable = _mutable
            form = AccountTransactionsForm(request.POST)
            if form.is_valid():
                form.save()
                form = AccountTransactionsForm(initial={'customer': customer})
                account_balance = get_account_balance(pk)
                # Uncomment below code to start emails. Also add valid Sendgrid API key in settings.py and valid from email
                # mail_body = 'Your account is debited with Rs. ' + amount
                # send_mail(
                #     'Transaction Alert',
                #     mail_body,
                #     'from@example.com',
                #     [customer.email],
                #     fail_silently=False,
                # )
        elif transaction_type == 'Deposit':
            form = AccountTransactionsForm(request.POST)
            if form.is_valid():
                form.save()
                form = AccountTransactionsForm(initial={'customer': customer})
                account_balance = get_account_balance(pk)
                # Uncomment below code to start emails. Also add valid Sendgrid API key in settings.py and valid from email
                # mail_body = 'Your account is credited with Rs. ' + amount
                # send_mail(
                #     'Transaction Alert',
                #     mail_body,
                #     'from@example.com',
                #     [customer.email],
                #     fail_silently=False,
                # )
        else:
            messages.info(request, 'Amount cannot be withdrawn because withdraw amount is greater than account balance')
    context = {'form': form, 'account_balance': account_balance}
    return render(request, 'accounts/transaction_form.html', context)


@unauthenticated_user
def register_page(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(
                user=user,
                name=username,
                email=user.email
            )
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')
    context = {}
    return render(request, 'accounts/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')
