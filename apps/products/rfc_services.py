"""
RFC by Month Service Layer.

Returns Draft and Approved RFC data plus Last Year (LY) qty/value per product per month.
Update RFC: updates draft quantity (and backend-calculated draft value) in arf_rolling_forecasts.
"""
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.db import connection
from django.utils import timezone

from apps.accounts.models import Account
from apps.products.models import ArfRollingForecast, Product

from .services import _currency_symbol_for_account

# Statuses that allow draft updates (not Approved or Frozen)
ARF_EDITABLE_STATUSES = ("Draft", "Pending_Approval", "Fixes_Needed")


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


def _months_in_range(from_date: date, to_date: date) -> List[Tuple[str, str]]:
    """List of (YYYY-MM, monthLabel e.g. February 2026) from from_date to to_date by month."""
    months = []
    y, m = from_date.year, from_date.month
    end_y, end_m = to_date.year, to_date.month
    while (y, m) <= (end_y, end_m):
        ym = f"{y}-{m:02d}"
        try:
            label_date = date(y, m, 1)
            month_label = label_date.strftime("%B %Y")  # e.g. February 2026
        except Exception:
            month_label = ym
        months.append((ym, month_label))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return months


def _add_one_year_month_key(month_key: str) -> str:
    """Shift a YYYY-MM key forward by one year (LY month -> current month key)."""
    year, month = map(int, month_key.split("-"))
    return f"{year + 1}-{month:02d}"


