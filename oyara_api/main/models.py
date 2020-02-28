import datetime, uuid

from django.db import models


class Customer(models.Model):
    accountNumber = models.CharField(max_length=10)
    accountName = models.CharField(max_length=30)
    currency = models.CharField(max_length=3)
    accountOpeningDate = models.DateField()
    lastTransactionDate = models.DateField()
    accountType = models.CharField(max_length=30)
    bvn = models.IntegerField()
    fullname = models.CharField(max_length=30)
    phoneNumber = models.BigIntegerField(blank=True)
    email = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=2, choices=[
        ("AC", "active"), ("IN", "inactive"), ("DO", "dormant")
    ])

    def save(self, *args, **kwargs):
        if self.accountNumber:
            if len(self.accountNumber) != 10:
                raise ValueError("Account Number must have 10 digits")
        
        super().save(*args, **kwargs)


class CustomerBalance(models.Model):
    accountNumber = models.CharField(max_length=10)
    currency = models.CharField(max_length=3)
    availableBalance = models.IntegerField()
    clearedBalance = models.IntegerField(blank=True)
    unclearBalance = models.IntegerField(blank=True)
    holdBalance = models.IntegerField(blank=True)
    minimumBalance = models.IntegerField(blank=True)


class Transaction(models.Model):
    accountNumber = models.CharField(max_length=10)
    amount = models.IntegerField()
    currency = models.CharField(max_length=3)
    channel = models.CharField(max_length=10, blank=True)
    debitOrCredit = models.CharField(max_length=2, choices=[
        ("Cr", "Credit"), ("Dr", "Debit")
    ])
    narration = models.TextField()
    referenceId = models.UUIDField(default=uuid.uuid4)
    transactionTime = models.DateTimeField()
    transactionType = models.CharField(max_length=10)
    valueDate = models.DateTimeField()
    balanceAfter = models.IntegerField(blank=True, default=0)

    def save(self, *args, **kwargs):
        if self.currency and self.accountNumber:
            customer = Customer.objects.get(accountNumber=self.accountNumber)
            if self.currency != customer.currency:
                raise ValueError("Invalid transaction currency")

        if self.accountNumber:
            customer = Customer.objects.get(accountNumber=self.accountNumber)
            if customer.status != "AC":
                raise ValueError("Transactions cannot be done on this account")

        if self.debitOrCredit and self.accountNumber and self.amount:
            balance = CustomerBalance.objects.get(accountNumber=self.accountNumber)
            customer = Customer.objects.get(accountNumber=self.accountNumber)

            sign = -1 if self.debitOrCredit == "Dr" else 1
            balance.availableBalance += sign * self.amount
            balance.save()

            customer.lastTransactionDate = datetime.datetime.today()
            customer.save()
        
        super().save(*args, **kwargs)