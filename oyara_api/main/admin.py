from django.contrib import admin

from main.models import Customer, CustomerBalance, Transaction

admin.register(Customer, CustomerBalance, Transaction)
