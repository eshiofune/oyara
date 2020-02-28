from django.conf.urls import url, include
from rest_framework import serializers, viewsets, routers

from main.models import Customer, CustomerBalance, Transaction


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class CustomerBalanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomerBalance
        fields = '__all__'


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'