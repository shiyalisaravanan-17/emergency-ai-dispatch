# Demo Script — Emergency AI Dispatch
**Duration:** 3–5 minutes
**Setup:** Streamlit dashboard running at http://localhost:8501

---

## Before you start

Say this to your audience:

> "Emergency dispatchers handle hundreds of calls a day. Each call requires quick judgement — who's calling, what happened, how serious is it, which unit is closest, should I send one or two? We built an AI agent that handles all of that in seconds, while keeping the dispatcher in full control."

---

## Scenario A — Missing Child (Primary Demo)

**Incident:** INC001 — 7-year-old boy missing from Riverside Park

### Steps:
1. In the sidebar, select: **[INC001] Missing Person — Riverside Park, Manhattan**
2. The 911 transcript appears — read part of it aloud:
   > _"My 7-year-old son was playing in Riverside Park about an hour ago and now I can't find him anywhere..."_
3. Click **"Analyse Incident with AI"**
4. Point out as results appear:
   - **Urgency Score: 5/5 — CRITICAL** (red banner)
   - **Vulnerability Flag: child**
   - **Subject description** extracted automatically
   - **Recommended units:** Patrol Unit + Search & Rescue Team
   - **AI Decision: ESCALATE TO HUMAN** — because urgency is 5 and subject is a child
   - **Justification:** shown in plain English
5. Click **"Approve Dispatch"**
6. Show the Decision Log tab — entry appears with timestamp

**What to say:**
> "In seconds, the AI identified this as a missing child, flagged the vulnerability, found the nearest police and search & rescue team, and correctly escalated to me for final approval — because a child's life is too important to fully automate. I approved with one click and the decision is permanently logged."

---

## Scenario B — Elderly Wanderer

**Incident:** INC002 — 80-year-old with dementia missing from home

### Steps:
1. Select: **[INC002] Missing Person — Elm Street, Midtown**
2. Click **"Analyse Incident with AI"**
3. Point out:
   - Vulnerability flag: **elderly / dementia**
   - AI again escalates rather than auto-dispatching
   - Justification specifically mentions the dementia vulnerability
4. This time, click **"Override / Escalate"**
5. Type a note: `Requesting K9 unit in addition to patrol — subject has medical condition`
6. Click **"Confirm Override"**

**What to say:**
> "The AI flagged dementia as a vulnerability and escalated again — correctly. But as the dispatcher, I decided to add a K9 unit. I overrode the recommendation, added my reason, and that override is now in the audit log. The AI never made the final call — I did."

---

## Scenario C — No Available Search & Rescue Units

**Incident:** INC014 — 10-year-old missing in Prospect Park at dusk

### Steps:
1. Select: **[INC014] Missing Person — Prospect Park, Brooklyn**
2. Click **"Analyse Incident with AI"**
3. Point out:
   - It's getting dark — urgency is high
   - **Resource warning:** No available Search & Rescue units (SAR003 and SAR004 are both busy)
   - AI escalates with justification: _"No available units for required type: search_rescue. Human must arrange mutual aid."_
4. Click **"Override / Escalate"**
5. Type: `Contacting neighbouring district for mutual aid S&R team`

**What to say:**
> "Here's where the AI really proves its value. All search and rescue units are busy. The AI didn't guess or make something up — it immediately flagged the gap and told me I need to arrange mutual aid. That's the kind of honest, transparent AI behaviour you want in a life-or-death situation."

---

## Closing Statement

> "This system demonstrates four key AI archetypes from the IBM framework: the Cognitive Load Reducer, the Invisible Coordinator, the Decision Gatekeeper, and the Human-AI Boundary Manager. Every decision is explainable, every action is logged, and the human is always in control. That's how AI should work in government services."

---

## Tips
- Keep the demo moving — don't wait for AI responses silently, narrate what's happening
- If watsonx.ai is slow, explain: "This is making a live call to IBM's foundation model — in production this would be optimised"
- Emphasise the Decision Log tab at the end — it's a strong closer on transparency
