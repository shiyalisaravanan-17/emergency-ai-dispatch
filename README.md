# 🚨 Emergency AI Dispatch — AI-Supported Emergency Response

**Hackathon Track:** Track #4 — Government & Public Services
**Challenge:** How might we use Agentic AI to help governments deliver more efficient, transparent, and citizen-centric public services?

---

## What It Does

An **Agentic AI Emergency Response Coordinator** that:
1. Reads a 911 call transcript
2. Uses IBM watsonx.ai to triage the incident (type, urgency, vulnerability flags)
3. Matches the nearest available emergency units
4. Decides whether to auto-recommend dispatch or escalate to a human
5. Presents everything to a dispatcher in a live Streamlit dashboard
6. Logs every decision for full transparency and audit

**Primary demo scenario: Missing Person response** (child, elderly wanderer, abduction risk)

---

## Agentic AI Archetypes Used

| Archetype | Where Applied |
|-----------|--------------|
| 🧠 Cognitive Load Reducer | Triage agent surfaces urgency + entities instantly |
| 🔗 Invisible Coordinator | Chains triage → resource → gatekeeper agents |
| ⚖️ Decision Gatekeeper | Confidence-scored auto-dispatch vs. escalate logic |
| 🛡️ Human–AI Boundary Manager | Human always has final say; all decisions are logged |

---

## Project Structure

```
emergency-ai/
├── data/
│   ├── incidents.json       # 15 simulated 911 call scenarios
│   └── resources.json       # 20 simulated emergency units
├── agents/
│   ├── triage_agent.py      # watsonx.ai — classifies incident + extracts entities
│   ├── resource_agent.py    # matches nearest available units by type
│   └── gatekeeper_agent.py  # decides auto-dispatch vs. escalate
├── utils/
│   ├── watsonx_client.py    # IBM watsonx.ai SDK setup
│   ├── data_loader.py       # JSON data helpers
│   └── geo_utils.py         # distance + ETA calculations
├── ui/
│   └── dashboard.py         # Streamlit dispatcher dashboard
├── logs/
│   └── decisions.jsonl      # auto-appended decision log
├── .env.example             # template for credentials
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- An IBM Cloud account (free at [cloud.ibm.com](https://cloud.ibm.com))

### 2. Get your watsonx.ai API Key
1. Sign up free at [cloud.ibm.com](https://cloud.ibm.com)
2. Go to **[cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)** → Create API Key → Copy it
3. Go to **[dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)** → New Project → Copy the Project ID from the URL

### 3. Configure credentials
```bash
cp .env.example .env
# Edit .env and fill in your WATSONX_API_KEY and WATSONX_PROJECT_ID
```

Your `.env` file should look like:
```
WATSONX_API_KEY=your-api-key-here
WATSONX_PROJECT_ID=your-project-id-here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the dashboard
```bash
streamlit run ui/dashboard.py
```

Open your browser to `http://localhost:8501`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Reasoning | IBM watsonx.ai — Granite 13B Instruct |
| Agent Orchestration | Python (manual agent chaining) |
| Data | Simulated JSON (15 incidents, 20 resources) |
| UI | Streamlit |
| Config/Secrets | python-dotenv |
| Decision Logging | JSONL file |

---

## Responsible AI Design

- **Human always in control** — dispatcher must approve or override every recommendation
- **Explainable decisions** — every AI decision includes a plain-language justification
- **Full audit trail** — all decisions logged with timestamp, incident ID, and dispatcher action
- **Safe fallbacks** — if AI fails at any step, the system escalates to human by default
- **Vulnerability detection** — extra caution automatically applied for children, elderly, disabilities

---

## Demo Scenarios

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the full 3-scenario walkthrough.
