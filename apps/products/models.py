# apps/products/models.py

from django.conf import settings
from django.db import models


class ProductBrand(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ProductBrands'
        verbose_name = 'Product Brand'
        verbose_name_plural = 'Product Brands'

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=255)
    family = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    classification = models.CharField(max_length=255, blank=True, null=True)
    central_product_code = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    product_code = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    product_brand = models.ForeignKey(
        ProductBrand, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='products',
        db_column='ProductBrandId', db_index=True
    )
    brand = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_products',
        db_column='CreatedById'
    )
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='modified_products',
        db_column='LastModifiedById'
    )

    class Meta:
        db_table = 'Products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name
