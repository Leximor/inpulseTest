from django.db import models


class User(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()

    class Meta:
        db_table = "user"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    has_processed_transactions = models.BooleanField(default=False)

    class Meta:
        db_table = "profile"


class Transaction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    status = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transaction"
