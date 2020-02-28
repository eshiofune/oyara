from rest_framework import serializers, viewsets, routers

from main.models import Customer, CustomerBalance, Transaction
from main.serializers import CustomerSerializer, CustomerBalanceSerializer, TransactionSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerBalanceViewSet(viewsets.ModelViewSet):
    queryset = CustomerBalance.objects.all()
    serializer_class = CustomerBalanceSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer