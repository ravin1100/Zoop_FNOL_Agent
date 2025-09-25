# --- Function to assess claim risk ---
from app.schema.claim_schema import ClaimSchema
from app.schema.risk_schema import RiskAssessmentLLMSchema
from langchain_core.prompts import ChatPromptTemplate


from app.service.llm_service import llm


llm_with_structured_output = llm.with_structured_output(RiskAssessmentLLMSchema)


def assess_claim_risk(claim_data: ClaimSchema) -> RiskAssessmentLLMSchema:
    """
    Analyze a claim for fraud indicators using LLM and return a structured RiskAssessmentSchema.
    """

    prompt = f"""
        You are a fraud detection assistant for insurance claims.

        Analyze a claim for fraud indicators using LLM and return a structured RiskAssessmentSchema.
        Also evaluate how complete the claim is and whether it is ready to process.

        Analyze the following claim data and determine:
        1. Fraud indicators present (list 3-5 simple rules you see triggered)
        2. Risk score on a scale from 1 (lowest) to 10 (highest)
        3. Risk category: Low, Medium, or High
        4. Processing readiness score: on a scale from 1 (not ready) to 10 (fully ready), based on whether the claim description and details are sufficient to process.

        Return the output in this JSON structure ONLY

        Claim Data:
        {claim_data}

        """

    format_prompt = ChatPromptTemplate.from_template(prompt)
    formatted_prompt = format_prompt.format_messages(
        claim_data=claim_data.model_dump_json()
    )

    response = llm_with_structured_output.invoke(formatted_prompt)
    return response
