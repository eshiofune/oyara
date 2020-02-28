from django.contrib import admin
from django.urls import include, path

from rest_framework import routers

from main.views import CustomerViewSet, CustomerBalanceViewSet, TransactionViewSet

router = routers.DefaultRouter()
router.register('customer', CustomerViewSet)
router.register('balance', CustomerBalanceViewSet)
router.register('transaction', TransactionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
