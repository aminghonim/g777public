"""
CRM API Router - Customer Relationship Management Endpoints
===========================================================

This module provides CRM API endpoints for managing customers, tags, and statistics.
All endpoints are secured with user authentication and tenant isolation.

Endpoints:
- GET /api/crm/customers: List customers with filtering
- GET /api/crm/stats: CRM statistics
- POST /api/crm/customers/{id}/tags: Add tag to customer
- DELETE /api/crm/customers/{id}/tags/{tag}: Remove tag from customer
- GET /api/crm/export/csv: Export customers to CSV
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from backend.core.analytics import track_crm_export
from backend.database_manager import db_manager
from core.dependencies import get_current_user
from backend.services.crm_logic import CRMService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/customers", response_model=List[Dict[str, Any]], tags=["CRM"])
async def get_customers(
    current_user: Dict[str, Any] = Depends(get_current_user),
    customer_type: Optional[str] = Query(None, description="Filter by customer type (lead, customer, vip)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    interests: Optional[List[str]] = Query(None, description="Filter by interests (comma-separated)"),
):
    """
    Get customers with optional filtering.

    Args:
        current_user: Authenticated user information
        customer_type: Filter by customer type
        city: Filter by city
        interests: Filter by interests

    Returns:
        List of filtered customers
    """
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found")

        # Get customers for this user (tenant isolation)
        customers = db_manager.get_customers_by_user(user_id)

        # Apply business logic filtering
        filtered_customers = CRMService.filter_customers(
            customers=customers,
            filter_type=customer_type,
            city=city,
            interests=interests
        )

        logger.info(f"Retrieved {len(filtered_customers)} customers for user {user_id}")
        return filtered_customers

    except Exception as e:
        logger.error(f"Error retrieving customers: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve customers")


@router.get("/stats", response_model=Dict[str, Any], tags=["CRM"])
async def get_crm_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get CRM statistics for the current user.

    Args:
        current_user: Authenticated user information

    Returns:
        Dictionary containing CRM statistics
    """
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found")

        # Get customers for this user
        customers = db_manager.get_customers_by_user(user_id)

        # Calculate statistics using business logic
        stats = CRMService.calculate_stats(customers)

        logger.info(f"Calculated CRM stats for user {user_id}: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error calculating CRM stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate statistics")


@router.post("/customers/{customer_id}/tags", tags=["CRM"])
async def add_customer_tag(
    customer_id: str,
    tag: str = Query(..., description="Tag to add to customer"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Add a tag to a specific customer.

    Args:
        customer_id: Customer ID
        tag: Tag to add
        current_user: Authenticated user information

    Returns:
        Success message
    """
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found")

        # Get customer to verify ownership
        customers = db_manager.get_customers_by_user(user_id)
        customer = next((c for c in customers if str(c.get('id')) == customer_id), None)

        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        updated_customer = CRMService.add_tag(customer, tag, user_id)
        logger.info("Added tag '%s' to customer %s for user %s", tag, customer_id, user_id)
        return {"message": f"Tag '{tag}' added successfully to customer {customer_id}"}

    except ValueError as e:
        logger.warning(f"Validation error adding tag: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding tag to customer: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add tag")


@router.delete("/customers/{customer_id}/tags/{tag}", tags=["CRM"])
async def remove_customer_tag(
    customer_id: str,
    tag: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Remove a tag from a specific customer.

    Args:
        customer_id: Customer ID
        tag: Tag to remove
        current_user: Authenticated user information

    Returns:
        Success message
    """
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found")

        # Get customer to verify ownership
        customers = db_manager.get_customers_by_user(user_id)
        customer = next((c for c in customers if str(c.get('id')) == customer_id), None)

        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        CRMService.remove_tag(customer, tag, user_id)
        logger.info("Removed tag '%s' from customer %s for user %s", tag, customer_id, user_id)
        return {"message": f"Tag '{tag}' removed successfully from customer {customer_id}"}

    except Exception as e:
        logger.error(f"Error removing tag from customer: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove tag")


@router.get("/export/csv", tags=["CRM"])
async def export_customers_csv(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Export customers to CSV format.

    Args:
        current_user: Authenticated user information

    Returns:
        StreamingResponse with CSV data
    """
    try:
        user_id = current_user.get("user_id") or current_user.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found")

        # Get customers for this user
        customers = db_manager.get_customers_by_user(user_id)

        csv_content = CRMService.export_csv(customers)
        logger.info("Exported %d customers to CSV for user %s", len(customers), user_id)

        # Fire PostHog event without blocking the response
        asyncio.create_task(track_crm_export(user_id, len(customers)))

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=customers.csv"},
        )

    except Exception as e:
        logger.error(f"Error exporting customers to CSV: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export customers")