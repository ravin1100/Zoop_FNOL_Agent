from langchain_core.prompts import ChatPromptTemplate
from app.schema.claim_schema import ClaimSchema
from app.schema.risk_schema import RiskAssessmentLLMSchema
from app.service.llm_service import llm


from app.schema.routing_decision_schema import RoutingDecisionLLMSchema


llm_with_structured_output = llm.with_structured_output(RoutingDecisionLLMSchema)


# --- Call Method ---
def decide_routing(
    claim_data: ClaimSchema, risk_assessment: RiskAssessmentLLMSchema
) -> RoutingDecisionLLMSchema:
    """
    Decide the routing for a claim based on claim data and risk assessment.
    """

    # --- Prompt Template ---
    ROUTING_PROMPT_TEMPLATE = f"""
    You are an experienced operations manager at an insurance company.

    Your task is to determine the optimal processing path for a claim based on:
    1. Structured Claim Data
    2. Risk Assessment Report

    Instructions:
    - Assign a risk_level based on the risk report.
    - Decide a priority level: "urgent", "normal", "low".
    - Select an adjuster tier: "senior", "junior", or "specialist".
    - If data is incomplete, include validation_errors.

    Structured Claim Data:
    {claim_data}

    Risk Assessment Report:
    {risk_assessment}

    Output your decision in JSON following the schema.
    """

    prompt = ChatPromptTemplate.from_template(ROUTING_PROMPT_TEMPLATE)
    formatted_prompt = prompt.format_messages(
        claim_data=claim_data.model_dump_json(),
        risk_assessment=risk_assessment.model_dump_json(),
    )

    response = llm_with_structured_output.invoke(formatted_prompt)
    return response


# sample input

# claim_data = {
#     "claim_id": "CLM-2024-001",
#     "type": "auto_collision",
#     "date": "2024-01-15",
#     "amount": 2500,
#     "description": "Minor fender bender in parking lot at low speed.",
#     "customer_id": "CUST-123",
#     "policy_number": "POL-789-ACTIVE",
#     "incident_location": "123 Main St, Springfield",
#     "timestamp_submitted": "2024-01-15T10:45:00"
# }

# risk_report = {
#     "fraud_indicators": ["late policy activation", "suspicious location"],
#     "risk_score": 8,
#     "risk_category": "high",
#     "processing_score": 6
# }
