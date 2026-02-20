from typing import List, Dict, Optional, Union
from pydantic import BaseModel
from enum import Enum


# -----------------------------------
# Enums
# -----------------------------------

class DecisionLabel(str, Enum):
    ELIGIBLE = "Eligible"
    REVIEW = "Review"
    NOT_ELIGIBLE = "Not Eligible"


class RulePriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# -----------------------------------
# Rule Definition Models
# -----------------------------------

class OutcomeEffect(BaseModel):
    eligible: bool
    score_delta: int


class DocumentReference(BaseModel):
    doc_id: str
    page: int
    section: str


class Rule(BaseModel):
    id: str
    name: str
    condition_expression: str
    variables_required: List[str]
    outcome_effect: OutcomeEffect
    priority: RulePriority
    mandatory: bool
    document_reference: DocumentReference
    human_description: str


# -----------------------------------
# API Request Models
# -----------------------------------

class DecisionRequest(BaseModel):
    ruleset_id: str
    user_input: Dict[str, Union[str, int, float, bool]]


# -----------------------------------
# Rule Evaluation Result
# -----------------------------------

class RuleResult(BaseModel):
    id: str
    name: str
    passed: bool
    reason: str
    priority: RulePriority
    mandatory: bool
    document_reference: DocumentReference
    score_delta: int = 0
    suggestion: Optional[str] = None


# -----------------------------------
# Structured Confidence Model
# -----------------------------------

class ConfidenceVector(BaseModel):
    rule_confidence: int
    retrieval_confidence: int
    data_completeness: int


# -----------------------------------
# API Response Model
# -----------------------------------

class DecisionResponse(BaseModel):
    decision_label: DecisionLabel
    eligibility_score: int
    confidence_score: int  # kept for UI compatibility
    confidence_vector: Optional[ConfidenceVector] = None
    passed_rules: List[RuleResult]
    failed_rules: List[RuleResult]
    explanation_text: str