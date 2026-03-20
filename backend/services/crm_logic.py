from typing import List, Dict, Any, Optional
import csv
import io
import logging
from backend.database_manager import db_manager

logger = logging.getLogger(__name__)

class CRMService:
    """
    Business logic layer for CRM features.
    Handles data transformations, aggregations, and business rules isolated from route/transport layer.
    """

    @staticmethod
    def filter_customers(
        customers: List[Dict[str, Any]],
        filter_type: Optional[str] = None,
        city: Optional[str] = None,
        interests: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Filter a list of customers based on criteria stored in their metadata."""
        filtered = []
        for customer in customers:
            meta = customer.get("metadata", {}) or {}
            
            # Type filter
            if filter_type:
                c_type = meta.get("customer_type", "customer")
                if c_type != filter_type:
                    continue
                    
            # City filter
            if city:
                c_city = meta.get("city", "")
                if city.lower() not in str(c_city).lower():
                    continue
                    
            # Interests filter
            if interests:
                c_interests = meta.get("interests", [])
                if not any(i in c_interests for i in interests):
                    continue
                    
            filtered.append(customer)
            
        return filtered

    @staticmethod
    def calculate_stats(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate high-level statistics like total customers and breakdown by type."""
        stats = {
            "total_customers": len(customers),
            "by_type": {
                "vip": 0,
                "lead": 0,
                "customer": 0
            }
        }
        
        for customer in customers:
            meta = customer.get("metadata", {}) or {}
            c_type = meta.get("customer_type", "customer")
            if c_type in stats["by_type"]:
                stats["by_type"][c_type] += 1
            else:
                stats["by_type"][c_type] = 1
                
        return stats

    @staticmethod
    def add_tag(customer: Dict[str, Any], tag: str, user_id: str) -> Dict[str, Any]:
        """Add a tag to a customer's metadata and save it to the DB."""
        if not tag or not tag.strip():
            raise ValueError("Tag cannot be empty")
            
        tag = tag.strip().lower()
        meta = customer.get("metadata", {}) or {}
        tags = meta.get("tags", [])
        
        if tag not in tags:
            tags.append(tag)
            meta["tags"] = tags
            
            # Persist to database
            phone = customer.get("phone")
            if phone and user_id:
                db_manager.upsert_customer(
                    phone=phone,
                    user_id=user_id,
                    metadata=meta
                )
            
        customer["metadata"] = meta
        return customer

    @staticmethod
    def remove_tag(customer: Dict[str, Any], tag: str, user_id: str) -> Dict[str, Any]:
        """Remove a tag from a customer's metadata."""
        tag = tag.strip().lower()
        meta = customer.get("metadata", {}) or {}
        tags = meta.get("tags", [])
        
        if tag in tags:
            tags.remove(tag)
            meta["tags"] = tags
            
            phone = customer.get("phone")
            if phone and user_id:
                db_manager.upsert_customer(
                    phone=phone,
                    user_id=user_id,
                    metadata=meta
                )
                
        customer["metadata"] = meta
        return customer

    @staticmethod
    def export_csv(customers: List[Dict[str, Any]]) -> str:
        """Convert a list of customers to a CSV string."""
        if not customers:
            return "phone,name,last_interaction,customer_type,city,tags\n"
            
        output = io.StringIO()
        fieldnames = ["phone", "name", "last_interaction", "customer_type", "city", "tags"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for c in customers:
            meta = c.get("metadata", {}) or {}
            tags = meta.get("tags", [])
            writer.writerow({
                "phone": c.get("phone", ""),
                "name": c.get("name", ""),
                "last_interaction": c.get("last_interaction", ""),
                "customer_type": meta.get("customer_type", "customer"),
                "city": meta.get("city", ""),
                "tags": ",".join(tags),
            })
            
        return output.getvalue()
