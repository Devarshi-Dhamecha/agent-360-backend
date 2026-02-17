"""
Analytics Service Layer

Business logic for analytics aggregation and computation.
"""
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import calendar

from . import selectors


class AnalyticsService:
    """Service for analytics data aggregation and processing"""
    
    VALID_LEVELS = ['family', 'product', 'invoice']
    
    def __init__(
        self,
        level: str,
        start_month: str,
        end_month: str,
        parent_id: Optional[str] = None,
        top_n: Optional[int] = None,
        ordering: Optional[str] = None
    ):
        """
        Initialize analytics service.
        
        Args:
            level: Aggregation level (family, product, invoice)
            start_month: Start month in YYYY-MM format
            end_month: End month in YYYY-MM format
            parent_id: Parent ID for drill-down (required for product and invoice)
            top_n: Limit results to top N
            ordering: Field to order by (prefix with - for descending)
        """
        self.level = level
        self.start_month = start_month
        self.end_month = end_month
        self.parent_id = parent_id
        self.top_n = top_n
        self.ordering = ordering or '-actual_sales'
        
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.level not in self.VALID_LEVELS:
            return False, f"Invalid level. Must be one of: {', '.join(self.VALID_LEVELS)}"
        
        if self.level in ['product', 'invoice'] and not self.parent_id:
            return False, f"parent_id is required for level '{self.level}'"
        
        try:
            datetime.strptime(self.start_month, '%Y-%m')
            datetime.strptime(self.end_month, '%Y-%m')
        except ValueError:
            return False, "Invalid month format. Use YYYY-MM"
        
        return True, None
    
    def get_date_range(self) -> Tuple[date, date]:
        """
        Convert month strings to date range.
        
        Returns:
            Tuple of (start_date, end_date)
        """
        start_date = datetime.strptime(self.start_month, '%Y-%m').date()
        
        end_year, end_month = map(int, self.end_month.split('-'))
        last_day = calendar.monthrange(end_year, end_month)[1]
        end_date = date(end_year, end_month, last_day)
        
        return start_date, end_date
    
    def get_last_year_date_range(self) -> Tuple[date, date]:
        """
        Get date range for last year period.
        
        Returns:
            Tuple of (last_year_start_date, last_year_end_date)
        """
        start_date, end_date = self.get_date_range()
        
        last_year_start = start_date - relativedelta(years=1)
        last_year_end = end_date - relativedelta(years=1)
        
        return last_year_start, last_year_end
    
    def compute_deviation_percent(self, actual: Decimal, rfc: Decimal) -> float:
        """
        Compute deviation percentage.
        
        Formula: ((actual - rfc) / rfc) * 100 if rfc > 0, else 0
        
        Args:
            actual: Actual sales value
            rfc: RFC value
            
        Returns:
            Deviation percentage rounded to 2 decimals
        """
        if rfc > 0:
            return round(float((actual - rfc) / rfc * 100), 2)
        return 0.0
    
    def merge_data(
        self,
        actual_data: List[Dict],
        rfc_data: List[Dict],
        last_year_data: List[Dict],
        key_field: str
    ) -> Dict[str, Dict]:
        """
        Merge actual, rfc, and last year data by key field.
        
        Args:
            actual_data: List of actual sales records
            rfc_data: List of RFC records
            last_year_data: List of last year sales records
            key_field: Field name to use as key for merging
            
        Returns:
            Dict mapping key to merged data
        """
        merged = {}
        
        # Merge actual sales
        for record in actual_data:
            key = record[key_field]
            merged[key] = {
                **record,
                'actual_sales': record.get('actual_sales', Decimal('0')),
                'rfc': Decimal('0'),
                'last_year_sales': Decimal('0')
            }
        
        # Merge RFC
        for record in rfc_data:
            key = record[key_field]
            if key not in merged:
                merged[key] = {
                    key_field: key,
                    'actual_sales': Decimal('0'),
                    'rfc': record.get('rfc', Decimal('0')),
                    'last_year_sales': Decimal('0')
                }
            else:
                merged[key]['rfc'] = record.get('rfc', Decimal('0'))
        
        # Merge last year sales
        for record in last_year_data:
            key = record[key_field]
            if key not in merged:
                merged[key] = {
                    key_field: key,
                    'actual_sales': Decimal('0'),
                    'rfc': Decimal('0'),
                    'last_year_sales': record.get('last_year_sales', Decimal('0'))
                }
            else:
                merged[key]['last_year_sales'] = record.get('last_year_sales', Decimal('0'))
        
        return merged
    
    def apply_ordering_and_limit(self, results: List[Dict]) -> List[Dict]:
        """
        Apply ordering and top_n limit to results.
        
        Args:
            results: List of result records
            
        Returns:
            Ordered and limited results
        """
        # Determine sort field and direction
        reverse = self.ordering.startswith('-')
        sort_field = self.ordering.lstrip('-')
        
        # Sort results
        sorted_results = sorted(
            results,
            key=lambda x: x.get(sort_field, 0),
            reverse=reverse
        )
        
        # Apply top_n limit
        if self.top_n:
            sorted_results = sorted_results[:self.top_n]
        
        return sorted_results
    
    def get_analytics(self) -> Dict:
        """
        Get analytics data based on level.
        
        Returns:
            Dict containing analytics results
        """
        start_date, end_date = self.get_date_range()
        last_year_start, last_year_end = self.get_last_year_date_range()
        
        if self.level == 'family':
            return self._get_family_analytics(start_date, end_date, last_year_start, last_year_end)
        elif self.level == 'product':
            return self._get_product_analytics(start_date, end_date, last_year_start, last_year_end)
        else:  # invoice
            return self._get_invoice_analytics(start_date, end_date, last_year_start, last_year_end)
    
    def _get_family_analytics(
        self,
        start_date: date,
        end_date: date,
        last_year_start: date,
        last_year_end: date
    ) -> Dict:
        """Get analytics aggregated by product family"""
        actual_data = selectors.get_family_actual_sales(start_date, end_date)
        rfc_data = selectors.get_family_rfc(start_date, end_date)
        last_year_data = selectors.get_family_last_year_sales(last_year_start, last_year_end)
        
        merged = self.merge_data(actual_data, rfc_data, last_year_data, 'family')
        
        results = []
        for family, data in merged.items():
            if not family:  # Skip null families
                continue
            
            actual = data['actual_sales']
            rfc = data['rfc']
            last_year = data['last_year_sales']
            
            results.append({
                'id': family,
                'name': family,
                'status': None,
                'actual_sales': float(actual),
                'rfc': float(rfc),
                'last_year_sales': float(last_year),
                'deviation_percent': self.compute_deviation_percent(actual, rfc),
                'is_drillable': True
            })
        
        results = self.apply_ordering_and_limit(results)
        
        return self._format_response(results)
    
    def _get_product_analytics(
        self,
        start_date: date,
        end_date: date,
        last_year_start: date,
        last_year_end: date
    ) -> Dict:
        """Get analytics aggregated by product"""
        actual_data = selectors.get_product_actual_sales(self.parent_id, start_date, end_date)
        rfc_data = selectors.get_product_rfc(self.parent_id, start_date, end_date)
        last_year_data = selectors.get_product_last_year_sales(self.parent_id, last_year_start, last_year_end)
        
        merged = self.merge_data(actual_data, rfc_data, last_year_data, 'product_id')
        
        results = []
        for product_id, data in merged.items():
            if not product_id:
                continue
            
            actual = data['actual_sales']
            rfc = data['rfc']
            last_year = data['last_year_sales']
            
            results.append({
                'id': product_id,
                'name': data.get('product_name', product_id),
                'status': None,
                'actual_sales': float(actual),
                'rfc': float(rfc),
                'last_year_sales': float(last_year),
                'deviation_percent': self.compute_deviation_percent(actual, rfc),
                'is_drillable': True
            })
        
        results = self.apply_ordering_and_limit(results)
        
        return self._format_response(results)
    
    def _get_invoice_analytics(
        self,
        start_date: date,
        end_date: date,
        last_year_start: date,
        last_year_end: date
    ) -> Dict:
        """Get analytics aggregated by invoice"""
        actual_data = selectors.get_invoice_actual_sales(self.parent_id, start_date, end_date)
        rfc_data = selectors.get_invoice_rfc(self.parent_id, start_date, end_date)
        last_year_data = selectors.get_invoice_last_year_sales(self.parent_id, last_year_start, last_year_end)
        
        # For invoices, RFC is at product level, so we'll use a single RFC value
        total_rfc = sum(r.get('rfc', Decimal('0')) for r in rfc_data)
        
        merged = self.merge_data(actual_data, [], last_year_data, 'invoice_id')
        
        results = []
        for invoice_id, data in merged.items():
            if not invoice_id:
                continue
            
            actual = data['actual_sales']
            last_year = data['last_year_sales']
            
            results.append({
                'id': invoice_id,
                'name': data.get('invoice_number', invoice_id),
                'status': data.get('invoice_status'),
                'actual_sales': float(actual),
                'rfc': float(total_rfc) if len(merged) == 1 else 0.0,  # Simplified RFC distribution
                'last_year_sales': float(last_year),
                'deviation_percent': self.compute_deviation_percent(actual, total_rfc) if len(merged) == 1 else 0.0,
                'is_drillable': False
            })
        
        results = self.apply_ordering_and_limit(results)
        
        return self._format_response(results)
    
    def _format_response(self, results: List[Dict]) -> Dict:
        """
        Format final response with totals and chart data.
        
        Args:
            results: List of result records
            
        Returns:
            Formatted response dict
        """
        total_actual = sum(r['actual_sales'] for r in results)
        total_rfc = sum(r['rfc'] for r in results)
        total_last_year = sum(r['last_year_sales'] for r in results)
        
        chart_data = [
            {'label': r['name'], 'value': r['actual_sales']}
            for r in results
        ]
        
        return {
            'level': self.level,
            'start_month': self.start_month,
            'end_month': self.end_month,
            'total_actual_sales': total_actual,
            'total_rfc': total_rfc,
            'total_last_year_sales': total_last_year,
            'chart_data': chart_data,
            'results': results
        }
