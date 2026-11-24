import streamlit as st
import json
import os
import sys
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_loader import load_incidents
from agents.triage_agent import triage_incident
from agents.resource_agent import match_resources
from agents.gatekeeper_agent import gate_decision

LOGS_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "decisions.jsonl")


# ── Helper to log human decisions ─────────────────────────────────────────────
def _log_human(incident, triage, decision, human_action, note):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "incident_id": incident.get("id"),
        "incident_type": triage.get("incident_type"),
        "urgency_score": triage.get("urgency_score"),
        "action": decision.get("action"),
        "confidence": decision.get("confidence"),
        "justification": decision.get("justification"),
        "rule_based": decision.get("rule_based", False),
        "human_action": human_action,
        "dispatcher_note": note,
    }
    os.makedirs(os.path.dirname(LOGS_PATH), exist_ok=True)
    with open(LOGS_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Emergency AI Dispatch",
    page_icon="🚨",
    layout="wide",
)

# ── Helper: urgency colour ─────────────────────────────────────────────────────
def urgency_color(score: int) -> str:
    if score >= 4:
        return "#FF4B4B"   # red
    elif score == 3:
        return "#FFA500"   # amber
    else:
        return "#21C354"   # green


def urgency_label(score: int) -> str:
    labels = {1: "LOW", 2: "LOW-MEDIUM", 3: "MEDIUM", 4: "HIGH", 5: "CRITICAL"}
    return labels.get(score, "UNKNOWN")


# ── Load incidents ─────────────────────────────────────────────────────────────
incidents = load_incidents()
incident_options = {f"[{i['id']}] {i['type_hint'].replace('_',' ').title()} — {i['location']['description']}": i for i in incidents}

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
st.sidebar.title("🚨 Emergency AI Dispatch")
st.sidebar.markdown("**AI-Supported Emergency Response**")
st.sidebar.markdown("---")

selected_label = st.sidebar.selectbox("Select an Incident", list(incident_options.keys()))
incident = incident_options[selected_label]

st.sidebar.markdown("---")
st.sidebar.markdown("**How it works:**")
st.sidebar.markdown("1. Select a 911 incident\n2. Click Analyse\n3. Review AI recommendation\n4. Approve or Override")

# ── Main tabs ──────────────────────────────────────────────────────────────────
tab_dispatch, tab_log = st.tabs(["📋 Incident Dispatch", "📜 Decision Log"])

