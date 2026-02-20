from typing import Any, Dict
from models import Rule, RuleResult
import re


# -----------------------------------
# Expression Safety Validation
# -----------------------------------

ALLOWED_PATTERN = re.compile(r"^[a-zA-Z0-9_\s<>=!&|().,'\"+-/*]+$")


def is_expression_safe(expression: str) -> bool:
    """
    Basic whitelist validation to prevent unsafe eval usage.
    """
    return bool(ALLOWED_PATTERN.match(expression))


# -----------------------------------
# Rule Evaluation
# -----------------------------------

def evaluate_rule(rule: Rule, user_input: Dict[str, Any]) -> RuleResult:
    """
    Deterministic rule evaluation engine.
    This is the system authority layer.
    """

    # 1️⃣ Check required inputs
    missing_vars = [
        var for var in rule.variables_required
        if var not in user_input
    ]

    if missing_vars:
        return RuleResult(
            id=rule.id,
            name=rule.name,
            passed=False,
            reason=f"Missing required input(s): {', '.join(missing_vars)}",
            priority=rule.priority,
            mandatory=rule.mandatory,
            document_reference=rule.document_reference,
            score_delta=0,
            suggestion=None
        )

    # 2️⃣ Validate expression safety
    if not is_expression_safe(rule.condition_expression):
        return RuleResult(
            id=rule.id,
            name=rule.name,
            passed=False,
            reason="Unsafe rule expression detected.",
            priority=rule.priority,
            mandatory=rule.mandatory,
            document_reference=rule.document_reference,
            score_delta=0,
            suggestion=None
        )

    context = user_input.copy()

    try:
        eval_globals = {
            "__builtins__": {},
            "true": True,
            "false": False,
            "null": None
        }

        condition_result = eval(
            rule.condition_expression,
            eval_globals,
            context
        )

        passed = bool(condition_result)

        # -----------------------------------
        # PASSED CASE
        # -----------------------------------

        if passed:
            reason_parts = []
            for var in rule.variables_required:
                val = user_input.get(var)
                formatted_val = f"'{val}'" if isinstance(val, str) else val
                reason_parts.append(f"{var} = {formatted_val}")

            return RuleResult(
                id=rule.id,
                name=rule.name,
                passed=True,
                reason=f"Condition met: {rule.condition_expression} "
                       f"where {', '.join(reason_parts)}",
                priority=rule.priority,
                mandatory=rule.mandatory,
                document_reference=rule.document_reference,
                score_delta=rule.outcome_effect.score_delta,
                suggestion=None
            )

        # -----------------------------------
        # FAILED CASE
        # -----------------------------------

        suggestion = None
        reason_parts = []

        for var in rule.variables_required:
            val = user_input.get(var)

            if isinstance(val, (int, float)):
                # <= or <
                match_max = re.search(
                    rf"{var}\s*(<=|<)\s*([\d\.]+)",
                    rule.condition_expression
                )
                if match_max:
                    limit = float(match_max.group(2))
                    if val > limit:
                        suggestion = f"Decrease {var} by {val - limit:.2f}"

                # >= or >
                match_min = re.search(
                    rf"{var}\s*(>=|>)\s*([\d\.]+)",
                    rule.condition_expression
                )
                if match_min:
                    limit = float(match_min.group(2))
                    if val < limit:
                        suggestion = f"Increase {var} by {limit - val:.2f}"

            formatted_val = f"'{val}'" if isinstance(val, str) else val
            reason_parts.append(f"{var} = {formatted_val}")

        return RuleResult(
            id=rule.id,
            name=rule.name,
            passed=False,
            reason=f"Condition failed: {rule.condition_expression} "
                   f"where {', '.join(reason_parts)}",
            priority=rule.priority,
            mandatory=rule.mandatory,
            document_reference=rule.document_reference,
            score_delta=0,
            suggestion=suggestion
        )

    except Exception as e:
        return RuleResult(
            id=rule.id,
            name=rule.name,
            passed=False,
            reason=f"Error evaluating rule: {str(e)}",
            priority=rule.priority,
            mandatory=rule.mandatory,
            document_reference=rule.document_reference,
            score_delta=0,
            suggestion=None
        )