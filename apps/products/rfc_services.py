"""
RFC by Month Service Layer.

Returns Draft and Approved RFC data plus Last Year (LY) qty/value per product per month.
Update RFC: updates draft quantity (and backend-calculated draft value) in arf_rolling_forecasts.
"""
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Sum, Max, F, Q, DecimalField, Value
from django.db.models.functions import TruncMonth, Coalesce
from django.utils import timezone

from apps.accounts.models import Account
from apps.products.models import ArfRollingForecast, Product, InvoiceLineItem

from .services import _currency_symbol_for_account

# Statuses that allow draft updates (not Approved or Frozen)
ARF_EDITABLE_STATUSES = ("Draft", "Pending_Approval", "Fixes_Needed", "Approved")


def _parse_dates(from_month: str, to_month: str) -> Tuple[date, date]:
    """Parse YYYY-MM to (first_day, last_day) as date objects."""
    from_year, from_m = map(int, from_month.split("-"))
    to_year, to_m = map(int, to_month.split("-"))
    from_date = date(from_year, from_m, 1)
    last_day = monthrange(to_year, to_m)[1]
    to_date = date(to_year, to_m, last_day)
    return from_date, to_date


def _default_month_range() -> Tuple[date, date]:
    """Current month through same month next year."""
    today = date.today()
    from_date = date(today.year, today.month, 1)
    to_year = today.year + 1
    to_month = today.month
    last_day = monthrange(to_year, to_month)[1]
    to_date = date(to_year, to_month, last_day)
    return from_date, to_date


def _ly_range(from_date: date, to_date: date) -> Tuple[date, date]:
    """Same window shifted back one year."""
    ly_from = date(from_date.year - 1, from_date.month, from_date.day)
    ly_to = date(to_date.year - 1, to_date.month, to_date.day)
    return ly_from, ly_to


def _subtract_one_year_month_key(month_key: str) -> str:
    """Shift a YYYY-MM key back by one year (API month -> LY month for lookup)."""
    year, month = map(int, month_key.split("-"))
    return f"{year - 1}-{month:02d}"


def _add_one_year_month_key(month_key: str) -> str:
    """Shift a YYYY-MM key forward by one year (LY month -> current year month for lookup)."""
    year, month = map(int, month_key.split("-"))
    return f"{year + 1}-{month:02d}"


