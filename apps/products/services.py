"""
Product Performance Service Layer.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Tuple, Any, Optional
from calendar import monthrange

from django.db import connection
from django.db.models import Sum, Q
from apps.accounts.models import Account, FrameAgreement, Target
from apps.products.models import Invoice

# ISO 4217 currency code → symbol for display (extend as needed)
CURRENCY_SYMBOLS = {
    'GBP': '£',
    'EUR': '€',
    'USD': '$',
    'CHF': 'CHF',
    'JPY': '¥',
    'INR': '₹',
}


def _currency_symbol_for_account(account_id: str) -> str:
    """Resolve display currency symbol from account's acc_currency_iso_code. Defaults to £ (GBP)."""
    try:
        acc = Account.objects.only('acc_currency_iso_code').get(acc_sf_id=account_id)
        code = (acc.acc_currency_iso_code or '').strip().upper()
        return CURRENCY_SYMBOLS.get(code, code or '£')  # use code if unknown, else £
    except Account.DoesNotExist:
        return '£'


class ProductPerformanceService:
    """Service for calculating product performance variance."""
    
    @staticmethod
    def parse_month_range(from_month: str, to_month: str) -> Tuple[str, str]:
        """
        Convert YYYY-MM format to first and last day of month range.
        
        Args:
            from_month: Start month in YYYY-MM format
            to_month: End month in YYYY-MM format
            
        Returns:
            Tuple of (from_date, to_date) in YYYY-MM-DD format
            
        Raises:
            ValueError: If date format is invalid
        """
        try:
            # Parse from_month
            from_year, from_month_num = map(int, from_month.split('-'))
            from_date = f"{from_year}-{from_month_num:02d}-01"
            
            # Parse to_month and get last day
            to_year, to_month_num = map(int, to_month.split('-'))
            last_day = monthrange(to_year, to_month_num)[1]
            to_date = f"{to_year}-{to_month_num:02d}-{last_day:02d}"
            
            # Validate dates
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
            
            return from_date, to_date
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM: {str(e)}")
    
    @staticmethod
    def get_product_performance(from_date: str, to_date: str, account_id: str = None) -> Dict[str, List[Dict]]:
        """
        Calculate product performance variance between forecast and actual revenue.
        
        Args:
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            account_id: Optional Salesforce Account ID to filter by
            
        Returns:
            Dictionary with topPerformers and bottomPerformers lists
        """
        # Build query with optional account filter
        account_filter_actual = "AND inv.inv_account_id = %s" if account_id else ""
        account_filter_forecast = "AND arf.arf_account_id = %s" if account_id else ""
        
        query = f"""
        WITH actual_revenue AS (
            SELECT
                p.prd_sf_id AS product_id,
                p.prd_name AS product_name,
                COALESCE(SUM(ili.ili_net_price), 0) AS actual_revenue
            FROM
                products p
            LEFT JOIN
                invoice_line_items ili ON ili.ili_product_id = p.prd_sf_id
            LEFT JOIN
                invoices inv ON inv.inv_sf_id = ili.ili_invoice_id
            WHERE
                inv.inv_invoice_date BETWEEN %s AND %s
                AND inv.inv_status = 'Closed'
                AND inv.inv_valid = TRUE
                AND ili.ili_valid = TRUE
                AND inv.inv_invoice_type != 'Credit Note'
                {account_filter_actual}
            GROUP BY
                p.prd_sf_id, p.prd_name
        ),
        forecast_revenue AS (
            SELECT
                arf.arf_product_id AS product_id,
                COALESCE(SUM(arf.arf_approved_value), 0) AS forecast_revenue
            FROM
                arf_rolling_forecasts arf
            WHERE
                arf.arf_forecast_date BETWEEN %s AND %s
                AND arf.arf_status = 'Approved'
                {account_filter_forecast}
            GROUP BY
                arf.arf_product_id
        ),
        combined AS (
            SELECT
                COALESCE(ar.product_id, fr.product_id) AS product_id,
                COALESCE(ar.product_name, p.prd_name) AS product_name,
                COALESCE(ar.actual_revenue, 0) AS actual_revenue,
                COALESCE(fr.forecast_revenue, 0) AS forecast_revenue,
                COALESCE(ar.actual_revenue, 0) - COALESCE(fr.forecast_revenue, 0) AS deviation,
                CASE
                    WHEN COALESCE(fr.forecast_revenue, 0) = 0 THEN 0
                    ELSE ((COALESCE(ar.actual_revenue, 0) - COALESCE(fr.forecast_revenue, 0)) / fr.forecast_revenue) * 100
                END AS deviation_percent
            FROM
                actual_revenue ar
            FULL OUTER JOIN
                forecast_revenue fr ON ar.product_id = fr.product_id
            LEFT JOIN
                products p ON COALESCE(ar.product_id, fr.product_id) = p.prd_sf_id
            WHERE
                COALESCE(ar.actual_revenue, 0) != 0 OR COALESCE(fr.forecast_revenue, 0) != 0
        )
        SELECT
            product_id,
            product_name,
            actual_revenue,
            forecast_revenue,
            deviation,
            deviation_percent
        FROM
            combined
        ORDER BY
            deviation DESC
        """
        
        # Build parameters list based on whether account_id is provided
        if account_id:
            params = [from_date, to_date, account_id, from_date, to_date, account_id]
        else:
            params = [from_date, to_date, from_date, to_date]
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Get top 3 performers (highest deviation)
        top_performers = results[:3]
        
        # Get bottom 3 performers (lowest deviation)
        bottom_performers = sorted(results, key=lambda x: x['deviation'])[:3]
        
        # Format response
        def format_product(product: Dict) -> Dict:
            return {
                'productId': product['product_id'],
                'productName': product['product_name'],
                'actualRevenue': float(product['actual_revenue']) if product['actual_revenue'] else 0.0,
                'forecastRevenue': float(product['forecast_revenue']) if product['forecast_revenue'] else 0.0,
                'deviation': float(product['deviation']) if product['deviation'] else 0.0,
                'deviationPercent': float(product['deviation_percent']) if product['deviation_percent'] else 0.0,
            }
        
        return {
            'topPerformers': [format_product(p) for p in top_performers],
            'bottomPerformers': [format_product(p) for p in bottom_performers],
        }


