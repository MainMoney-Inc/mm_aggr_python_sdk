from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    price = models.CharField(max_length=32)
    currency = models.CharField(max_length=8)

    class Meta:
        db_table = "products"

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    reference = models.CharField(max_length=64, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orders")
    amount = models.CharField(max_length=32)
    currency = models.CharField(max_length=8)
    status = models.CharField(max_length=32, default="pending")

    class Meta:
        db_table = "orders"


class Transfer(models.Model):
    reference = models.CharField(max_length=64, unique=True)
    amount = models.CharField(max_length=32)
    currency = models.CharField(max_length=8)
    destination = models.CharField(max_length=64, blank=True, default="")
    status = models.CharField(max_length=32, default="pending")

    class Meta:
        db_table = "transfers"
