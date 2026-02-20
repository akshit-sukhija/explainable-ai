import json
import hashlib
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)

def log_decision(request, response):
    payload_str = json.dumps(request, sort_keys=True)
    checksum = hashlib.sha256(payload_str.encode()).hexdigest()

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "input_checksum": checksum,
        "decision_label": response["decision_label"],
        "eligibility_score": response["eligibility_score"],
        "confidence": response.get("confidence_vector", {}),
        "passed_rules": [r["id"] for r in response["passed_rules"]],
        "failed_rules": [r["id"] for r in response["failed_rules"]],
    }

    with open(LOG_PATH / "decision_logs.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")