import json
import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.watsonx_client import get_model

LOGS_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "decisions.jsonl")

# Urgency threshold: at or above this score always escalates to human
ESCALATE_URGENCY_THRESHOLD = 4

GATEKEEPER_PROMPT_TEMPLATE = """You are an AI decision assistant for emergency dispatch.

Incident Type: {incident_type}
Urgency Score: {urgency_score}/5
Incident Summary: {summary}
Vulnerability Flags: {vulnerability_flags}
Recommended Units: {units}
Missing Resource Types: {missing_types}

Based on this information, should this be AUTO-DISPATCHED by AI recommendation, or ESCALATED to a human dispatcher for review?

Consider:
- Urgency score 4 or 5 always warrants human review
- Missing resources always warrant escalation
- Vulnerable subjects (children, elderly, disability) warrant extra caution

Respond ONLY with a valid JSON object in this exact format:
{{
  "action": "<auto_dispatch or escalate_to_human>",
  "confidence": <float between 0.0 and 1.0>,
  "justification": "<one or two sentences explaining the decision>"
}}
###"""


def _rule_based_decision(triage: dict, resource: dict) -> dict | None:
    """
    Fast rule-based decision for clear-cut cases.
    Returns a decision dict or None if the case needs LLM reasoning.
    """
    urgency = triage.get("urgency_score", 3)
    no_resource = resource.get("escalate_no_resource", False)
    missing_types = resource.get("missing_resource_types", [])
    vulnerability = triage.get("key_entities", {}).get("vulnerability_flags")

    # Always escalate: high urgency, no resources, or vulnerable subject
    if urgency >= ESCALATE_URGENCY_THRESHOLD:
        return {
            "action": "escalate_to_human",
            "confidence": 1.0,
            "justification": f"Urgency score is {urgency}/5 — requires human dispatcher review.",
            "rule_based": True,
        }
    if no_resource or missing_types:
        return {
            "action": "escalate_to_human",
            "confidence": 1.0,
            "justification": f"No available units for required type(s): {', '.join(missing_types)}. Human must arrange mutual aid.",
            "rule_based": True,
        }
    if vulnerability and any(flag in str(vulnerability).lower() for flag in ["child", "elderly", "disability", "dementia", "autism", "non-verbal"]):
        return {
            "action": "escalate_to_human",
            "confidence": 0.95,
            "justification": f"Vulnerable subject detected ({vulnerability}). Human review required for safeguarding.",
            "rule_based": True,
        }

    return None  # ambiguous — send to LLM


def gate_decision(triage: dict, resource: dict) -> dict:
    """
    Decide whether to auto-dispatch or escalate.
    Uses rules first; falls back to LLM for ambiguous cases.
    """
    # Try rule-based first
    decision = _rule_based_decision(triage, resource)

    if decision is None:
        # Use LLM for ambiguous cases
        units_str = ", ".join(
            f"{u['unit_name']} (ETA {u['estimated_arrival_minutes']} min)"
            for u in resource.get("recommended_units", [])
        ) or "None"

        prompt = GATEKEEPER_PROMPT_TEMPLATE.format(
            incident_type=triage.get("incident_type", "unknown"),
            urgency_score=triage.get("urgency_score", 3),
            summary=triage.get("summary", ""),
            vulnerability_flags=triage.get("key_entities", {}).get("vulnerability_flags") or "none",
            units=units_str,
            missing_types=", ".join(resource.get("missing_resource_types", [])) or "none",
        )

        try:
            model = get_model()
            response = model.generate_text(prompt=prompt)
            raw = response.strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            decision = json.loads(raw[start:end])
            decision["rule_based"] = False
        except Exception as e:
            # Safe fallback: escalate on any LLM error
            decision = {
                "action": "escalate_to_human",
                "confidence": 0.5,
                "justification": "AI reasoning unavailable — defaulting to human review for safety.",
                "rule_based": False,
                "error": str(e),
            }

    # Log every decision
    _log_decision(triage, resource, decision)
    return decision


def _log_decision(triage: dict, resource: dict, decision: dict):
    """Append decision to the JSONL log file."""
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "incident_id": triage.get("incident_id"),
        "incident_type": triage.get("incident_type"),
        "urgency_score": triage.get("urgency_score"),
        "action": decision.get("action"),
        "confidence": decision.get("confidence"),
        "justification": decision.get("justification"),
        "rule_based": decision.get("rule_based", False),
    }
    os.makedirs(os.path.dirname(LOGS_PATH), exist_ok=True)
    with open(LOGS_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    from utils.data_loader import load_incidents
    from agents.triage_agent import triage_incident
    from agents.resource_agent import match_resources

    incidents = load_incidents()
    inc = incidents[0]  # missing child — INC001
    triage = triage_incident(inc)
    resource = match_resources(triage, inc)
    decision = gate_decision(triage, resource)
    print(f"Decision: {decision['action']} (confidence: {decision['confidence']})")
    print(f"Justification: {decision['justification']}")
