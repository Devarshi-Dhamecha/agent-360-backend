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
        to_date: str,
        search: str = None
    ) -> List[Dict]:
        """
        Get product family level analytics with actuals, last year, open sales, and RFC.
        
        Args:
            account_id: Salesforce Account ID
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            search: Optional search term to filter family names
            
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
                COALESCE(SUM(ili.ili_net_price), 0) AS actual_sales
            FROM
                products prd
            LEFT JOIN
                invoice_line_items ili ON ili.ili_product_id = prd.prd_sf_id AND ili.ili_active = 1
            LEFT JOIN
                invoices inv ON inv.inv_sf_id = ili.ili_invoice_id
            WHERE
                inv.inv_account_id = %s
                AND inv.inv_invoice_date BETWEEN %s AND %s
                AND inv.inv_active = 1
                AND prd.prd_active = 1
            GROUP BY
                prd.prd_family
        ),
        last_year AS (
            SELECT
                prd.prd_family AS family,
                COALESCE(SUM(ili.ili_net_price), 0) AS last_year_sales
            FROM
                products prd
            LEFT JOIN
                invoice_line_items ili ON ili.ili_product_id = prd.prd_sf_id AND ili.ili_active = 1
            LEFT JOIN
                invoices inv ON inv.inv_sf_id = ili.ili_invoice_id
            WHERE
                inv.inv_account_id = %s
                AND inv.inv_invoice_date BETWEEN %s AND %s
                AND inv.inv_active = 1
                AND prd.prd_active = 1
            GROUP BY
                prd.prd_family
        ),
        open_sales AS (
            SELECT
                prd.prd_family AS family,
                COALESCE(SUM(ori.ori_open_amount), 0) AS open_sales
            FROM
                products prd
            LEFT JOIN
                order_items ori ON ori.ori_product_id = prd.prd_sf_id AND ori.ori_active = 1
            LEFT JOIN
                orders ord ON ord.ord_sf_id = ori.ori_order_id
            WHERE
                ord.ord_account_id = %s
                AND ord.ord_effective_date BETWEEN %s AND %s
                AND ord.ord_status = 'Open'
                AND ord.ord_active = 1
                AND prd.prd_active = 1
            GROUP BY
                prd.prd_family
        ),
        rfc AS (
            SELECT
                prd.prd_family AS family,
                COALESCE(SUM(arf.arf_approved_quantity * arf.arf_approved_unit_price), 0) AS rfc_value
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
            COALESCE(a.family, ly.family, os.family, r.family) AS family,
            COALESCE(a.actual_sales, 0) AS actual_sales,
            COALESCE(os.open_sales, 0) AS open_sales,
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
            open_sales os ON COALESCE(a.family, ly.family) = os.family
        FULL OUTER JOIN
            rfc r ON COALESCE(a.family, ly.family, os.family) = r.family
        WHERE
            COALESCE(a.family, ly.family, os.family, r.family) IS NOT NULL
            {search_filter}
        ORDER BY
            family
        """
        
        params = [
            account_id, from_date, to_date,
            account_id, ly_from_date, ly_to_date,
            account_id, from_date, to_date,
            account_id, from_date, to_date
        ]
        
        # Add search filter if provided
        search_filter = ""
        if search:
            search_filter = "AND LOWER(COALESCE(a.family, ly.family, os.family, r.family)) LIKE %s"
            params.append(f"%{search.lower()}%")
        
        query = query.format(search_filter=search_filter)
        
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
        to_date: str,
        search: str = None,
        top_x: int = None
    ) -> List[Dict]:
        """
        Get product level analytics for a specific family.
        
        Args:
            account_id: Salesforce Account ID
            family: Product family name
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            search: Optional search term to filter product names
            top_x: Optional filter for top X products (5, 10, 20, 30)
            
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
                ili.ili_product_id AS product_id,
                prd.prd_name AS product_name,
                COALESCE(SUM(ili.ili_net_price), 0) AS actual_sales
            FROM
                invoice_line_items ili
            JOIN
                invoices inv ON inv.inv_sf_id = ili.ili_invoice_id
            JOIN
                products prd ON prd.prd_sf_id = ili.ili_product_id
            WHERE
                inv.inv_account_id = %s
                AND prd.prd_family = %s
                AND inv.inv_invoice_date BETWEEN %s AND %s
                AND inv.inv_active = 1
                AND ili.ili_active = 1
                AND prd.prd_active = 1
            GROUP BY
                ili.ili_product_id, prd.prd_name
        ),
        last_year AS (
            SELECT
                ili.ili_product_id AS product_id,
                COALESCE(SUM(ili.ili_net_price), 0) AS last_year_sales
            FROM
                invoice_line_items ili
            JOIN
                invoices inv ON inv.inv_sf_id = ili.ili_invoice_id
            JOIN
                products prd ON prd.prd_sf_id = ili.ili_product_id
            WHERE
                inv.inv_account_id = %s
                AND prd.prd_family = %s
                AND inv.inv_invoice_date BETWEEN %s AND %s
                AND inv.inv_active = 1
                AND ili.ili_active = 1
                AND prd.prd_active = 1
            GROUP BY
                ili.ili_product_id
        ),
        open_sales AS (
            SELECT
                ori.ori_product_id AS product_id,
                COALESCE(SUM(ori.ori_open_amount), 0) AS open_sales
            FROM
                order_items ori
            JOIN
                orders ord ON ord.ord_sf_id = ori.ori_order_id
            JOIN
                products prd ON prd.prd_sf_id = ori.ori_product_id
            WHERE
                ord.ord_account_id = %s
                AND prd.prd_family = %s
                AND ord.ord_effective_date BETWEEN %s AND %s
                AND ord.ord_status = 'Open'
                AND ord.ord_active = 1
                AND ori.ori_active = 1
                AND prd.prd_active = 1
            GROUP BY
                ori.ori_product_id
        ),
        rfc AS (
            SELECT
                arf.arf_product_id AS product_id,
                COALESCE(SUM(arf.arf_approved_quantity * arf.arf_approved_unit_price), 0) AS rfc_value
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
            COALESCE(a.product_id, ly.product_id, os.product_id, r.product_id) AS product_id,
            COALESCE(a.product_name, p.prd_name) AS product_name,
            COALESCE(a.actual_sales, 0) AS actual_sales,
            COALESCE(os.open_sales, 0) AS open_sales,
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
            open_sales os ON COALESCE(a.product_id, ly.product_id) = os.product_id
        FULL OUTER JOIN
            rfc r ON COALESCE(a.product_id, ly.product_id, os.product_id) = r.product_id
        LEFT JOIN
            products p ON COALESCE(a.product_id, ly.product_id, os.product_id, r.product_id) = p.prd_sf_id
        WHERE
            COALESCE(a.product_id, ly.product_id, os.product_id, r.product_id) IS NOT NULL
            {search_filter}
        ORDER BY
            actual_sales DESC
        """
        
        params = [
            account_id, family, from_date, to_date,
            account_id, family, ly_from_date, ly_to_date,
            account_id, family, from_date, to_date,
            account_id, family, from_date, to_date
        ]
        
        # Add search filter if provided
        search_filter = ""
        if search:
            search_filter = "AND LOWER(COALESCE(a.product_name, p.prd_name)) LIKE %s"
            params.append(f"%{search.lower()}%")
        
        query = query.format(search_filter=search_filter)
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Convert to list of dictionaries
        product_list = [
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
        
        # Apply TopX filter if provided
        if top_x:
            # Define ranges: 5→1-5, 10→1-10, 20→11-20, 30→21-30
            if top_x == 5:
                product_list = product_list[0:5]
            elif top_x == 10:
                product_list = product_list[0:10]
            elif top_x == 20:
                product_list = product_list[10:20]
            elif top_x == 30:
                product_list = product_list[20:30]
        
        return product_list
    
    @staticmethod
    def get_order_contribution(
        account_id: str,
        product_id: str,
        from_date: str,
        to_date: str,
        search: str = None
    ) -> List[Dict]:
        """
        Get order contribution for a specific product.
        
        Args:
            account_id: Salesforce Account ID
            product_id: Product Salesforce ID
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            search: Optional search term to filter order numbers
            
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
            order_items ori
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
        {search_filter}
        ORDER BY
            ord.ord_order_number
        """
        
        params = [account_id, product_id, from_date, to_date]
        
        # Add search filter if provided
        search_filter = ""
        if search:
            search_filter = "HAVING LOWER(ord.ord_order_number) LIKE %s"
            params.append(f"%{search.lower()}%")
        
        query = query.format(search_filter=search_filter)
        
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
        to_date: str,
        search: str = None
    ) -> Dict:
        """
        Get all product details for a specific order including order information.
        
        Args:
            account_id: Salesforce Account ID
            order_id: Order Salesforce ID
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            search: Optional search term to filter product names
            
        Returns:
            Dictionary with order information and list of products
        """
        query = """
        SELECT
            ord.ord_sf_id AS order_id,
            ord.ord_order_number AS order_number,
            ord.ord_status AS order_status,
            ord.ord_effective_date AS order_effective_date,
            ord.ord_end_date AS order_end_date,
            ord.ord_type AS order_type,
            ord.ord_total_amount AS order_total_amount,
            ord.ord_currency_iso_code AS order_currency_iso_code,
            ori.ori_product_id AS product_id,
            prd.prd_name AS product_name,
            ori.ori_status AS status,
            COALESCE(SUM(ori.ori_ordered_quantity), 0) AS ordered_quantity,
            COALESCE(SUM(ori.ori_ordered_amount), 0) AS ordered_amount,
            COALESCE(SUM(ori.ori_open_quantity), 0) AS open_quantity,
            COALESCE(SUM(ori.ori_open_amount), 0) AS open_amount
        FROM
            order_items ori
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
            ord.ord_sf_id, ord.ord_order_number, ord.ord_status, 
            ord.ord_effective_date, ord.ord_end_date, ord.ord_type,
            ord.ord_total_amount, ord.ord_currency_iso_code,
            ori.ori_product_id, prd.prd_name, ori.ori_status
        {search_filter}
        ORDER BY
            prd.prd_name
        """
        
        params = [account_id, order_id, from_date, to_date]
        
        # Add search filter if provided
        search_filter = ""
        if search:
            search_filter = "HAVING LOWER(prd.prd_name) LIKE %s"
            params.append(f"%{search.lower()}%")
        
        query = query.format(search_filter=search_filter)
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # If no results, return None
        if not results:
            return None
        
        # Extract order information from first row
        first_row = results[0]
        order_info = {
            'orderId': first_row['order_id'],
            'orderNumber': first_row['order_number'],
            'orderStatus': first_row['order_status'] or 'Unknown',
            'orderEffectiveDate': first_row['order_effective_date'],
            'orderEndDate': first_row['order_end_date'],
            'orderType': first_row['order_type'],
            'orderTotalAmount': float(first_row['order_total_amount']) if first_row['order_total_amount'] else None,
            'orderCurrencyIsoCode': first_row['order_currency_iso_code'],
            'products': []
        }
        
        # Add all products to the order
        for row in results:
            order_info['products'].append({
                'productId': row['product_id'],
                'productName': row['product_name'] or 'Unknown',
                'status': row['status'] or 'Unknown',
                'orderedQuantity': float(row['ordered_quantity']) if row['ordered_quantity'] else 0.0,
                'orderedAmount': float(row['ordered_amount']) if row['ordered_amount'] else 0.0,
                'openQuantity': float(row['open_quantity']) if row['open_quantity'] else 0.0,
                'openAmount': float(row['open_amount']) if row['open_amount'] else 0.0,
            })
        
        return order_info
