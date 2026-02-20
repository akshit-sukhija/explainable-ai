from fastapi import FastAPI, HTTPException
from models import (
    DecisionRequest,
    DecisionResponse,
    RuleResult,
    ConfidenceVector
)
from rules_loader import load_rules
from rule_engine import evaluate_rule
from scoring import (
    calculate_eligibility_score,
    determine_deterministic_label,
    calculate_confidence_vector,
    apply_governance_layer
)
from explanations import generate_explanation
from vector_store import vector_store

import logging
import hashlib
import json
from datetime import datetime
from pathlib import Path

# -------------------------------------
# Logging Configuration
# -------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Explainable Decision Intelligence System")

# -------------------------------------
# Audit Logging Setup
# -------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def log_decision(request_dict: dict, response_dict: dict):
    checksum = hashlib.sha256(
        json.dumps(request_dict, sort_keys=True).encode()
    ).hexdigest()

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "input_checksum": checksum,
        "decision_label": response_dict["decision_label"],
        "eligibility_score": response_dict["eligibility_score"],
        "confidence_score": response_dict["confidence_score"],
        "confidence_vector": response_dict.get("confidence_vector"),
        "passed_rule_ids": [r["id"] for r in response_dict["passed_rules"]],
        "failed_rule_ids": [r["id"] for r in response_dict["failed_rules"]],
    }

    with open(LOG_DIR / "decision_logs.json", "a") as f:
        f.write(json.dumps(entry) + "\n")

# -------------------------------------
# Health Endpoint
# -------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}

# -------------------------------------
# Get Rules Endpoint
# -------------------------------------

@app.get("/rules/{ruleset_id}")
def get_rules(ruleset_id: str):
    try:
        return load_rules(ruleset_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Ruleset '{ruleset_id}' not found"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# -------------------------------------
# Evaluate Endpoint
# -------------------------------------

@app.post("/evaluate", response_model=DecisionResponse)
def evaluate(request: DecisionRequest):
    try:
        # 1️⃣ Load Rules
        rules = load_rules(request.ruleset_id)

        # 2️⃣ Initialize Vector Store
        vector_store.init_index(rules)

        # 3️⃣ Deterministic Rule Evaluation
        results: list[RuleResult] = []

        for rule in rules:
            result = evaluate_rule(rule, request.user_input)
            results.append(result)

        passed_rules = [r for r in results if r.passed]
        failed_rules = [r for r in results if not r.passed]

        # 4️⃣ Eligibility Score
        eligibility_score = calculate_eligibility_score(passed_rules)

        # 5️⃣ Deterministic Label
        deterministic_label = determine_deterministic_label(
            passed_rules,
            failed_rules,
            eligibility_score
        )

        # 6️⃣ CRAG Retrieval
        if failed_rules:
            query = " ".join([r.name for r in failed_rules])
        else:
            query = "General eligibility criteria"

        relevant_clauses, similarity_score = vector_store.search(
            query,
            k=3
        )

        # 7️⃣ Data Completeness (coverage proxy)
        evaluated_count = len(results)
        total_rules = len(rules)
        data_completeness = evaluated_count / max(total_rules, 1)

        # 8️⃣ Confidence Vector
        confidence_vector_dict = calculate_confidence_vector(
            passed_rules,
            failed_rules,
            total_rules,
            similarity_score,
            data_completeness
        )

        # Convert to Pydantic model
        confidence_vector = ConfidenceVector(**confidence_vector_dict)

        # 9️⃣ Governance Layer
        final_label = apply_governance_layer(
            deterministic_label,
            confidence_vector_dict
        )

        # 🔟 Confidence Score (UI compatibility)
        confidence_score = confidence_vector.rule_confidence

        # 1️⃣1️⃣ Explanation
        explanation_text = generate_explanation(
            final_label,
            passed_rules,
            failed_rules,
            eligibility_score,
            confidence_score,
            relevant_clauses,
            confidence_vector_dict
        )

        response_obj = DecisionResponse(
            decision_label=final_label,
            eligibility_score=eligibility_score,
            confidence_score=confidence_score,
            confidence_vector=confidence_vector,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            explanation_text=explanation_text
        )

        # 1️⃣2️⃣ Audit Logging
        log_decision(request.dict(), response_obj.dict())

        return response_obj

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Ruleset '{request.ruleset_id}' not found"
        )

    except Exception as e:
        logger.error(f"Error processing evaluation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# -------------------------------------
# Local Run
# -------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)