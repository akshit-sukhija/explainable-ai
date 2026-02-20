import json
import os
from typing import List, Dict
from models import Rule
from functools import lru_cache

RULES_DIR = "rules"

@lru_cache(maxsize=10)
def load_rules(ruleset_id: str) -> List[Rule]:
    """
    Loads a ruleset from a JSON file, validates it against the Rule model,
    and returns a list of Rule objects.
    
    Raises:
        FileNotFoundError: If the rules definition file doesn't exist.
        ValueError: If the rules JSON is invalid.
    """
    # Sanitize ruleset_id to prevent directory traversal
    safe_id = os.path.basename(ruleset_id)
    file_path = os.path.join(RULES_DIR, f"{safe_id}.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Ruleset '{ruleset_id}' not found at {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validate list of rules
        rules = [Rule(**item) for item in data]
        return rules
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in ruleset '{ruleset_id}': {e}")
    except Exception as e:
        raise ValueError(f"Error validating ruleset '{ruleset_id}': {e}")
