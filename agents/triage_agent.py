import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.watsonx_client import get_model


TRIAGE_PROMPT_TEMPLATE = """You are an emergency dispatch triage assistant. Analyze the 911 call transcript below and extract structured information.

Transcript:
"{transcript}"

Respond ONLY with a valid JSON object in this exact format (no extra text before or after):
{{
  "incident_type": "<one of: missing_person, fire, medical, crime, accident, flood, other>",
  "urgency_score": <integer 1-5 where 5 is most urgent>,
  "location_extracted": "<location mentioned in the call>",
  "summary": "<one sentence summary of the incident>",
  "key_entities": {{
    "num_people_involved": <integer or null>,
    "subject_description": "<physical description if mentioned, else null>",
    "last_seen_location": "<last known location if missing person, else null>",
    "time_missing": "<how long missing if stated, else null>",
    "vulnerability_flags": "<child/elderly/disability/medical_condition or null>"
  }}
}}
###"""


def triage_incident(incident: dict) -> dict:
    """
    Run the triage agent on a single incident.
    Returns a structured triage dict, or a fallback escalation dict on failure.
    """
    transcript = incident.get("transcript", "")
    prompt = TRIAGE_PROMPT_TEMPLATE.format(transcript=transcript)

    try:
        model = get_model()
        response = model.generate_text(prompt=prompt)
        raw = response.strip()

        # Extract JSON from response (handle any extra text)
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found in response")

        result = json.loads(raw[start:end])
        result["incident_id"] = incident.get("id")
        result["raw_transcript"] = transcript
        return result

    except Exception as e:
        # Fallback: flag for human review if LLM fails
        return {
            "incident_id": incident.get("id"),
            "incident_type": incident.get("type_hint", "other"),
            "urgency_score": 3,
            "location_extracted": incident.get("location", {}).get("description", "unknown"),
            "summary": "Triage failed — flagged for human review.",
            "key_entities": {
                "num_people_involved": None,
                "subject_description": None,
                "last_seen_location": None,
                "time_missing": None,
                "vulnerability_flags": None,
            },
            "raw_transcript": transcript,
            "error": str(e),
            "fallback": True,
        }


if __name__ == "__main__":
    from utils.data_loader import load_incidents
    incidents = load_incidents()
    print(f"Testing triage agent on {len(incidents)} incidents...\n")
    for inc in incidents[:3]:  # test first 3
        result = triage_incident(inc)
        print(f"[{result['incident_id']}] {result['incident_type']} | urgency: {result['urgency_score']}/5")
        print(f"  Summary: {result['summary']}")
        print(f"  Vulnerability flags: {result['key_entities'].get('vulnerability_flags')}")
        print()
