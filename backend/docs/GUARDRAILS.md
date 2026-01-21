# GUARDRAILS.md
## Bible Therapy Assistant (BTA)
### Core Guardrails — Version 1 Scope

---

## 1. Purpose

This document defines the **system-level guardrails** for **Bible Therapy Assistant (BTA) Version 1**.

A **guardrail** is an enforceable architectural constraint that **prevents execution** of behaviors that are:
- Out of scope
- Legally restricted
- Ethically unsafe
- Theologically ambiguous
- Cost-unpredictable

Guardrails are **preventive**, **fail-closed**, and **version-aware**.  
They are not prompts, UI messages, or policies — they are execution controls.

---

## 2. Core Guardrail Identifier

**CORE-GUARDRAIL-V1-SCOPE**

This is the master guardrail required to pass:
- **PI-GATE-V1-GTM-READY**

No V1 release is permitted without this guardrail enforced.

---

## 3. Guardrail Domains

### 3.1 Capability Guardrail

**Objective:**  
Prevent execution of deferred or future capabilities.

**Blocked Capabilities in V1:**
- Any LLM calls (local or external)
- Embeddings / RAG pipelines
- Commentary ingestion
- Licensed Bible translations
- Safety escalation logic
- Dynamic tier routing

**Enforcement Mechanism:**
- Feature flags default to `False`
- No fallback execution paths
- No auto-upgrade logic

**Primary Control:**
- `config/feature_flags.py`
- `backend/services/query_service.py`

---

### 3.2 Content & License Guardrail

**Objective:**  
Ensure only legally safe, public-domain content is used.

**Allowed Content in V1:**
- King James Version (KJV) Bible only

**Explicitly Disallowed:**
- Good News Bible (GNB / GNT)
- Complete Jewish Bible (CJB)
- NIV, ESV, NLT, CSB
- Any licensed or restricted translations

**Enforcement Mechanism:**
- Translation allowlist
- Static corpus loading
- No dynamic content ingestion

---

### 3.3 Theology Guardrail

**Objective:**  
Prevent inferred, blended, or undisclosed theological interpretation.

**Rules:**
- No theology inferred from user input
- No commentary execution in V1
- No interpretive synthesis beyond verse presentation and neutral summary
- Theology must be **declared metadata**, never inferred

**Required Design Artifact:**
- `THEOLOGICAL-DISTINCTIVENESS-MAP` (design-only in V1)

---

### 3.4 Safety & Ethics Guardrail

**Objective:**  
Ensure BTA does not act as a medical, psychological, or crisis system.

**Blocked Behaviors:**
- Diagnosis
- Crisis intervention
- Emotional escalation
- Prescriptive spiritual counseling

**Flag State:**
- `ENABLE_SAFETY_ESCALATION = False`

**Behavior on Trigger:**
- Neutral response
- No redirection to emergency workflows
- No classification of user mental state

---

### 3.5 Cost Guardrail

**Objective:**  
Guarantee predictable, minimal operational cost in V1.

**Enforced Conditions:**
- Zero LLM token usage
- CPU-only execution
- Static storage only
- No third-party inference APIs

**Outcome:**
- Flat, predictable AWS cost baseline
- No variable usage charges

---

## 4. Guardrail Enforcement Map

| Guardrail Domain | Enforcement Layer | Location |
|----------------|------------------|----------|
| Capability | Feature flags + code guards | `feature_flags.py`, `query_service.py` |
| Content License | Allowlist | Bible data loader |
| Theology | Design constraint | `/docs/architecture/` |
| Safety | Feature flag | Safety hooks |
| Cost | Architecture | No external calls |

---

## 5. Guardrail Failure Model

| Event | System Behavior |
|-----|----------------|
| Guardrail hit | Hard failure |
| Fallback | None |
| Logging | Yes |
| User message | Neutral (“Not available in this version”) |
| Auto-enable | Never |

Guardrails are **fail-closed by design**.

---

## 6. Version Inheritance Rule

> Guardrails cannot be removed.
> They may only be **relaxed by a higher version gate**.

Examples:
- V1 → LLM disabled
- V1.x → LLM flag exists but defaults OFF
- V2 → PI-GATE-V2 explicitly permits enablement

---

## 7. PI-Gate Dependency

**PI-GATE-V1-GTM-READY requires:**
- CORE-GUARDRAIL-V1-SCOPE defined
- Guardrails mapped
- Guardrail enforcement verified
- Guardrail behavior documented

Failure of any guardrail = **release blocked**.

---

## 8. Status

- Guardrails: **ACTIVE**
- Scope: **LOCKED**
- Version: **V1.0**
- Release posture: **Controlled Go-To-Market**

---

*This document is authoritative for BTA Version 1.*