# -----------------------------------------------------------------------------
# Quarter boundaries for a given year (inclusive start/end dates)
# -----------------------------------------------------------------------------
QUARTER_RANGES = [
    (1, 3),   # Q1: Jan-Mar
    (4, 6),   # Q2: Apr-Jun
    (7, 9),   # Q3: Jul-Sep
    (10, 12), # Q4: Oct-Dec
]


def _quarter_start_end(year: int, q: int) -> Tuple[date, date]:
    """Return (start_date, end_date) for quarter 1-4 in given year."""
    start_month = (q - 1) * 3 + 1
    end_month = start_month + 2
    start = date(year, start_month, 1)
    last_day = monthrange(year, end_month)[1]
    end = date(year, end_month, last_day)
    return start, end


def _invoice_sum(
    account_id: str,
    start_date: date,
    end_date: date,
) -> Decimal:
    """Sum inv_net_price for account in date range; closed, valid, exclude credit notes."""
    qs = Invoice.objects.filter(
        inv_account_id=account_id,
        inv_invoice_date__gte=start_date,
        inv_invoice_date__lte=end_date,
        inv_status='Closed',
        inv_valid=True,
    ).exclude(
        inv_invoice_type='Credit Note'
    ).aggregate(total=Sum('inv_net_price'))
    total = qs.get('total')
    return total if total is not None else Decimal('0')


def _period_achieved(
    actual: Decimal,
    target: Decimal,
    currency_symbol: str = '£',
) -> Dict[str, Any]:
    """Build achieved block: target, actual, difference, percent, label."""
    target = target or Decimal('0')
    diff = actual - target
    if target and target != 0:
        pct = (actual / target) * 100
    else:
        pct = Decimal('100') if actual else Decimal('0')
    sym = currency_symbol or '£'
    if diff >= 0:
        label = f"Exceeded target by {sym}{diff:,.2f}" if diff else "On target"
    else:
        label = f"Below target by {sym}{abs(diff):,.2f}"
    return {
        'target': float(target),
        'actual': float(actual),
        'difference': float(diff),
        'percent': round(float(pct), 1),
        'label': label,
    }


