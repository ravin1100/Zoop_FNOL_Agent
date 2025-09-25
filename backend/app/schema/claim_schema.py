from datetime import datetime, date as dt
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# class AgentStatus(str, Enum):
#     IDLE = "idle"
#     PROCESSING = "processing"
#     COMPLETED = "completed"
#     ERROR = "error"


# class WorkflowStatus(str, Enum):
#     PENDING = "pending"
#     IN_PROGRESS = "in_progress"
#     COMPLETED = "completed"
#     FAILED = "failed"


class ClaimSchema(BaseModel):
    """Schema for insurance claim data with validation"""

    # --- Required Fields ---
    claim_id: str = Field(..., description="Unique ID of the claim")
    type: str = Field(..., description="Type of claim")  # changed to string
    date: dt = Field(..., description="Date of the incident")
    amount: float = Field(..., description="Claim amount")
    description: str = Field(..., description="Description of the incident")
    customer_id: str = Field(..., description="ID of the customer")
    policy_number: str = Field(
        ..., description="Policy number associated with the claim"
    )
    incident_location: str = Field(..., description="Location of the incident")
    timestamp_submitted: datetime = Field(
        ..., description="Timestamp when the claim was submitted"
    )

    # --- Optional Fields ---
    police_report: Optional[str] = Field(
        None, description="Link or ID of police report if available"
    )
    injuries_reported: Optional[bool] = Field(
        None, description="Whether injuries were reported"
    )
    other_party_involved: Optional[bool] = Field(
        None, description="Whether another party was involved"
    )
    customer_tenure_days: Optional[int] = Field(
        None, description="Customer tenure in days"
    )
    previous_claims_count: Optional[int] = Field(
        None, description="Number of previous claims"
    )

    # --- Validators ---
    # @field_validator(
    #     "claim_id",
    #     "type",
    #     "date",
    #     "amount",
    #     "description",
    #     "customer_id",
    #     "policy_number",
    #     "incident_location",
    #     "timestamp_submitted",
    # )
    # def required_fields_not_empty(cls, v, field):
    #     if v is None or (isinstance(v, str) and not v.strip()):
    #         raise ValueError(f"Field '{field.name}' is required and cannot be empty")
    #     return v

    # @field_validator("description")
    # def description_min_length(cls, v):
    #     if len(v.strip()) < 30:
    #         raise ValueError("Description must be at least 30 characters long")
    #     return v