def get_rfc_by_month(
    account_id: str,
    product_ids: List[str],
    from_date: date,
    to_date: date,
) -> Dict[str, Any]:
    """
    Get RFC by month: LY qty/value and Draft/Approved RFC qty/value per product per month.

    from_date/to_date are the current (RFC) range; LY range is same window - 1 year.
    """
    ly_from, ly_to = _ly_range(from_date, to_date)

    if not product_ids:
        return {
            "accountId": account_id,
            "from": f"{from_date.year}-{from_date.month:02d}",
            "to": f"{to_date.year}-{to_date.month:02d}",
            "currencySymbol": _currency_symbol_for_account(account_id),
            "products": [],
        }

    # Product order and names: preserve request order
    products_order = list(dict.fromkeys(product_ids))
    products_qs = Product.objects.filter(prd_sf_id__in=products_order).only(
        "prd_sf_id", "prd_name"
    )
    product_names = {p.prd_sf_id: p.prd_name for p in products_qs}
    # Include requested IDs even if not in DB (name can be ID)
    for pid in products_order:
        if pid not in product_names:
            product_names[pid] = pid

    # Last year: invoice_line_items + invoices, by product and month
    # Include both 'Closed' and 'Posted' so LY data appears when invoices are in either status
    ly_data = InvoiceLineItem.objects.filter(
        ili_invoice_id__inv_account_id=account_id,
        ili_product_id__in=products_order,
        ili_invoice_id__inv_invoice_date__range=[ly_from, ly_to],
        ili_invoice_id__inv_status__in=['Closed', 'Posted'],
        ili_invoice_id__inv_valid=True,
        ili_valid=True,
    ).exclude(
        ili_invoice_id__inv_invoice_type='Credit Note'
    ).annotate(
        month=TruncMonth('ili_invoice_id__inv_invoice_date')
    ).values('ili_product_id', 'month').annotate(
        ly_qty=Coalesce(Sum('ili_quantity'), Decimal('0')),
        ly_value=Coalesce(Sum('ili_net_price'), Decimal('0'))
    )

    # Convert to dict with month key shifted forward by 1 year
    ly_rows = {}
    for row in ly_data:
        product_id = row['ili_product_id']
        month_date = row['month']
        month_key = f"{month_date.year}-{month_date.month:02d}"
        # Shift LY month to current year
        current_month_key = _add_one_year_month_key(month_key)
        ly_rows[(product_id, current_month_key)] = {
            "lyQty": float(row['ly_qty']),
            "lyValue": float(row['ly_value']),
        }

    # Current year: arf_rolling_forecasts, draft and approved by product and month
    rfc_data = ArfRollingForecast.objects.filter(
        arf_account_id=account_id,
        arf_product_id__in=products_order,
        arf_forecast_date__range=[from_date, to_date],
        arf_active=1,
    ).annotate(
        month=TruncMonth('arf_forecast_date'),
        draft_qty=Coalesce(Sum('arf_draft_quantity'), Decimal('0')),
        draft_value=Coalesce(Sum(F('arf_draft_quantity') * F('arf_draft_unit_price'), output_field=DecimalField()), Decimal('0')),
        draft_unit_price=Max('arf_draft_unit_price'),
        approved_qty=Coalesce(Sum('arf_approved_quantity'), Decimal('0')),
        approved_value=Coalesce(Sum(F('arf_approved_quantity') * F('arf_approved_unit_price'), output_field=DecimalField()), Decimal('0')),
        approved_unit_price=Max('arf_approved_unit_price'),
    ).values(
        'arf_id', 'arf_product_id', 'month', 'arf_rejection_reason'
    ).annotate(
        draft_qty=Coalesce(Sum('arf_draft_quantity'), Decimal('0')),
        draft_value=Coalesce(Sum(F('arf_draft_quantity') * F('arf_draft_unit_price'), output_field=DecimalField()), Decimal('0')),
        draft_unit_price=Max('arf_draft_unit_price'),
        approved_qty=Coalesce(Sum('arf_approved_quantity'), Decimal('0')),
        approved_value=Coalesce(Sum(F('arf_approved_quantity') * F('arf_approved_unit_price'), output_field=DecimalField()), Decimal('0')),
        approved_unit_price=Max('arf_approved_unit_price'),
    ).filter(
        Q(draft_qty__gt=0) | Q(approved_qty__gt=0)
    )

    # Convert to dict
    rfc_rows = {}
    for row in rfc_data:
        product_id = row['arf_product_id']
        month_date = row['month']
        month_key = f"{month_date.year}-{month_date.month:02d}"
        rfc_rows[(product_id, month_key)] = {
            "rfcId": row['arf_id'],
            "draftRfcQty": float(row['draft_qty']),
            "draftRfcValue": float(row['draft_value']),
            "draftRfcUnitPrice": float(row['draft_unit_price']) if row['draft_unit_price'] is not None else None,
            "approvedRfcQty": float(row['approved_qty']),
            "approvedRfcValue": float(row['approved_value']),
            "approvedRfcUnitPrice": float(row['approved_unit_price']) if row['approved_unit_price'] is not None else None,
            "rejectionReason": row['arf_rejection_reason'] if row['arf_rejection_reason'] else None,
        }

    # Build products list: only include months that have RFC entries in the forecast table
    products_out = []
    for product_id in products_order:
        product_name = product_names.get(product_id, product_id)
        months_out = []
        
        # Only iterate through months that have RFC data for this product
        for (rfc_product_id, ym), rfc_data_item in rfc_rows.items():
            if rfc_product_id != product_id:
                continue
            
            # Get month label
            try:
                year, month = map(int, ym.split("-"))
                label_date = date(year, month, 1)
                month_label = label_date.strftime("%B %Y")
            except Exception:
                month_label = ym
            
            # Get LY data if available (optional, for display)
            ly_month_key = _subtract_one_year_month_key(ym)
            ly = ly_rows.get((product_id, ly_month_key), {"lyQty": 0.0, "lyValue": 0.0})
            
            months_out.append({
                "rfcId": rfc_data_item["rfcId"],
                "month": ym,
                "monthLabel": month_label,
                "lyQty": ly["lyQty"],
                "lyValue": ly["lyValue"],
                "draftRfcQty": rfc_data_item["draftRfcQty"],
                "draftRfcValue": rfc_data_item["draftRfcValue"],
                "draftRfcUnitPrice": rfc_data_item.get("draftRfcUnitPrice"),
                "approvedRfcQty": rfc_data_item["approvedRfcQty"],
                "approvedRfcValue": rfc_data_item["approvedRfcValue"],
                "approvedRfcUnitPrice": rfc_data_item.get("approvedRfcUnitPrice"),
                "rejectionReason": rfc_data_item.get("rejectionReason"),
            })
        
        # Only include product if it has at least one RFC entry
        if months_out:
            products_out.append({
                "productId": product_id,
                "productName": product_name,
                "months": months_out,
            })

    return {
        "accountId": account_id,
        "from": f"{from_date.year}-{from_date.month:02d}",
        "to": f"{to_date.year}-{to_date.month:02d}",
        "currencySymbol": _currency_symbol_for_account(account_id),
        "products": products_out,
    }


def _parse_month_to_date(month_str: str) -> date:
    """Parse YYYY-MM to first day of month."""
    year, month = map(int, month_str.split("-"))
    return date(year, month, 1)


def _is_future_month(month_str: str) -> bool:
    """True if the first day of month_str is strictly after today."""
    try:
        d = _parse_month_to_date(month_str)
        return d > date.today()
    except (ValueError, IndexError):
        return False


