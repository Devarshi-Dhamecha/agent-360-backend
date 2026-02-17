"""
Analytics Selectors

All database queries for analytics aggregation.
"""
from datetime import date
from decimal import Decimal
from typing import Dict, List
from django.db.models import Sum, F, Q, Value, CharField, Case, When, DecimalField
from django.db.models.functions import Coalesce

from apps.invoices.models import Invoice, InvoiceLineItem
from apps.forecasts.models import Forecast
from apps.products.models import Product


def get_family_actual_sales(start_date: date, end_date: date) -> List[Dict]:
    """
    Get actual sales aggregated by product family.
    
    Args:
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        List of dicts with family and actual_sales
    """
    return list(
        InvoiceLineItem.objects.filter(
            is_valid=True,
            invoice__status='Closed',
            invoice__invoice_date__gte=start_date,
            invoice__invoice_date__lte=end_date
        )
        .values(family=F('product__family'))
        .annotate(
            actual_sales=Coalesce(Sum('net_price'), Value(0), output_field=DecimalField())
        )
        .order_by('family')
    )


def get_family_rfc(start_date: date, end_date: date) -> List[Dict]:
    """
    Get RFC (forecast revenue) aggregated by product family.
    
    Args:
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        List of dicts with family and rfc
    """
    return list(
        Forecast.objects.filter(
            forecast_date__gte=start_date,
            forecast_date__lte=end_date
        )
        .values(family=F('product__family'))
        .annotate(
            rfc=Coalesce(Sum('revenue'), Value(0), output_field=DecimalField())
        )
        .order_by('family')
    )


def get_family_last_year_sales(start_date: date, end_date: date) -> List[Dict]:
    """
    Get last year sales aggregated by product family.
    
    Args:
        start_date: Start date for last year period
        end_date: End date for last year period
        
    Returns:
        List of dicts with family and last_year_sales
    """
    return list(
        InvoiceLineItem.objects.filter(
            is_valid=True,
            invoice__status='Closed',
            invoice__invoice_date__gte=start_date,
            invoice__invoice_date__lte=end_date
        )
        .values(family=F('product__family'))
        .annotate(
            last_year_sales=Coalesce(Sum('net_price'), Value(0), output_field=DecimalField())
        )
        .order_by('family')
    )


def get_product_actual_sales(parent_id: str, start_date: date, end_date: date) -> List[Dict]:
    """
    Get actual sales aggregated by product for a specific family.
    
    Args:
        parent_id: Product family name
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        List of dicts with product_id, product_name, and actual_sales
    """
    return list(
        InvoiceLineItem.objects.filter(
            is_valid=True,
            invoice__status='Closed',
            invoice__invoice_date__gte=start_date,
            invoice__invoice_date__lte=end_date,
            product__family=parent_id
        )
        .values(
            product_id=F('product__id'),
            product_name=F('product__name')
        )
        .annotate(
            actual_sales=Coalesce(Sum('net_price'), Value(0), output_field=DecimalField())
        )
        .order_by('product_id')
    )


def get_product_rfc(parent_id: str, start_date: date, end_date: date) -> List[Dict]:
    """
    Get RFC aggregated by product for a specific family.
    
    Args:
        parent_id: Product family name
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        List of dicts with product_id and rfc
    """
    return list(
        Forecast.objects.filter(
            forecast_date__gte=start_date,
            forecast_date__lte=end_date,
            product__family=parent_id
        )
        .values(product_id=F('product__id'))
        .annotate(
            rfc=Coalesce(Sum('revenue'), Value(0), output_field=DecimalField())
        )
        .order_by('product_id')
    )


def get_product_last_year_sales(parent_id: str, start_date: date, end_date: date) -> List[Dict]:
    """
    Get last year sales aggregated by product for a specific family.
    
    Args:
        parent_id: Product family name
        start_date: Start date for last year period
        end_date: End date for last year period
        
    Returns:
        List of dicts with product_id and last_year_sales
    """
    return list(
        InvoiceLineItem.objects.filter(
            is_valid=True,
            invoice__status='Closed',
            invoice__invoice_date__gte=start_date,
            invoice__invoice_date__lte=end_date,
            product__family=parent_id
        )
        .values(product_id=F('product__id'))
        .annotate(
            last_year_sales=Coalesce(Sum('net_price'), Value(0), output_field=DecimalField())
        )
        .order_by('product_id')
    )


def get_invoice_actual_sales(parent_id: str, start_date: date, end_date: date) -> List[Dict]:
    """
    Get actual sales aggregated by invoice for a specific product.
    
    Args:
        parent_id: Product ID
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        List of dicts with invoice details and actual_sales
    """
    return list(
        InvoiceLineItem.objects.filter(
            is_valid=True,
            invoice__status='Closed',
            invoice__invoice_date__gte=start_date,
            invoice__invoice_date__lte=end_date,
            product_id=parent_id
        )
        .values(
            invoice_id=F('invoice__id'),
            invoice_number=F('invoice__invoice_number'),
            invoice_status=F('invoice__status')
        )
        .annotate(
            actual_sales=Coalesce(Sum('net_price'), Value(0), output_field=DecimalField())
        )
        .order_by('invoice_id')
    )


def get_invoice_rfc(parent_id: str, start_date: date, end_date: date) -> List[Dict]:
    """
    Get RFC aggregated by invoice for a specific product.
    
    Args:
        parent_id: Product ID
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        List of dicts with invoice_id and rfc
    """
    # Note: Forecasts don't have invoice relationship, so we aggregate by product
    # and distribute evenly across invoices (simplified approach)
    return list(
        Forecast.objects.filter(
            forecast_date__gte=start_date,
            forecast_date__lte=end_date,
            product_id=parent_id
        )
        .values(invoice_id=Value(None, output_field=CharField()))
        .annotate(
            rfc=Coalesce(Sum('revenue'), Value(0), output_field=DecimalField())
        )
    )


def get_invoice_last_year_sales(parent_id: str, start_date: date, end_date: date) -> List[Dict]:
    """
    Get last year sales aggregated by invoice for a specific product.
    
    Args:
        parent_id: Product ID
        start_date: Start date for last year period
        end_date: End date for last year period
        
    Returns:
        List of dicts with invoice_id and last_year_sales
    """
    return list(
        InvoiceLineItem.objects.filter(
            is_valid=True,
            invoice__status='Closed',
            invoice__invoice_date__gte=start_date,
            invoice__invoice_date__lte=end_date,
            product_id=parent_id
        )
        .values(invoice_id=F('invoice__id'))
        .annotate(
            last_year_sales=Coalesce(Sum('net_price'), Value(0), output_field=DecimalField())
        )
        .order_by('invoice_id')
    )
