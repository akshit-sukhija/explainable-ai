from typing import List, Optional, Dict
from models import RuleResult


def generate_explanation(
    decision_label: str,
    passed_rules: List[RuleResult],
    failed_rules: List[RuleResult],
    eligibility_score: int,
    confidence_score: int,
    relevant_clauses: Optional[List[str]] = None,
    confidence_vector: Optional[Dict[str, int]] = None
) -> str:
    """
    Constructs a transparent, governance-aware explanation.
    Deterministic layer decides. This layer explains.
    """

    lines = []

    # ---------------------------------------
    # 1️⃣ Decision Summary
    # ---------------------------------------

    lines.append(f"## 🏷 Final Decision: **{decision_label}**")
    lines.append(f"- **Eligibility Score:** {eligibility_score}/100")
    lines.append(f"- **Rule Confidence:** {confidence_score}%")

    if confidence_vector:
        lines.append("")
        lines.append("### 🔍 Confidence Breakdown:")
        lines.append(f"- Rule Coverage: {confidence_vector.get('rule_confidence', 0)}%")
        lines.append(f"- Retrieval Confidence: {confidence_vector.get('retrieval_confidence', 0)}%")
        lines.append(f"- Data Completeness: {confidence_vector.get('data_completeness', 0)}%")

    lines.append("")

    # ---------------------------------------
    # 2️⃣ Governance Context
    # ---------------------------------------

    if decision_label == "Review":
        lines.append("⚠ **This application requires manual review due to trust thresholds or policy validation checks.**")
        lines.append("")

    if decision_label == "Not Eligible":
        lines.append("❌ The application does not meet one or more mandatory eligibility criteria.")
        lines.append("")

    # ---------------------------------------
    # 3️⃣ Failed Rules
    # ---------------------------------------

    if failed_rules:
        lines.append("### ❌ Rules Not Satisfied:")
        for rule in failed_rules:
            lines.append(f"- **{rule.name}**: {rule.reason}")
            if rule.suggestion:
                lines.append(f"  - 💡 Suggestion: {rule.suggestion}")
        lines.append("")

    # ---------------------------------------
    # 4️⃣ Passed Rules
    # ---------------------------------------

    if passed_rules:
        lines.append("### ✅ Criteria Successfully Met:")
        for rule in passed_rules:
            lines.append(f"- **{rule.name}**: {rule.reason}")
        lines.append("")

    # ---------------------------------------
    # 5️⃣ Supporting Policy References
    # ---------------------------------------

    if relevant_clauses:
        lines.append("### 📚 Supporting Policy References:")
        for clause in relevant_clauses:
            lines.append(f"> {clause}")
        lines.append("")

    # ---------------------------------------
    # 6️⃣ Transparency Footer
    # ---------------------------------------

    lines.append("---")
    lines.append("_This decision was computed using deterministic policy rules with governance safeguards._")

    return "\n".join(lines)