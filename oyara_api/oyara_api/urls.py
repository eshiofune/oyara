from django.contrib import admin
from django.urls import include, path

from rest_framework import routers

from main.views import CustomerViewSet, CustomerBalanceViewSet, TransactionViewSet, ListTransactionViewSet, list_transactions

router = routers.DefaultRouter()
router.register('customer', CustomerViewSet)
router.register('balance', CustomerBalanceViewSet)
router.register('transaction', TransactionViewSet)
router.register('list-transactions', ListTransactionViewSet, basename="Transaction")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('list-transactions', list_transactions)
]
