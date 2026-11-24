import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_loader import load_resources
from utils.geo_utils import euclidean_distance, estimated_arrival_minutes


# Maps incident type to required resource types
RESOURCE_MAP = {
    "missing_person": ["police", "search_rescue"],  # always sends 2 unit types
    "fire":           ["fire_truck"],
    "medical":        ["ambulance"],
    "crime":          ["police"],
    "accident":       ["ambulance", "fire_truck"],
    "flood":          ["fire_truck", "ambulance"],
    "other":          ["police"],
}


def match_resources(triage_result: dict, incident: dict) -> dict:
    """
    Match the best available emergency resources to a triaged incident.
    Returns recommended units, estimated arrival, and plain-language reasoning.
    """
    incident_type = triage_result.get("incident_type", "other")
    incident_location = incident.get("location", {"lat": 0.0, "lng": 0.0})
    required_types = RESOURCE_MAP.get(incident_type, ["police"])

    all_resources = load_resources()
    recommendations = []
    missing_types = []

    for resource_type in required_types:
        # Filter to available units of this type
        candidates = [
            r for r in all_resources
            if r["type"] == resource_type and r["status"] == "available"
        ]

        if not candidates:
            missing_types.append(resource_type)
            continue

        # Sort by distance to incident
        candidates.sort(key=lambda r: euclidean_distance(r["location"], incident_location))
        best = candidates[0]
        dist = euclidean_distance(best["location"], incident_location)
        eta = estimated_arrival_minutes(dist)

        recommendations.append({
            "unit_id": best["id"],
            "unit_name": best["unit_name"],
            "unit_type": resource_type,
            "estimated_arrival_minutes": eta,
        })

    # Build plain-language reasoning string
    if recommendations:
        unit_lines = ", ".join(
            f"{r['unit_name']} (ETA {r['estimated_arrival_minutes']} min)"
            for r in recommendations
        )
        reasoning = f"Matched {len(recommendations)} unit(s) for {incident_type} incident: {unit_lines}."
        if missing_types:
            reasoning += f" WARNING: No available units found for: {', '.join(missing_types)}."
    else:
        reasoning = f"No available units found for any required type ({', '.join(required_types)}). Escalation required."

    return {
        "incident_id": triage_result.get("incident_id"),
        "incident_type": incident_type,
        "recommended_units": recommendations,
        "missing_resource_types": missing_types,
        "reasoning": reasoning,
        "escalate_no_resource": len(missing_types) > 0 and len(recommendations) == 0,
    }


if __name__ == "__main__":
    from utils.data_loader import load_incidents
    from agents.triage_agent import triage_incident

    incidents = load_incidents()
    # Test on first missing person incident
    inc = incidents[0]
    triage = triage_incident(inc)
    result = match_resources(triage, inc)
    print(f"Incident: {result['incident_id']} ({result['incident_type']})")
    print(f"Reasoning: {result['reasoning']}")
    for unit in result["recommended_units"]:
        print(f"  → {unit['unit_name']} | ETA: {unit['estimated_arrival_minutes']} min")
