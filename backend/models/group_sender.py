"""
G777 Group Sender Models Module

This module defines Pydantic models for WhatsApp group management and 
broadcasting operations, ensuring strict type safety and SAAF compliance.
"""

from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BroadcastStatusEnum(str, Enum):
    """Enumeration of possible broadcast statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WhatsAppGroup(BaseModel):
    """
    Represents a WhatsApp Group entity with tenant isolation.
    """
    id: str = Field(..., description="Remote JID of the group (e.g. 123@g.us)")
    name: str = Field(..., alias="subject", description="Display name of the group")
    member_count: Optional[int] = Field(0, description="Number of members in the group")
    instance_name: str = Field("default", description="Tenant identifier for isolation")

    class Config:
        populate_by_name = True


class GroupSyncResponse(BaseModel):
    """
    Standard response format for group synchronization tasks.
    """
    success: bool = Field(..., description="Boolean indicating sync success")
    groups: List[WhatsAppGroup] = Field(..., description="List of synchronized groups")


class GroupBroadcastRequest(BaseModel):
    """
    Request model for initiating a message broadcast to multiple groups.
    """
    group_ids: List[str] = Field(..., description="List of target group JIDs")
    message: str = Field(..., description="Content of the message to be sent")
    delay_min: int = Field(5, ge=0, description="Minimum delay between messages (seconds)")
    delay_max: int = Field(15, ge=0, description="Maximum delay between messages (seconds)")
    instance_name: str = Field("default", description="Tenant identifier for isolation")


class BroadcastStatus(BaseModel):
    """
    Model representing the current status and metrics of a broadcast task.
    """
    id: str = Field(..., description="Unique identifier for the broadcast session")
    status: BroadcastStatusEnum = Field(
        BroadcastStatusEnum.PENDING, 
        description="Current state of the broadcast"
    )
    total_targets: int = Field(..., ge=0, description="Total number of target groups")
    sent_count: int = Field(0, ge=0, description="Count of messages successfully sent")
    start_time: datetime = Field(default_factory=datetime.now, description="Timestamp of session start")
    instance_name: str = Field("default", description="Tenant identifier for isolation")