def _subtract_one_year_month_key(month_key: str) -> str:
    """Shift a YYYY-MM key back by one year (API month -> LY month for lookup)."""
    year, month = map(int, month_key.split("-"))
    return f"{year - 1}-{month:02d}"


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
    months_list = _months_in_range(from_date, to_date)
    from_str = from_date.isoformat()
    to_str = to_date.isoformat()
    ly_from_str = ly_from.isoformat()
    ly_to_str = ly_to.isoformat()

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

    placeholders = ",".join(["%s"] * len(products_order))

    # Last year: invoice_line_items + invoices, by product and month
    # Include both 'Closed' and 'Posted' so LY data appears when invoices are in either status
    ly_query = f"""
        SELECT
            ili.ili_product_id AS product_id,
            TO_CHAR(inv.inv_invoice_date, 'YYYY-MM') AS month_key,
            COALESCE(SUM(ili.ili_quantity), 0) AS ly_qty,
            COALESCE(SUM(ili.ili_net_price), 0) AS ly_value
        FROM invoice_line_items ili
        INNER JOIN invoices inv ON inv.inv_sf_id = ili.ili_invoice_id
        WHERE inv.inv_account_id = %s
          AND ili.ili_product_id IN ({placeholders})
          AND inv.inv_invoice_date BETWEEN %s AND %s
          AND inv.inv_status IN ('Closed', 'Posted')
          AND inv.inv_valid = TRUE
          AND ili.ili_valid = TRUE
          AND (inv.inv_invoice_type IS NULL OR inv.inv_invoice_type != 'Credit Note')
        GROUP BY ili.ili_product_id, TO_CHAR(inv.inv_invoice_date, 'YYYY-MM')
    """
    with connection.cursor() as cursor:
        cursor.execute(
            ly_query,
            [account_id] + products_order + [ly_from_str, ly_to_str],
        )
        ly_rows = {
            # Map LY month (e.g. 2025-10) to current month key (2026-10)
            (row[0], _add_one_year_month_key(row[1])): {
                "lyQty": float(row[2]),
                "lyValue": float(row[3]),
            }
            for row in cursor.fetchall()
        }

    # Current year: arf_rolling_forecasts, draft and approved by product and month; include rejection reason
    rfc_query = f"""
        SELECT
            arf.arf_product_id AS product_id,
            TO_CHAR(arf.arf_forecast_date, 'YYYY-MM') AS month_key,
            COALESCE(SUM(arf.arf_draft_quantity), 0) AS draft_qty,
            COALESCE(SUM(arf.arf_draft_value), 0) AS draft_value,
            COALESCE(SUM(arf.arf_approved_quantity), 0) AS approved_qty,
            COALESCE(SUM(arf.arf_approved_value), 0) AS approved_value,
            MAX(arf.arf_rejection_reason) AS rejection_reason
        FROM arf_rolling_forecasts arf
        WHERE arf.arf_account_id = %s
          AND arf.arf_product_id IN ({placeholders})
          AND arf.arf_forecast_date BETWEEN %s AND %s
          AND arf.arf_active = 1
        GROUP BY arf.arf_product_id, TO_CHAR(arf.arf_forecast_date, 'YYYY-MM')
    """
    with connection.cursor() as cursor:
        cursor.execute(
            rfc_query,
            [account_id] + products_order + [from_str, to_str],
        )
        rfc_rows = {
            (row[0], row[1]): {
                "draftRfcQty": float(row[2]),
                "draftRfcValue": float(row[3]),
                "approvedRfcQty": float(row[4]),
                "approvedRfcValue": float(row[5]),
                "rejectionReason": row[6] if row[6] else None,
            }
            for row in cursor.fetchall()
        }

    # Build products list: each product has months with ly + draft + approved
    products_out = []
    for product_id in products_order:
        product_name = product_names.get(product_id, product_id)
        months_out = []
        for ym, month_label in months_list:
            ly_month_key = _subtract_one_year_month_key(ym)  # API month 2026-10 -> LY 2025-10
            ly = ly_rows.get((product_id, ly_month_key), {"lyQty": 0.0, "lyValue": 0.0})
            rfc = rfc_rows.get(
                (product_id, ym),
                {
                    "draftRfcQty": 0.0,
                    "draftRfcValue": 0.0,
                    "approvedRfcQty": 0.0,
                    "approvedRfcValue": 0.0,
                    "rejectionReason": None,
                },
            )
            months_out.append({
                "month": ym,
                "monthLabel": month_label,
                "lyQty": ly["lyQty"],
                "lyValue": ly["lyValue"],
                "draftRfcQty": rfc["draftRfcQty"],
                "draftRfcValue": rfc["draftRfcValue"],
                "approvedRfcQty": rfc["approvedRfcQty"],
                "approvedRfcValue": rfc["approvedRfcValue"],
                "rejectionReason": rfc.get("rejectionReason"),
            })
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
    Update draft RFC quantity (and backend-calculated draft value) in arf_rolling_forecasts.

    - User sends only draftRfcQty per (productId, month).
    - Backend sets arf_draft_quantity; computes arf_draft_value = qty × unit_price
      (unit price from existing row: arf_draft_unit_price else arf_approved_unit_price; else null).
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
        product_id = (item.get("productId") or "").strip()
        month_str = (item.get("month") or "").strip()
        draft_qty = item.get("draftRfcQty")

        if not product_id or not month_str:
            not_updated.append({
                "productId": product_id or "(missing)",
                "month": month_str or "(missing)",
                "reason": "productId and month are required",
            })
            continue

        if draft_qty is None:
            not_updated.append({
                "productId": product_id,
                "month": month_str,
                "reason": "draftRfcQty is required",
            })
            continue

        try:
            qty_decimal = Decimal(str(draft_qty))
            if qty_decimal < 0:
                not_updated.append({
                    "productId": product_id,
                    "month": month_str,
                    "reason": "draftRfcQty must be non-negative",
                })
                continue
        except (ValueError, TypeError):
            not_updated.append({
                "productId": product_id,
                "month": month_str,
                "reason": "draftRfcQty must be a valid number",
            })
            continue

        try:
            forecast_date = _parse_month_to_date(month_str)
        except (ValueError, IndexError):
            not_updated.append({
                "productId": product_id,
                "month": month_str,
                "reason": "month must be YYYY-MM",
            })
            continue

        if not _is_future_month(month_str):
            not_updated.append({
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
                "productId": product_id,
                "month": month_str,
                "reason": "No editable forecast row found for this product and month",
            })
            continue

        unit_price = None
        if row.arf_draft_unit_price is not None:
            unit_price = row.arf_draft_unit_price
        elif row.arf_approved_unit_price is not None:
            unit_price = row.arf_approved_unit_price

        draft_value = None
        if unit_price is not None:
            draft_value = (qty_decimal * unit_price).quantize(Decimal("0.01"))

        row.arf_draft_quantity = qty_decimal
        row.arf_draft_value = draft_value
        row.arf_agent_modified_by_id = modified_by_id
        row.arf_agent_modified_date = modified_at
        row.arf_last_modified_by_id = modified_by_id or row.arf_last_modified_by_id or ""
        row.save(update_fields=[
            "arf_draft_quantity",
            "arf_draft_value",
            "arf_agent_modified_by_id",
            "arf_agent_modified_date",
            "arf_last_modified_by_id",
            "arf_updated_at",
        ])

        updated.append({"productId": product_id, "month": month_str})

    return {
        "accountId": account_id,
        "updatedCount": len(updated),
        "updated": updated,
        "notUpdated": not_updated,
    }