def update_rfc(
    account_id: str,
    updates: List[Dict[str, Any]],
    modified_by_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Update draft RFC quantity in arf_rolling_forecasts.

    - User sends draftRfcQty per (productId, month) or rfcId.
    - If rfcId is provided, it's used directly (faster, no ambiguity).
    - If rfcId is not provided, falls back to searching by productId + month.
    - Backend sets arf_draft_quantity; draft value is calculated as qty × unit_price on retrieval.
    - Only rows with status in Draft, Pending_Approval, Fixes_Needed and arf_active=1 are updated.
    - Returns updatedCount, updated list, and notUpdated list with reasons.
    """
    updated: List[Dict[str, str]] = []
    not_updated: List[Dict[str, Any]] = []
    modified_at = timezone.now()
    modified_by_id = None
    if modified_by_user is not None and getattr(modified_by_user, "usr_sf_id", None):
        modified_by_id = str(modified_by_user.usr_sf_id)

    for item in updates:
        rfc_id = item.get("rfcId")
        product_id = (item.get("productId") or "").strip()
        month_str = (item.get("month") or "").strip()
        draft_qty = item.get("draftRfcQty")

        if draft_qty is None:
            not_updated.append({
                "rfcId": rfc_id,
                "productId": product_id or "(missing)",
                "month": month_str or "(missing)",
                "reason": "draftRfcQty is required",
            })
            continue

        try:
            qty_decimal = Decimal(str(draft_qty))
            if qty_decimal < 0:
                not_updated.append({
                    "rfcId": rfc_id,
                    "productId": product_id or "(missing)",
                    "month": month_str or "(missing)",
                    "reason": "draftRfcQty must be non-negative",
                })
                continue
        except (ValueError, TypeError):
            not_updated.append({
                "rfcId": rfc_id,
                "productId": product_id or "(missing)",
                "month": month_str or "(missing)",
                "reason": "draftRfcQty must be a valid number",
            })
            continue

        row = None

        # If rfcId is provided, use it directly
        if rfc_id:
            try:
                rfc_id_int = int(rfc_id)
                row = (
                    ArfRollingForecast.objects.filter(
                        arf_id=rfc_id_int,
                        arf_account_id=account_id,
                        arf_status__in=ARF_EDITABLE_STATUSES,
                        arf_active=1,
                    )
                    .first()
                )
                if not row:
                    not_updated.append({
                        "rfcId": rfc_id,
                        "productId": product_id or "(missing)",
                        "month": month_str or "(missing)",
                        "reason": "RFC not found or not editable",
                    })
                    continue
            except (ValueError, TypeError):
                not_updated.append({
                    "rfcId": rfc_id,
                    "productId": product_id or "(missing)",
                    "month": month_str or "(missing)",
                    "reason": "rfcId must be a valid integer",
                })
                continue
        else:
            # Fallback: search by productId + month
            if not product_id or not month_str:
                not_updated.append({
                    "rfcId": rfc_id,
                    "productId": product_id or "(missing)",
                    "month": month_str or "(missing)",
                    "reason": "rfcId or (productId + month) are required",
                })
                continue

            try:
                forecast_date = _parse_month_to_date(month_str)
            except (ValueError, IndexError):
                not_updated.append({
                    "rfcId": rfc_id,
                    "productId": product_id,
                    "month": month_str,
                    "reason": "month must be YYYY-MM",
                })
                continue

            if not _is_future_month(month_str):
                not_updated.append({
                    "rfcId": rfc_id,
                    "productId": product_id,
                    "month": month_str,
                    "reason": "Only future months can be edited",
                })
                continue

            row = (
                ArfRollingForecast.objects.filter(
                    arf_account_id=account_id,
                    arf_product_id=product_id,
                    arf_forecast_date__year=forecast_date.year,
                    arf_forecast_date__month=forecast_date.month,
                    arf_status__in=ARF_EDITABLE_STATUSES,
                    arf_active=1,
                )
                .order_by("arf_forecast_date")
                .first()
            )

            if not row:
                not_updated.append({
                    "rfcId": rfc_id,
                    "productId": product_id,
                    "month": month_str,
                    "reason": "No editable forecast row found for this product and month",
                })
                continue

        row.arf_draft_quantity = qty_decimal
        if modified_by_id:
            row.arf_agent_modified_by_id = modified_by_id
        row.arf_agent_modified_date = modified_at
        row.save(update_fields=[
            "arf_draft_quantity",
            "arf_agent_modified_by",
            "arf_agent_modified_date",
            "arf_updated_at",
        ])

        updated.append({
            "rfcId": row.arf_id,
            "productId": str(row.arf_product_id_id),
            "month": month_str or f"{row.arf_forecast_date.year}-{row.arf_forecast_date.month:02d}",
        })

    return {
        "accountId": account_id,
        "updatedCount": len(updated),
        "updated": updated,
        "notUpdated": not_updated,
    }