# ══ TAB 1: Dispatch ════════════════════════════════════════════════════════════
with tab_dispatch:
    st.title("📋 Incident Dispatcher Dashboard")
    st.markdown(f"**Incident ID:** `{incident['id']}` &nbsp;|&nbsp; **Received:** {incident['timestamp']}")

    # 911 Transcript
    with st.expander("📞 911 Call Transcript", expanded=True):
        st.info(incident["transcript"])

    st.markdown("---")

    # Analyse button
    if st.button("🔍 Analyse Incident with AI", type="primary", use_container_width=True):
        with st.spinner("Running AI triage..."):
            triage = triage_incident(incident)
        with st.spinner("Matching resources..."):
            resource = match_resources(triage, incident)
        with st.spinner("Evaluating dispatch decision..."):
            decision = gate_decision(triage, resource)

        # Store in session state
        st.session_state["triage"] = triage
        st.session_state["resource"] = resource
        st.session_state["decision"] = decision
        st.session_state["incident"] = incident
        st.session_state["human_action"] = None

    # ── Results (only shown after analysis) ───────────────────────────────────
    if "triage" in st.session_state and st.session_state.get("incident", {}).get("id") == incident["id"]:
        triage   = st.session_state["triage"]
        resource = st.session_state["resource"]
        decision = st.session_state["decision"]

        # Triage Result Card
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🧠 AI Triage Result")
            score = triage.get("urgency_score", 3)
            color = urgency_color(score)
            label = urgency_label(score)
            st.markdown(
                f"<div style='background:{color};padding:10px;border-radius:8px;color:white;font-size:1.2em;text-align:center'>"
                f"⚠️ Urgency: <strong>{score}/5 — {label}</strong></div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Type:** {triage.get('incident_type','').replace('_',' ').title()}")
            st.markdown(f"**Summary:** {triage.get('summary','')}")

            entities = triage.get("key_entities", {})
            if entities.get("vulnerability_flags"):
                st.warning(f"🚩 Vulnerability Flag: **{entities['vulnerability_flags']}**")
            if entities.get("subject_description"):
                st.markdown(f"**Subject:** {entities['subject_description']}")
            if entities.get("time_missing"):
                st.markdown(f"**Missing for:** {entities['time_missing']}")

        with col2:
            st.subheader("🚒 Recommended Resources")
            units = resource.get("recommended_units", [])
            if units:
                for unit in units:
                    st.success(f"✅ **{unit['unit_name']}** ({unit['unit_type'].replace('_',' ').title()})  \nETA: {unit['estimated_arrival_minutes']} min")
            else:
                st.error("❌ No available units found")

            missing = resource.get("missing_resource_types", [])
            if missing:
                st.warning(f"⚠️ No available units of type: {', '.join(missing)}")

        st.markdown("---")

        # Gatekeeper Decision
        st.subheader("⚖️ AI Decision")
        action = decision.get("action", "escalate_to_human")
        confidence = decision.get("confidence", 0.0)
        justification = decision.get("justification", "")

        if action == "auto_dispatch":
            st.success(f"🟢 **AUTO-DISPATCH RECOMMENDED** (Confidence: {confidence*100:.0f}%)")
        else:
            st.error(f"🔴 **ESCALATE TO HUMAN DISPATCHER** (Confidence: {confidence*100:.0f}%)")

        st.markdown(f"**AI Justification:** _{justification}_")

        st.markdown("---")
        st.subheader("👮 Dispatcher Action Required")

        if st.session_state.get("human_action") is None:
            col_approve, col_override = st.columns(2)
            with col_approve:
                if st.button("✅ Approve Dispatch", type="primary", use_container_width=True):
                    st.session_state["human_action"] = "approved"
                    _log_human(incident, triage, decision, "approved", "")
            with col_override:
                if st.button("🔄 Override / Escalate", type="secondary", use_container_width=True):
                    st.session_state["human_action"] = "override_pending"

        if st.session_state.get("human_action") == "override_pending":
            note = st.text_area("Enter your override reason:", placeholder="e.g. Requesting mutual aid from neighbouring district...")
            if st.button("Confirm Override", type="primary"):
                st.session_state["human_action"] = "overridden"
                _log_human(incident, triage, decision, "overridden", note)

        if st.session_state.get("human_action") == "approved":
            st.success("✅ **Dispatch approved by human dispatcher.** Decision logged.")
        elif st.session_state.get("human_action") == "overridden":
            st.warning("🔄 **Decision overridden by dispatcher.** Override logged.")

    elif "triage" in st.session_state:
        # Different incident selected — clear state
        st.session_state.pop("triage", None)
        st.session_state.pop("resource", None)
        st.session_state.pop("decision", None)
        st.session_state.pop("human_action", None)


# ══ TAB 2: Decision Log ════════════════════════════════════════════════════════
with tab_log:
    st.title("📜 Decision Log")
    st.markdown("All AI and human decisions are recorded here for transparency and audit.")

    if os.path.exists(LOGS_PATH):
        with open(LOGS_PATH, "r") as f:
            lines = [json.loads(line) for line in f if line.strip()]

        if lines:
            import pandas as pd
            df = pd.DataFrame(lines)
            # Reorder columns for display
            cols = ["timestamp", "incident_id", "incident_type", "urgency_score", "action", "confidence", "justification", "rule_based"]
            df = df[[c for c in cols if c in df.columns]]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No decisions logged yet. Analyse an incident first.")
    else:
        st.info("No decisions logged yet. Analyse an incident first.")


