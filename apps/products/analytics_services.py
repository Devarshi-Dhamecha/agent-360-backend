"""
Sales Analytics Service Layer.
"""
from datetime import datetime
from calendar import monthrange
from typing import Dict, List, Tuple
from decimal import Decimal

from django.db import connection


class SalesAnalyticsService:
    """Service for sales analytics calculations."""
    
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
    def get_product_family_analytics(
        account_id: str,
        from_date: str,
        to_date: str
    ) -> List[Dict]:
        """
        Get product family level analytics with actuals, last year, and RFC.
        
        Args:
            account_id: Salesforce Account ID
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            List of product family analytics
        """
        # Calculate last year dates
        from_year = int(from_date.split('-')[0])
        to_year = int(to_date.split('-')[0])
        ly_from_date = f"{from_year - 1}{from_date[4:]}"
        ly_to_date = f"{to_year - 1}{to_date[4:]}"
        
        query = """
        WITH actuals AS (
            SELECT
                prd.prd_family AS family,
                COALESCE(SUM(ori.ori_ordered_amount), 0) AS actual_sales,
                COALESCE(SUM(ori.ori_open_amount), 0) AS open_sales
            FROM
                products prd
            LEFT JOIN
                order_line_items ori ON ori.ori_product_id = prd.prd_sf_id AND ori.ori_active = 1
            LEFT JOIN
                orders ord ON ord.ord_sf_id = ori.ori_order_id
            WHERE
                ord.ord_account_id = %s
                AND ord.ord_effective_date BETWEEN %s AND %s
                AND ord.ord_active = 1
                AND prd.prd_active = 1
            GROUP BY
                prd.prd_family
        ),
        last_year AS (
            SELECT
                prd.prd_family AS family,
                COALESCE(SUM(ori.ori_ordered_amount), 0) AS last_year_sales
            FROM
                products prd
            LEFT JOIN
                order_line_items ori ON ori.ori_product_id = prd.prd_sf_id AND ori.ori_active = 1
            LEFT JOIN
                orders ord ON ord.ord_sf_id = ori.ori_order_id
            WHERE
                ord.ord_account_id = %s
                AND ord.ord_effective_date BETWEEN %s AND %s
                AND ord.ord_active = 1
                AND prd.prd_active = 1
            GROUP BY
                prd.prd_family
        ),
        rfc AS (
            SELECT
                prd.prd_family AS family,
                COALESCE(SUM(arf.arf_approved_value), 0) AS rfc_value
            FROM
                arf_rolling_forecasts arf
            JOIN
                products prd ON prd.prd_sf_id = arf.arf_product_id
            WHERE
                arf.arf_account_id = %s
                AND arf.arf_status = 'Approved'
                AND arf.arf_forecast_date BETWEEN %s AND %s
                AND arf.arf_active = 1
                AND prd.prd_active = 1
            GROUP BY
                prd.prd_family
        )
        SELECT
            COALESCE(a.family, ly.family, r.family) AS family,
            COALESCE(a.actual_sales, 0) AS actual_sales,
            COALESCE(a.open_sales, 0) AS open_sales,
            COALESCE(ly.last_year_sales, 0) AS last_year_sales,
            COALESCE(r.rfc_value, 0) AS rfc,
            CASE
                WHEN COALESCE(r.rfc_value, 0) = 0 THEN 0
                ELSE ((COALESCE(a.actual_sales, 0) - COALESCE(r.rfc_value, 0)) / r.rfc_value) * 100
            END AS deviation_percent
        FROM
            actuals a
        FULL OUTER JOIN
            last_year ly ON a.family = ly.family
        FULL OUTER JOIN
            rfc r ON COALESCE(a.family, ly.family) = r.family
        WHERE
            COALESCE(a.family, ly.family, r.family) IS NOT NULL
        ORDER BY
            family
        """
        
        params = [
            account_id, from_date, to_date,
            account_id, ly_from_date, ly_to_date,
            account_id, from_date, to_date
        ]
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return [
            {
                'family': row['family'] or 'Unknown',
                'actualSales': float(row['actual_sales']) if row['actual_sales'] else 0.0,
                'openSales': float(row['open_sales']) if row['open_sales'] else 0.0,
                'lastYearSales': float(row['last_year_sales']) if row['last_year_sales'] else 0.0,
                'rfc': float(row['rfc']) if row['rfc'] else 0.0,
                'deviationPercent': float(row['deviation_percent']) if row['deviation_percent'] else 0.0,
            }
            for row in results
        ]
    
    @staticmethod
    def get_product_analytics(
        account_id: str,
        family: str,
        from_date: str,
        to_date: str
    ) -> List[Dict]:
        """
        Get product level analytics for a specific family.
        
        Args:
            account_id: Salesforce Account ID
            family: Product family name
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            List of product analytics
        """
        # Calculate last year dates
        from_year = int(from_date.split('-')[0])
        to_year = int(to_date.split('-')[0])
        ly_from_date = f"{from_year - 1}{from_date[4:]}"
        ly_to_date = f"{to_year - 1}{to_date[4:]}"
        
        query = """
        WITH actuals AS (
            SELECT
                ori.ori_product_id AS product_id,
                prd.prd_name AS product_name,
                COALESCE(SUM(ori.ori_ordered_amount), 0) AS actual_sales,
                COALESCE(SUM(ori.ori_open_amount), 0) AS open_sales
            FROM
                order_line_items ori
            JOIN
                orders ord ON ord.ord_sf_id = ori.ori_order_id
            JOIN
                products prd ON prd.prd_sf_id = ori.ori_product_id
            WHERE
                ord.ord_account_id = %s
                AND prd.prd_family = %s
                AND ord.ord_effective_date BETWEEN %s AND %s
                AND ord.ord_active = 1
                AND ori.ori_active = 1
                AND prd.prd_active = 1
            GROUP BY
                ori.ori_product_id, prd.prd_name
        ),
        last_year AS (
            SELECT
                ori.ori_product_id AS product_id,
                COALESCE(SUM(ori.ori_ordered_amount), 0) AS last_year_sales
            FROM
                order_line_items ori
            JOIN
                orders ord ON ord.ord_sf_id = ori.ori_order_id
            JOIN
                products prd ON prd.prd_sf_id = ori.ori_product_id
            WHERE
                ord.ord_account_id = %s
                AND prd.prd_family = %s
                AND ord.ord_effective_date BETWEEN %s AND %s
                AND ord.ord_active = 1
                AND ori.ori_active = 1
                AND prd.prd_active = 1
            GROUP BY
                ori.ori_product_id
        ),
        rfc AS (
            SELECT
                arf.arf_product_id AS product_id,
                COALESCE(SUM(arf.arf_approved_value), 0) AS rfc_value
            FROM
                arf_rolling_forecasts arf
            JOIN
                products prd ON prd.prd_sf_id = arf.arf_product_id
            WHERE
                arf.arf_account_id = %s
                AND prd.prd_family = %s
                AND arf.arf_status = 'Approved'
                AND arf.arf_forecast_date BETWEEN %s AND %s
                AND arf.arf_active = 1
                AND prd.prd_active = 1
            GROUP BY
                arf.arf_product_id
        )
        SELECT
            COALESCE(a.product_id, ly.product_id, r.product_id) AS product_id,
            COALESCE(a.product_name, p.prd_name) AS product_name,
            COALESCE(a.actual_sales, 0) AS actual_sales,
            COALESCE(a.open_sales, 0) AS open_sales,
            COALESCE(ly.last_year_sales, 0) AS last_year_sales,
            COALESCE(r.rfc_value, 0) AS rfc,
            CASE
                WHEN COALESCE(r.rfc_value, 0) = 0 THEN 0
                ELSE ((COALESCE(a.actual_sales, 0) - COALESCE(r.rfc_value, 0)) / r.rfc_value) * 100
            END AS deviation_percent
        FROM
            actuals a
        FULL OUTER JOIN
            last_year ly ON a.product_id = ly.product_id
        FULL OUTER JOIN
            rfc r ON COALESCE(a.product_id, ly.product_id) = r.product_id
        LEFT JOIN
            products p ON COALESCE(a.product_id, ly.product_id, r.product_id) = p.prd_sf_id
        WHERE
            COALESCE(a.product_id, ly.product_id, r.product_id) IS NOT NULL
        ORDER BY
            product_name
        """
        
        params = [
            account_id, family, from_date, to_date,
            account_id, family, ly_from_date, ly_to_date,
            account_id, family, from_date, to_date
        ]
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return [
            {
                'productId': row['product_id'],
                'productName': row['product_name'] or 'Unknown',
                'actualSales': float(row['actual_sales']) if row['actual_sales'] else 0.0,
                'openSales': float(row['open_sales']) if row['open_sales'] else 0.0,
                'lastYearSales': float(row['last_year_sales']) if row['last_year_sales'] else 0.0,
                'rfc': float(row['rfc']) if row['rfc'] else 0.0,
                'deviationPercent': float(row['deviation_percent']) if row['deviation_percent'] else 0.0,
            }
            for row in results
        ]
    
    @staticmethod
    def get_order_contribution(
        account_id: str,
        product_id: str,
        from_date: str,
        to_date: str
    ) -> List[Dict]:
        """
        Get order contribution for a specific product.
        
        Args:
            account_id: Salesforce Account ID
            product_id: Product Salesforce ID
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            List of order contributions
        """
        query = """
        SELECT
            ori.ori_order_id AS order_id,
            ord.ord_order_number AS order_number,
            ord.ord_status AS order_status,
            COALESCE(SUM(ori.ori_ordered_quantity), 0) AS ordered_quantity,
            COALESCE(SUM(ori.ori_ordered_amount), 0) AS ordered_amount,
            COALESCE(SUM(ori.ori_open_quantity), 0) AS open_quantity,
            COALESCE(SUM(ori.ori_open_amount), 0) AS open_amount
        FROM
            order_line_items ori
        JOIN
            orders ord ON ord.ord_sf_id = ori.ori_order_id
        WHERE
            ord.ord_account_id = %s
            AND ori.ori_product_id = %s
            AND ord.ord_effective_date BETWEEN %s AND %s
            AND ord.ord_active = 1
            AND ori.ori_active = 1
        GROUP BY
            ori.ori_order_id, ord.ord_order_number, ord.ord_status
        ORDER BY
            ord.ord_order_number
        """
        
        params = [account_id, product_id, from_date, to_date]
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return [
            {
                'orderId': row['order_id'],
                'orderNumber': row['order_number'],
                'orderStatus': row['order_status'] or 'Unknown',
                'orderedQuantity': float(row['ordered_quantity']) if row['ordered_quantity'] else 0.0,
                'orderedAmount': float(row['ordered_amount']) if row['ordered_amount'] else 0.0,
                'openQuantity': float(row['open_quantity']) if row['open_quantity'] else 0.0,
                'openAmount': float(row['open_amount']) if row['open_amount'] else 0.0,
            }
            for row in results
        ]
    
    @staticmethod
    def get_order_details(
        account_id: str,
        order_id: str,
        from_date: str,
        to_date: str
    ) -> List[Dict]:
        """
        Get all product details for a specific order.
        
        Args:
            account_id: Salesforce Account ID
            order_id: Order Salesforce ID
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            List of order line item details
        """
        query = """
        SELECT
            ori.ori_product_id AS product_id,
            prd.prd_name AS product_name,
            ori.ori_status AS status,
            COALESCE(SUM(ori.ori_ordered_quantity), 0) AS ordered_quantity,
            COALESCE(SUM(ori.ori_ordered_amount), 0) AS ordered_amount,
            COALESCE(SUM(ori.ori_open_quantity), 0) AS open_quantity,
            COALESCE(SUM(ori.ori_open_amount), 0) AS open_amount
        FROM
            order_line_items ori
        JOIN
            orders ord ON ord.ord_sf_id = ori.ori_order_id
        JOIN
            products prd ON prd.prd_sf_id = ori.ori_product_id
        WHERE
            ord.ord_account_id = %s
            AND ori.ori_order_id = %s
            AND ord.ord_effective_date BETWEEN %s AND %s
            AND ord.ord_active = 1
            AND ori.ori_active = 1
            AND prd.prd_active = 1
        GROUP BY
            ori.ori_product_id, prd.prd_name, ori.ori_status
        ORDER BY
            prd.prd_name
        """
        
        params = [account_id, order_id, from_date, to_date]
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return [
            {
                'productId': row['product_id'],
                'productName': row['product_name'] or 'Unknown',
                'status': row['status'] or 'Unknown',
                'orderedQuantity': float(row['ordered_quantity']) if row['ordered_quantity'] else 0.0,
                'orderedAmount': float(row['ordered_amount']) if row['ordered_amount'] else 0.0,
                'openQuantity': float(row['open_quantity']) if row['open_quantity'] else 0.0,
                'openAmount': float(row['open_amount']) if row['open_amount'] else 0.0,
            }
            for row in results
        ]
