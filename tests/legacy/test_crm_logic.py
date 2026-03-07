"""
=============================================================================
CRM Service Layer Tests - Target: 95%+ Coverage
=============================================================================

Tests for services/crm_logic.py - Pure business logic functions
=============================================================================
"""

import pytest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from services.crm_logic import CRMService, CRMDataLogic


@pytest.fixture
def sample_customers():
    return [
        {'id': '1', 'name': 'أحمد محمد', 'phone': '+201234567890', 'city': 'القاهرة',
         'customer_type': 'lead', 'metadata': {'interests': ['تسويق', 'عقارات']}},
        {'id': '2', 'name': 'سارة أحمد', 'phone': '+201987654321', 'city': 'الإسكندرية',
         'customer_type': 'customer', 'metadata': {'interests': ['سيارات']}},
        {'id': '3', 'name': 'محمد علي', 'phone': '+201555555555', 'city': 'القاهرة',
         'customer_type': 'vip', 'metadata': {'interests': ['استثمار', 'عقارات']}},
    ]


# =============================================================================
# FILTER TESTS
# =============================================================================

class TestFilterCustomers:
    def test_filter_empty_list(self):
        assert CRMService.filter_customers([]) == []
        assert CRMService.filter_customers(None) == []
    
    def test_filter_by_type_lead(self, sample_customers):
        result = CRMService.filter_customers(sample_customers, filter_type='lead')
        assert len(result) == 1
        assert result[0]['name'] == 'أحمد محمد'
    
    def test_filter_by_type_customer(self, sample_customers):
        result = CRMService.filter_customers(sample_customers, filter_type='customer')
        assert len(result) == 1
        assert result[0]['name'] == 'سارة أحمد'
    
    def test_filter_by_type_vip(self, sample_customers):
        result = CRMService.filter_customers(sample_customers, filter_type='vip')
        assert len(result) == 1
        assert result[0]['name'] == 'محمد علي'
    
    def test_filter_by_city(self, sample_customers):
        result = CRMService.filter_customers(sample_customers, city='القاهرة')
        assert len(result) == 2
    
    def test_filter_by_city_case_insensitive(self, sample_customers):
        customers = [{'name': 'Test', 'city': 'Cairo', 'metadata': {}}]
        result = CRMService.filter_customers(customers, city='cairo')
        assert len(result) == 1
    
    def test_filter_by_city_from_metadata(self):
        customers = [{'name': 'Test', 'metadata': {'city': 'Giza'}}]
        result = CRMService.filter_customers(customers, city='Giza')
        assert len(result) == 1
    
    def test_filter_by_interests(self, sample_customers):
        result = CRMService.filter_customers(sample_customers, interests=['تسويق'])
        assert len(result) == 1
        assert result[0]['name'] == 'أحمد محمد'
    
    def test_filter_by_multiple_interests(self, sample_customers):
        result = CRMService.filter_customers(sample_customers, interests=['عقارات'])
        assert len(result) == 2
    
    def test_filter_combined(self, sample_customers):
        result = CRMService.filter_customers(sample_customers, filter_type='lead', city='القاهرة', interests=['تسويق'])
        assert len(result) == 1
    
    def test_filter_no_match(self, sample_customers):
        result = CRMService.filter_customers(sample_customers, filter_type='nonexistent')
        assert len(result) == 0
    
    def test_filter_skips_none_entries(self):
        customers = [None, {'name': 'Valid', 'customer_type': 'lead', 'metadata': {}}, None]
        result = CRMService.filter_customers(customers, filter_type='lead')
        assert len(result) == 1


# =============================================================================
# EXPORT CSV TESTS
# =============================================================================

class TestExportCSV:
    def test_export_empty_list(self):
        csv = CRMService.export_csv([])
        assert 'name,phone,city' in csv
    
    def test_export_single_customer(self, sample_customers):
        csv = CRMService.export_csv([sample_customers[0]])
        assert 'أحمد محمد' in csv
        assert '+201234567890' in csv
        assert 'تسويق;عقارات' in csv
    
    def test_export_all_customers(self, sample_customers):
        csv = CRMService.export_csv(sample_customers)
        lines = csv.strip().split('\n')
        assert len(lines) == 4  # Header + 3 customers
    
    def test_export_handles_none_customer(self):
        csv = CRMService.export_csv([None, {'name': 'Test', 'phone': '123'}])
        assert 'Test' in csv
    
    def test_export_handles_missing_fields(self):
        csv = CRMService.export_csv([{'name': 'Test'}])
        assert 'Test' in csv
    
    def test_export_handles_special_characters(self):
        customers = [{'name': 'Ahmed, Jr.', 'phone': '123', 'metadata': {}}]
        csv = CRMService.export_csv(customers)
        # Should properly escape CSV
        assert 'Ahmed' in csv


# =============================================================================
# TAG MANAGEMENT TESTS
# =============================================================================

