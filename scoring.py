from typing import List, Dict
from models import RuleResult

# -----------------------------------
# Threshold Configuration
# -----------------------------------

ELIGIBLE_THRESHOLD = 70
REVIEW_THRESHOLD = 50
RETRIEVAL_MIN_THRESHOLD = 0.60
DATA_COMPLETENESS_MIN = 0.80


# -----------------------------------
# Eligibility Score
# -----------------------------------

def calculate_eligibility_score(passed_rules: List[RuleResult]) -> int:
    total_score = sum(r.score_delta for r in passed_rules)
    return max(0, min(100, total_score))


# -----------------------------------
# Deterministic Label
# -----------------------------------

def determine_deterministic_label(
    passed_rules: List[RuleResult],
    failed_rules: List[RuleResult],
    eligibility_score: int
) -> str:

    for r in failed_rules:
        if r.mandatory:
            return "Not Eligible"

    if eligibility_score >= ELIGIBLE_THRESHOLD:
        return "Eligible"
    elif eligibility_score >= REVIEW_THRESHOLD:
        return "Review"
    else:
        return "Not Eligible"


# -----------------------------------
# Confidence Vector
# -----------------------------------

def calculate_confidence_vector(
    passed_rules: List[RuleResult],
    failed_rules: List[RuleResult],
    total_rules_count: int,
    retrieval_similarity: float,
    data_completeness: float
) -> Dict[str, int]:

    rule_coverage = (
        (len(passed_rules) + len(failed_rules))
        / max(total_rules_count, 1)
    )

    return {
        "rule_confidence": round(rule_coverage * 100),
        "retrieval_confidence": round(retrieval_similarity * 100),
        "data_completeness": round(data_completeness * 100)
    }


# -----------------------------------
# Governance Layer
# -----------------------------------

def apply_governance_layer(
    deterministic_label: str,
    confidence_vector: Dict[str, int]
) -> str:

    if confidence_vector["retrieval_confidence"] < int(RETRIEVAL_MIN_THRESHOLD * 100):
        return "Review"

    if confidence_vector["data_completeness"] < int(DATA_COMPLETENESS_MIN * 100):
        return "Review"

    return deterministic_label