from datetime import datetime

from fastapi import HTTPException
from app.schema.claim_schema import ClaimSchema


KEY_FIELDS = [
    "claim_id",
    "type",
    "date",
    "amount",
    "description",
    "customer_id",
    "policy_number",
    "incident_location",
    "timestamp_submitted",
]


def parse_claim_key_fields(raw_data: ClaimSchema) -> ClaimSchema:
    """
    Extract key claim information and validate:
    - completeness for key fields
    - description length > 30 characters
    Returns a dict with extracted fields if valid.
    """
    raw_data_values = raw_data.model_dump()
    # Check for missing key fields
    missing_fields = [
        field
        for field in KEY_FIELDS
        if field not in raw_data_values or raw_data_values[field] in (None, "")
    ]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing mandatory fields: {', '.join(missing_fields)}",
        )

    # Extract key information
    key_info = {field: raw_data_values[field] for field in KEY_FIELDS}

    # Convert 'date' to datetime.date if it is a string
    if isinstance(key_info["date"], str):
        try:
            key_info["date"] = datetime.strptime(key_info["date"], "%Y-%m-%d").date()
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid date format for field 'date': {e}"
            )

    # Check description length
    if len(key_info["description"]) < 30:
        raise HTTPException(
            status_code=400, detail="Description must be at least 30 characters long"
        )

    return raw_data
