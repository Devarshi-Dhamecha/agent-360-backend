"""
Analytics Tests

Test cases for analytics API functionality.
"""
from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.products.models import Product
from apps.accounts.models import Account
from apps.invoices.models import Invoice, InvoiceLineItem
from apps.forecasts.models import Forecast
from .services import AnalyticsService

User = get_user_model()


class AnalyticsServiceTestCase(TestCase):
    """Test cases for AnalyticsService"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test account
        self.account = Account.objects.create(
            id='ACC001',
            name='Test Account',
            owner=self.user,
            last_modified_by=self.user
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            id='PROD001',
            name='Product 1',
            family='Herbicides',
            created_by=self.user,
            last_modified_by=self.user
        )
        
        self.product2 = Product.objects.create(
            id='PROD002',
            name='Product 2',
            family='Herbicides',
            created_by=self.user,
            last_modified_by=self.user
        )
        
        self.product3 = Product.objects.create(
            id='PROD003',
            name='Product 3',
            family='Fungicides',
            created_by=self.user,
            last_modified_by=self.user
        )
    
    def test_validate_valid_family_level(self):
        """Test validation with valid family level parameters"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10'
        )
        
        is_valid, error = service.validate()
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_invalid_level(self):
        """Test validation with invalid level"""
        service = AnalyticsService(
            level='invalid',
            start_month='2025-03',
            end_month='2025-10'
        )
        
        is_valid, error = service.validate()
        self.assertFalse(is_valid)
        self.assertIn('Invalid level', error)
    
    def test_validate_product_level_without_parent_id(self):
        """Test validation for product level without parent_id"""
        service = AnalyticsService(
            level='product',
            start_month='2025-03',
            end_month='2025-10'
        )
        
        is_valid, error = service.validate()
        self.assertFalse(is_valid)
        self.assertIn('parent_id is required', error)
    
    def test_validate_invalid_month_format(self):
        """Test validation with invalid month format"""
        service = AnalyticsService(
            level='family',
            start_month='2025/03',
            end_month='2025-10'
        )
        
        is_valid, error = service.validate()
        self.assertFalse(is_valid)
        self.assertIn('Invalid month format', error)
    
    def test_get_date_range(self):
        """Test date range conversion from month strings"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10'
        )
        
        start_date, end_date = service.get_date_range()
        
        self.assertEqual(start_date, date(2025, 3, 1))
        self.assertEqual(end_date, date(2025, 10, 31))
    
    def test_get_last_year_date_range(self):
        """Test last year date range calculation"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10'
        )
        
        last_year_start, last_year_end = service.get_last_year_date_range()
        
        self.assertEqual(last_year_start, date(2024, 3, 1))
        self.assertEqual(last_year_end, date(2024, 10, 31))
    
    def test_compute_deviation_percent_positive(self):
        """Test deviation calculation with positive deviation"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10'
        )
        
        deviation = service.compute_deviation_percent(
            Decimal('110'),
            Decimal('100')
        )
        
        self.assertEqual(deviation, 10.0)
    
    def test_compute_deviation_percent_negative(self):
        """Test deviation calculation with negative deviation"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10'
        )
        
        deviation = service.compute_deviation_percent(
            Decimal('90'),
            Decimal('100')
        )
        
        self.assertEqual(deviation, -10.0)
    
    def test_compute_deviation_percent_zero_rfc(self):
        """Test deviation calculation with zero RFC"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10'
        )
        
        deviation = service.compute_deviation_percent(
            Decimal('100'),
            Decimal('0')
        )
        
        self.assertEqual(deviation, 0.0)
    
    def test_merge_data(self):
        """Test data merging from multiple sources"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10'
        )
        
        actual_data = [
            {'family': 'Herbicides', 'actual_sales': Decimal('1000')}
        ]
        rfc_data = [
            {'family': 'Herbicides', 'rfc': Decimal('900')}
        ]
        last_year_data = [
            {'family': 'Herbicides', 'last_year_sales': Decimal('800')}
        ]
        
        merged = service.merge_data(actual_data, rfc_data, last_year_data, 'family')
        
        self.assertIn('Herbicides', merged)
        self.assertEqual(merged['Herbicides']['actual_sales'], Decimal('1000'))
        self.assertEqual(merged['Herbicides']['rfc'], Decimal('900'))
        self.assertEqual(merged['Herbicides']['last_year_sales'], Decimal('800'))
    
    def test_apply_ordering_descending(self):
        """Test ordering results in descending order"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10',
            ordering='-actual_sales'
        )
        
        results = [
            {'name': 'A', 'actual_sales': 100},
            {'name': 'B', 'actual_sales': 300},
            {'name': 'C', 'actual_sales': 200}
        ]
        
        ordered = service.apply_ordering_and_limit(results)
        
        self.assertEqual(ordered[0]['name'], 'B')
        self.assertEqual(ordered[1]['name'], 'C')
        self.assertEqual(ordered[2]['name'], 'A')
    
    def test_apply_ordering_ascending(self):
        """Test ordering results in ascending order"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10',
            ordering='actual_sales'
        )
        
        results = [
            {'name': 'A', 'actual_sales': 100},
            {'name': 'B', 'actual_sales': 300},
            {'name': 'C', 'actual_sales': 200}
        ]
        
        ordered = service.apply_ordering_and_limit(results)
        
        self.assertEqual(ordered[0]['name'], 'A')
        self.assertEqual(ordered[1]['name'], 'C')
        self.assertEqual(ordered[2]['name'], 'B')
    
    def test_apply_top_n_limit(self):
        """Test applying top_n limit"""
        service = AnalyticsService(
            level='family',
            start_month='2025-03',
            end_month='2025-10',
            ordering='-actual_sales',
            top_n=2
        )
        
        results = [
            {'name': 'A', 'actual_sales': 100},
            {'name': 'B', 'actual_sales': 300},
            {'name': 'C', 'actual_sales': 200}
        ]
        
        limited = service.apply_ordering_and_limit(results)
        
        self.assertEqual(len(limited), 2)
        self.assertEqual(limited[0]['name'], 'B')
        self.assertEqual(limited[1]['name'], 'C')


class AnalyticsAPITestCase(TestCase):
    """Test cases for Analytics API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_get_analytics_missing_required_params(self):
        """Test API call with missing required parameters"""
        response = self.client.get('/api/analytics/')
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
    
    def test_get_analytics_invalid_level(self):
        """Test API call with invalid level"""
        response = self.client.get('/api/analytics/', {
            'level': 'invalid',
            'start_month': '2025-03',
            'end_month': '2025-10'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
    
    def test_get_analytics_product_level_without_parent_id(self):
        """Test API call for product level without parent_id"""
        response = self.client.get('/api/analytics/', {
            'level': 'product',
            'start_month': '2025-03',
            'end_month': '2025-10'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
