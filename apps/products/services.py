"""
Product Performance Service Layer.
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Tuple
from calendar import monthrange

from django.db import connection


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