def get_quarterly_performance(account_id: str, year: int) -> Dict[str, Any]:
    """
    Get Achieved and Rebate for each quarter and full year for the given account and year.

    Logic depends on frame agreement type:
    - Quarterly: target records per Q + year; compare invoice sums to targets; rebate from target.
    - Quarterly & Volume: same as Quarterly plus year volume target.
    - Growth: no target records; year rebate = max(0, (fa_total_sales_ty - fa_total_sales_ly) * 0.15); Q1–Q4 = 0.

    Returns structure with Q1, Q2, Q3, Q4, Year each having achieved and rebate; missing data as 0.
    """
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    currency_symbol = _currency_symbol_for_account(account_id)

    def zero_period(period_id: str) -> Dict[str, Any]:
        return {
            'period': period_id,
            'achieved': {
                'target': 0.0,
                'actual': 0.0,
                'difference': 0.0,
                'percent': 0.0,
                'label': 'No target',
            },
            'rebate': 0.0,
            'rebate_label': f'{currency_symbol}0',
        }

    result = {
        'accountId': account_id,
        'year': year,
        'currencySymbol': currency_symbol,
        'agreementType': None,
        'periods': {
            'Q1': zero_period('Q1'),
            'Q2': zero_period('Q2'),
            'Q3': zero_period('Q3'),
            'Q4': zero_period('Q4'),
            'Year': zero_period('Year'),
        },
    }

    # Find active frame agreement for this account covering the year
    fa = (
        FrameAgreement.objects.filter(
            fa_account_id=account_id,
            fa_active=1,
        ).filter(
            Q(fa_start_date__lte=year_end) & Q(fa_end_date__gte=year_start)
        ).first()
    )
    if not fa:
        return result

    result['agreementType'] = fa.fa_agreement_type or ''
    agreement_type = (fa.fa_agreement_type or '').strip()

    if agreement_type == 'Growth':
        # No target records; year rebate = max(0, (ty - ly) * 0.15)
        ty = (fa.fa_total_sales_ty or Decimal('0'))
        ly = (fa.fa_total_sales_ly or Decimal('0'))
        growth_rebate = max(Decimal('0'), (ty - ly) * Decimal('0.15'))
        result['periods']['Year'] = {
            'period': 'Year',
            'achieved': {
                'target': 0.0,
                'actual': float(ty),
                'difference': float(ty),
                'percent': 100.0,
                'label': 'Growth (no target)',
            },
            'rebate': float(growth_rebate),
            'rebate_label': f'{currency_symbol}{growth_rebate:,.2f} earned' if growth_rebate else f'{currency_symbol}0',
        }
        # Q1–Q4 remain zero
        return result

    # Quarterly or Quarterly & Volume: use targets and invoice sums
    targets = {
        t.tgt_quarter: t
        for t in Target.objects.filter(
            tgt_frame_agreement_id=fa.fa_sf_id,
            tgt_active=1,
        ).filter(
            tgt_quarter__in=['Q1', 'Q2', 'Q3', 'Q4', 'Year']
        )
    }

    # Invoice actuals per quarter and full year
    actuals = {}
    for q in range(1, 5):
        start_d, end_d = _quarter_start_end(year, q)
        actuals[f'Q{q}'] = _invoice_sum(account_id, start_d, end_d)
    actuals['Year'] = _invoice_sum(account_id, year_start, year_end)

    for period_id in ['Q1', 'Q2', 'Q3', 'Q4', 'Year']:
        actual = actuals.get(period_id, Decimal('0'))
        tgt = targets.get(period_id)
        target_val = tgt.tgt_net_turnover_target if tgt else Decimal('0')
        achieved = _period_achieved(actual, target_val, currency_symbol)
        rebate_val = Decimal('0')
        if tgt and actual >= target_val and target_val > 0:
            rebate_val = tgt.tgt_rebate_if_achieved or Decimal('0')
        result['periods'][period_id] = {
            'period': period_id,
            'achieved': achieved,
            'rebate': float(rebate_val),
            'rebate_label': f'{currency_symbol}{rebate_val:,.2f} earned' if rebate_val else f'{currency_symbol}0',
        }

    return result
