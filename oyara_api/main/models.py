import decimal, datetime, uuid
import dateutil.relativedelta as relativedelta

from django.db import models
from rest_framework.exceptions import ValidationError


class Customer(models.Model):
    accountNumber = models.CharField(max_length=10, unique=True)
    accountName = models.CharField(max_length=30)
    currency = models.CharField(max_length=3)
    accountOpeningDate = models.DateField(auto_now_add=True)
    lastTransactionDate = models.DateField(default=datetime.date.today)
    accountType = models.CharField(max_length=2, choices=[
        ("SA", "Savings"), ("CU", "Current"), ("FD", "Fixed Deposit")
    ])
    bvn = models.BigIntegerField()
    fullname = models.CharField(max_length=30)
    phoneNumber = models.BigIntegerField(blank=True)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=2, choices=[
        ("AC", "active"), ("IN", "inactive"), ("DO", "dormant")
    ])

    def save(self, *args, **kwargs):
        if self.accountNumber:
            if len(self.accountNumber) != 10:
                raise ValidationError("Account Number must have 10 digits")

        if self.currency and len(self.currency) != 3:
            raise ValidationError("Currency must have 3 characters")

        if self.bvn:
            if len(str(self.bvn)) not in range (10, 12):
                raise ValidationError("BVN must have 11 digits")
        
        super().save(*args, **kwargs)


class CustomerBalance(models.Model):
    accountNumber = models.CharField(max_length=10)
    currency = models.CharField(max_length=3)
    availableBalance = models.DecimalField(max_digits=22, decimal_places=2)
    clearedBalance = models.DecimalField(max_digits=22, decimal_places=2, blank=True, default=0.0)
    unclearBalance = models.DecimalField(max_digits=22, decimal_places=2, blank=True, default=0.0)
    holdBalance = models.DecimalField(max_digits=22, decimal_places=2, blank=True, default=0.0)
    minimumBalance = models.DecimalField(max_digits=22, decimal_places=2, blank=True, default=0.0)

    def save(self, *args, **kwargs):
        if self.accountNumber:
            customer = Customer.objects.filter(accountNumber=self.accountNumber)
            if len(customer) != 1:
                raise ValidationError("No customer with this account number exists")

            if len(self.accountNumber) != 10:
                raise ValidationError("Account Number must have 10 digits")
            customer = customer[0]

        if customer and self.currency and self.currency != customer.currency:
            raise ValidationError("Invalid currency")
        
        super().save(*args, **kwargs)


class Transaction(models.Model):
    accountNumber = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=22, decimal_places=2)
    currency = models.CharField(max_length=3)
    channel = models.CharField(max_length=3, blank=True, choices=[
        ("POS", "POS"), ("ATM", "ATM"), ("EC", "E-Channels")
    ])
    debitOrCredit = models.CharField(max_length=2, choices=[
        ("Cr", "Credit"), ("Dr", "Debit")
    ])
    narration = models.TextField()
    referenceId = models.UUIDField(default=uuid.uuid4, editable=False)
    transactionTime = models.DateTimeField(auto_now_add=True)
    transactionType = models.CharField(max_length=10, blank=True)
    valueDate = models.DateField(auto_now_add=True)
    balanceAfter = models.IntegerField(blank=True, default=0)

    def _get_charges(self, balance, customer):
        if self.debitOrCredit != "Dr":
            return 0.0

        if self.channel == "ATM":
            today = datetime.datetime.today()
            first_of_this_month = datetime.date(today.year, today.month, 1)
            transactions_this_month = Transaction.objects.filter(accountNumber=customer.accountNumber,
                valueDate__range=(first_of_this_month, datetime.date.today()), channel="ATM")
            if len(transactions_this_month) > 3:
                return 35.0
        elif self.channel == "POS":
            charge = decimal.Decimal(0.75/100) * self.amount
            return min(1200.00, charge)
        elif self.channel == "EC":
            if self.amount <= 5000:
                charge = decimal.Decimal(5/100) * self.amount
                return min(10.00, charge)
            if self.amount in range(5001, 50001):
                charge = decimal.Decimal(4.5/100) * self.amount
                return min(25, charge)
            if self.amount > 50000:
                charge = decimal.Decimal(3/100) * self.amount
                return min(50.00, charge)
        
        return 0.00
    
    def _authorise_transaction(self, balance, customer):
        if self.currency and self.currency != customer.currency:
            raise ValidationError("Invalid transaction currency")

        if customer.status != "AC":
            raise ValidationError("Transactions cannot be done on this account")

        if self.debitOrCredit == "Dr" and balance.availableBalance < self.amount:
            raise ValidationError("This amount cannot be withdrawn from this account")

        today = datetime.datetime.today()
        three_months_ago = today - relativedelta.relativedelta(months=3)
        all_transactions = Transaction.objects.all()
        recent_transactions = Transaction.objects.filter(accountNumber=customer.accountNumber,
            valueDate__range=(three_months_ago, datetime.date.today()))

        if len(all_transactions) > 0 and len(recent_transactions) == 0:
            customer.status = "DO"
            customer.save()
            raise ValidationError("This account is dormant")

    def _update_dependent_records(self, balance, customer):
        if self.debitOrCredit and self.accountNumber and self.amount:
            sign = -1 if self.debitOrCredit == "Dr" else 1
            balance.availableBalance += sign * self.amount
            self.balanceAfter = balance.availableBalance
            balance.save()

            customer.lastTransactionDate = datetime.date.today()
            customer.save()
    
    def save(self, *args, **kwargs):
        balance = CustomerBalance.objects.filter(accountNumber=self.accountNumber)
        customer = Customer.objects.filter(accountNumber=self.accountNumber)
        
        if len(customer) != 1:
            raise ValidationError("No customer with this account number exists")

        if len(balance) != 1:
            raise ValidationError("No balance has been created for this customer")

        balance = balance[0]
        customer = customer[0]
        
        charges = self._get_charges(balance, customer)
        self.amount += decimal.Decimal(charges)
        self._authorise_transaction(balance, customer)
        self._update_dependent_records(balance, customer)
        
        super().save(*args, **kwargs)