class TestTagManagement:
    def test_add_tag_basic(self):
        customer = {'name': 'Test', 'metadata': {'interests': ['a']}}
        result = CRMService.add_tag(customer, 'b')
        assert 'b' in result['metadata']['interests']
    
    def test_add_tag_no_metadata(self):
        customer = {'name': 'Test'}
        result = CRMService.add_tag(customer, 'new')
        assert result['metadata']['interests'] == ['new']
    
    def test_add_tag_empty_interests(self):
        customer = {'name': 'Test', 'metadata': {}}
        result = CRMService.add_tag(customer, 'tag')
        assert 'tag' in result['metadata']['interests']
    
    def test_add_tag_duplicate_ignored(self):
        customer = {'name': 'Test', 'metadata': {'interests': ['existing']}}
        result = CRMService.add_tag(customer, 'existing')
        assert result['metadata']['interests'].count('existing') == 1
    
    def test_add_tag_strips_whitespace(self):
        customer = {'name': 'Test', 'metadata': {'interests': []}}
        result = CRMService.add_tag(customer, '  tag  ')
        assert 'tag' in result['metadata']['interests']
    
    def test_add_tag_none_customer_raises(self):
        with pytest.raises(ValueError):
            CRMService.add_tag(None, 'tag')
    
    def test_add_tag_empty_tag_raises(self):
        with pytest.raises(ValueError):
            CRMService.add_tag({'name': 'Test'}, '')
    
    def test_add_tag_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            CRMService.add_tag({'name': 'Test'}, '   ')
    
    def test_remove_tag(self):
        customer = {'name': 'Test', 'metadata': {'interests': ['a', 'b']}}
        result = CRMService.remove_tag(customer, 'a')
        assert 'a' not in result['metadata']['interests']
    
    def test_remove_tag_not_exists(self):
        customer = {'name': 'Test', 'metadata': {'interests': ['a']}}
        result = CRMService.remove_tag(customer, 'nonexistent')
        assert result['metadata']['interests'] == ['a']
    
    def test_remove_tag_none_customer(self):
        result = CRMService.remove_tag(None, 'tag')
        assert result is None


# =============================================================================
# STATISTICS TESTS
# =============================================================================

class TestCalculateStats:
    def test_stats_empty_list(self):
        stats = CRMService.calculate_stats([])
        assert stats['total'] == 0
        assert stats['leads'] == 0
    
    def test_stats_with_customers(self, sample_customers):
        stats = CRMService.calculate_stats(sample_customers)
        assert stats['total'] == 3
        assert stats['leads'] == 1
        assert stats['customers'] == 1
        assert stats['vips'] == 1
    
    def test_stats_cities_count(self, sample_customers):
        stats = CRMService.calculate_stats(sample_customers)
        assert 'القاهرة' in stats['cities']
        assert stats['cities']['القاهرة'] == 2
    
    def test_stats_top_interests(self, sample_customers):
        stats = CRMService.calculate_stats(sample_customers)
        assert 'عقارات' in stats['top_interests']
    
    def test_stats_skips_none(self):
        customers = [None, {'name': 'Test', 'customer_type': 'lead'}]
        stats = CRMService.calculate_stats(customers)
        assert stats['total'] == 2
        assert stats['leads'] == 1


# =============================================================================
# VALIDATION TESTS
# =============================================================================

class TestValidation:
    def test_validate_valid_customer(self):
        result = CRMService.validate_customer({'phone': '+201234567890'})
        assert result['is_valid'] is True
    
    def test_validate_none_customer(self):
        result = CRMService.validate_customer(None)
        assert result['is_valid'] is False
    
    def test_validate_missing_phone(self):
        result = CRMService.validate_customer({'name': 'Test'})
        assert result['is_valid'] is False
        assert 'Phone number is required' in result['errors']
    
    def test_validate_invalid_phone_format(self):
        result = CRMService.validate_customer({'phone': 'abc'})
        assert result['is_valid'] is False
    
    def test_validate_phone_too_short(self):
        result = CRMService.validate_customer({'phone': '123'})
        assert result['is_valid'] is False
    
    @pytest.mark.parametrize("phone", [
        '+201234567890',
        '01234567890',
        '+20 123 456 7890',
        '1234567890123'
    ])
    def test_validate_various_phone_formats(self, phone):
        assert CRMService.validate_phone_format(phone) is True
    
    def test_validate_phone_format_empty(self):
        assert CRMService.validate_phone_format('') is False
        assert CRMService.validate_phone_format(None) is False


# =============================================================================
# HELPER FUNCTIONS TESTS
# =============================================================================

class TestHelperFunctions:
    def test_get_customer_interests_valid(self):
        customer = {'metadata': {'interests': ['a', 'b']}}
        assert CRMService._get_customer_interests(customer) == ['a', 'b']
    
    def test_get_customer_interests_no_metadata(self):
        assert CRMService._get_customer_interests({'name': 'Test'}) == []
    
    def test_get_customer_interests_invalid_metadata(self):
        assert CRMService._get_customer_interests({'metadata': 'string'}) == []
    
    def test_get_customer_interests_none(self):
        assert CRMService._get_customer_interests(None) == []
    
    def test_get_city_from_customer(self):
        assert CRMService._get_city({'city': 'Cairo'}) == 'Cairo'
    
    def test_get_city_from_metadata(self):
        assert CRMService._get_city({'metadata': {'city': 'Cairo'}}) == 'Cairo'
    
    def test_get_city_default(self):
        assert CRMService._get_city({}) == 'غير معروف'
    
    def test_format_last_contact_valid(self):
        dt = datetime(2024, 1, 15, 10, 30)
        assert CRMService.format_last_contact(dt) == '2024-01-15 10:30'
    
    def test_format_last_contact_none(self):
        assert CRMService.format_last_contact(None) == 'لا يوجد'
    
    def test_format_last_contact_invalid(self):
        assert CRMService.format_last_contact('invalid') == 'لا يوجد'
    
    def test_get_customer_color_lead(self):
        assert CRMService.get_customer_color('lead') == '#a6e3a1'
    
    def test_get_customer_color_customer(self):
        assert CRMService.get_customer_color('customer') == '#89b4fa'
    
    def test_get_customer_color_vip(self):
        assert CRMService.get_customer_color('vip') == '#cba6f7'
    
    def test_get_customer_color_unknown(self):
        assert CRMService.get_customer_color('unknown') == '#a6e3a1'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=services.crm_logic", "--cov-report=term-missing"])
