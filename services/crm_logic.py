"""
=============================================================================
CRM Service Layer - Pure Business Logic
=============================================================================

This module contains all CRM business logic separated from UI (NiceGUI).
All functions are Pure Functions: receive data, return data.

Target Coverage: 95%+
=============================================================================
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import csv
import io
import re


class CRMService:
    """
    CRM Business Logic Service.
    All methods are pure functions - no UI dependencies.
    """
    
    # ==========================================================================
    # FILTERING FUNCTIONS
    # ==========================================================================
    
    @staticmethod
    def filter_customers(
        customers: List[Dict], 
        filter_type: Optional[str] = None,
        city: Optional[str] = None,
        interests: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Filter customers based on multiple criteria.
        
        Args:
            customers: List of customer dictionaries
            filter_type: Customer type (lead, customer, vip)
            city: City name to filter by
            interests: List of interests to match (ANY match)
            
        Returns:
            Filtered list of customers
        """
        if not customers:
            return []
        
        result = []
        
        for cust in customers:
            if cust is None:
                continue
            
            # Filter by type
            if filter_type:
                cust_type = cust.get('customer_type', '')
                if cust_type != filter_type:
                    continue
            
            # Filter by city
            if city:
                cust_city = cust.get('city') or ''
                metadata = cust.get('metadata') or {}
                metadata_city = metadata.get('city', '') if isinstance(metadata, dict) else ''
                
                actual_city = cust_city or metadata_city
                if not actual_city or city.lower() not in actual_city.lower():
                    continue
            
            # Filter by interests
            if interests:
                cust_interests = CRMService._get_customer_interests(cust)
                if not any(i in cust_interests for i in interests):
                    continue
            
            result.append(cust)
        
        return result
    
    @staticmethod
    def _get_customer_interests(customer: Dict) -> List[str]:
        """Extract interests from customer metadata safely."""
        if not customer:
            return []
        
        metadata = customer.get('metadata')
        if not isinstance(metadata, dict):
            return []
        
        interests = metadata.get('interests')
        if not isinstance(interests, list):
            return []
        
        return interests
    
    # ==========================================================================
    # EXPORT FUNCTIONS
    # ==========================================================================
    
    @staticmethod
    def export_csv(customers: List[Dict]) -> str:
        """
        Export customers to CSV string.
        
        Args:
            customers: List of customer dictionaries
            
        Returns:
            CSV formatted string with UTF-8 BOM for Excel compatibility
        """
        if not customers:
            return "name,phone,city,customer_type,interests\n"
        
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Header
        writer.writerow(['name', 'phone', 'city', 'customer_type', 'interests'])
        
        for cust in customers:
            if not cust:
                continue
            
            name = cust.get('name', '')
            phone = cust.get('phone', '')
            city = CRMService._get_city(cust)
            cust_type = cust.get('customer_type', 'lead')
            interests = CRMService._get_customer_interests(cust)
            interests_str = ';'.join(str(i) for i in interests if i)
            
            writer.writerow([name, phone, city, cust_type, interests_str])
        
        return output.getvalue()
    
    @staticmethod
    def _get_city(customer: Dict) -> str:
        """Extract city from customer safely."""
        if not customer:
            return 'غير معروف'
        
        city = customer.get('city')
        if city:
            return city
        
        metadata = customer.get('metadata')
        if isinstance(metadata, dict):
            return metadata.get('city', 'غير معروف')
        
        return 'غير معروف'
    
    # ==========================================================================
    # TAG MANAGEMENT
    # ==========================================================================
    
    @staticmethod
    def add_tag(customer: Dict, tag: str) -> Dict:
        """
        Add a tag (interest) to customer.
        
        Args:
            customer: Customer dictionary (will be modified in place)
            tag: Tag string to add
            
        Returns:
            Modified customer dictionary
            
        Raises:
            ValueError: If customer is None or tag is empty
        """
        if not customer:
            raise ValueError("Customer cannot be None")
        
        if not tag or not tag.strip():
            raise ValueError("Tag cannot be empty")
        
        tag = tag.strip()
        
        # Ensure metadata exists
        if 'metadata' not in customer or not isinstance(customer['metadata'], dict):
            customer['metadata'] = {}
        
        # Ensure interests list exists
        if 'interests' not in customer['metadata'] or not isinstance(customer['metadata']['interests'], list):
            customer['metadata']['interests'] = []
        
        # Add tag if not duplicate
        if tag not in customer['metadata']['interests']:
            customer['metadata']['interests'].append(tag)
        
        return customer
    
    @staticmethod
    def remove_tag(customer: Dict, tag: str) -> Dict:
        """
        Remove a tag from customer.
        
        Args:
            customer: Customer dictionary
            tag: Tag to remove
            
        Returns:
            Modified customer dictionary
        """
        if not customer:
            return customer
        
        interests = CRMService._get_customer_interests(customer)
        if tag in interests:
            customer['metadata']['interests'].remove(tag)
        
        return customer
    
    # ==========================================================================
    # STATISTICS FUNCTIONS
    # ==========================================================================
    
    @staticmethod
    def calculate_stats(customers: List[Dict]) -> Dict[str, Any]:
        """
        Calculate CRM statistics.
        
        Args:
            customers: List of customer dictionaries
            
        Returns:
            Dictionary with stats: total, leads, customers, vips, cities, top_interests
        """
        if not customers:
            return {
                'total': 0,
                'leads': 0,
                'customers': 0,
                'vips': 0,
                'cities': {},
                'top_interests': []
            }
        
        stats = {
            'total': len(customers),
            'leads': 0,
            'customers': 0,
            'vips': 0,
            'cities': {},
            'top_interests': []
        }
        
        interest_counts = {}
        
        for cust in customers:
            if not cust:
                continue
            
            # Count by type
            cust_type = cust.get('customer_type', '')
            if cust_type == 'lead':
                stats['leads'] += 1
            elif cust_type == 'customer':
                stats['customers'] += 1
            elif cust_type == 'vip':
                stats['vips'] += 1
            
            # Count cities
            city = CRMService._get_city(cust)
            if city and city != 'غير معروف':
                stats['cities'][city] = stats['cities'].get(city, 0) + 1
            
            # Count interests
            interests = CRMService._get_customer_interests(cust)
            for interest in interests:
                if interest:
                    interest_counts[interest] = interest_counts.get(interest, 0) + 1
        
        # Get top 5 interests
        sorted_interests = sorted(interest_counts.items(), key=lambda x: x[1], reverse=True)
        stats['top_interests'] = [i[0] for i in sorted_interests[:5]]
        
        return stats
    
    # ==========================================================================
    # VALIDATION FUNCTIONS
    # ==========================================================================
    
    @staticmethod
    def validate_customer(customer: Dict) -> Dict[str, Any]:
        """
        Validate customer data.
        
        Args:
            customer: Customer dictionary to validate
            
        Returns:
            Dictionary with is_valid, errors list
        """
        result = {'is_valid': True, 'errors': []}
        
        if not customer:
            result['is_valid'] = False
            result['errors'].append('Customer data is required')
            return result
        
        # Validate phone
        phone = customer.get('phone', '')
        if not phone:
            result['is_valid'] = False
            result['errors'].append('Phone number is required')
        else:
            # Remove spaces and dashes for validation
            clean_phone = re.sub(r'[\s\-]', '', phone)
            if not re.match(r'^[\+]?[0-9]{10,15}$', clean_phone):
                result['is_valid'] = False
                result['errors'].append('Invalid phone format')
        
        return result
    
    @staticmethod
    def validate_phone_format(phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number string
            
        Returns:
            True if valid, False otherwise
        """
        if not phone:
            return False
        
        # Remove spaces and dashes
        clean_phone = re.sub(r'[\s\-]', '', phone)
        
        # Must be 10-15 digits, optionally starting with +
        return bool(re.match(r'^[\+]?[0-9]{10,15}$', clean_phone))
    
    # ==========================================================================
    # DATE/TIME HELPERS
    # ==========================================================================
    
    @staticmethod
    def format_last_contact(last_contact: Optional[datetime]) -> str:
        """
        Format last contact datetime for display.
        
        Args:
            last_contact: datetime object or None
            
        Returns:
            Formatted string
        """
        if not last_contact:
            return 'لا يوجد'
        
        try:
            return last_contact.strftime('%Y-%m-%d %H:%M')
        except (AttributeError, ValueError):
            return 'لا يوجد'
    
    @staticmethod
    def get_customer_color(customer_type: str) -> str:
        """
        Get neon color for customer type.
        
        Args:
            customer_type: lead, customer, or vip
            
        Returns:
            Hex color code
        """
        colors = {
            'lead': '#a6e3a1',      # Green neon
            'customer': '#89b4fa',  # Blue neon
            'vip': '#cba6f7'        # Purple neon
        }
        return colors.get(customer_type, '#a6e3a1')


# =============================================================================
# BACKWARDS COMPATIBILITY ALIAS
# =============================================================================

# For compatibility with existing code
CRMDataLogic = CRMService
