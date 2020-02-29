import datetime, json

from django.forms.models import model_to_dict
from django.http import HttpResponse

from rest_framework import serializers, viewsets, routers, mixins
from rest_framework.response import Response

from main.models import Customer, CustomerBalance, Transaction
from main.serializers import CustomerSerializer, CustomerBalanceSerializer, TransactionSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerBalanceViewSet(viewsets.ModelViewSet):
    queryset = CustomerBalance.objects.all()
    serializer_class = CustomerBalanceSerializer


class TransactionViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class ListTransactionViewSet(viewsets.ViewSet):
    """
    ViewSet for listing transactions.
    """
    def list(self, request):
        start_date = request.data.get("startDate")
        end_date = request.data.get("endDate") or datetime.date.today()
        acc_no = request.data.get("accNumber") or ""
        channel = request.data.get("channel") or ""
        reference_id = request.data.get("referenceID") or ""

        if start_date:
            queryset = Transaction.objects.filter(
                valueDate__range(start_date, end_date),
                accountNumber__icontains=acc_no,
                channel__icontains=channel,
                referenceId__icontains=reference_id)
        else:
            queryset = Transaction.objects.filter(
                # accountNumber__icontains=acc_no,
                # channel__icontains=channel,
                referenceId__icontains=reference_id)

        serializer = TransactionSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


def list_transactions(request):
    start_date = request.GET.get("startDate")
    end_date = request.GET.get("endDate") or datetime.date.today()
    acc_no = request.GET.get("accNumber") or ""
    channel = request.GET.get("channel") or ""
    reference_id = request.GET.get("referenceID") or ""

    # if start_date:
    #     results = Transaction.objects.filter(
    #         valueDate__range(start_date, end_date),
    #         accountNumber__icontains=acc_no,
    #         channel__icontains=channel,
    #         referenceId__icontains=reference_id)
    # else:
    results = Transaction.objects.filter(
            # accountNumber__icontains=acc_no)
            # channel__icontains=channel,
        referenceId__icontains=reference_id)

    for item in results:
        item['data'] = model_to_dict(item['data'])

    results = list(results)
    # data = TransactionSerializer(results, context={'request': request})
    # print(serializer.data
    # return JsonResponse(serializer.data)
    return HttpResponse(json.dumps(results))