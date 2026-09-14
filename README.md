# 🤖 Self-Evaluating Lesson Content Generator

## GenAI Engineer – Content Systems Take-Home Assessment

An enterprise-oriented agentic system that creates beginner AI lessons and decides whether they are good enough to ship.

The system follows:

> **Generate → Evaluate → Learn → Regenerate → Ship**

---

# 🎯 Assignment Coverage

| Assessment Requirement | Implementation |
|---|---|
| Generate lesson | Azure OpenAI Generator |
| Evaluate quality | Independent structured Evaluator |
| Hard pass/fail | 6 mandatory checkpoints |
| Regenerate | LangGraph conditional loop |
| Termination | Maximum 2 retries |
| Rejection log | Stored and displayed |
| Self-evolving | Previous failures influence prompts |
| Persistent memory | SQLite |
| Agentic workflow | LangGraph |
| UI | Streamlit |
| Enterprise readiness | Azure OpenAI v1 endpoint |

---

# 🏗 Architecture

```text
                        ┌───────────────┐
                        │     USER      │
                        │ Topic: RAG    │
                        └───────┬───────┘
                                │
                                ▼
                       ┌────────────────┐
                       │   STREAMLIT    │
                       │       UI       │
                       └────────┬───────┘
                                │
                                ▼
                       ┌────────────────┐
                       │   LANGGRAPH    │
                       │ ORCHESTRATOR   │
                       └────────┬───────┘
                                │
                ┌───────────────▼────────────────┐
                │           GENERATOR             │
                │        Azure OpenAI             │
                └───────────────┬────────────────┘
                                │
                                ▼
                          BEGINNER LESSON
                                │
                                ▼
                ┌───────────────────────────────┐
                │           EVALUATOR            │
                │ Azure OpenAI + Structured JSON │
                └───────────────┬───────────────┘
                                │
                         ┌──────┴──────┐
                         │             │
                       PASS           FAIL
                         │             │
                         ▼             ▼
                      SHIP      ┌─────────────┐
                                │   SQLITE    │
                                │   MEMORY    │
                                └──────┬──────┘
                                       │
                                       ▼
                                  REGENERATE
                                       │
                                  Max 2 retries
```

---

# 🧪 Hard Quality Gates

Every check must pass.

1. **Accuracy**
2. **Beginner Language**
3. **Relatable Example**
4. **No Unexplained Jargon**
5. **What + Why + How**
6. **Teaching Flow**

There is no partial credit.

A single critical failure triggers rejection.

---

# ☁️ Azure OpenAI

This project uses the current Azure OpenAI v1 endpoint style:

```text
https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/
```

Environment variables:

```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE-NAME.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_EVALUATOR_DEPLOYMENT_NAME=
MAX_RETRIES=2
```

`AZURE_OPENAI_EVALUATOR_DEPLOYMENT_NAME` is optional.

If supplied, the evaluator uses a separate Azure deployment.

---

# 🚀 Setup

## 1. Clone

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd genai-content-system
```

## 2. Create virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Azure

Copy:

```bash
.env.example
```

to:

```bash
.env
```

Add your Azure OpenAI credentials and deployment name.

## 5. CLI run

```bash
python main.py --topic "Introduction to RAG"
```

## 6. Streamlit UI

```bash
streamlit run app.py
```

---

# 🎥 Deliberate Error Demo

For the Loom video:

```bash
python main.py --topic "Introduction to RAG" --inject-error
```

The first attempt contains:

```text
RAG permanently retrains the model every time it reads a document.
Vector database.
```

The evaluator should reject it for:

- Accuracy
- Unexplained jargon

The failure is then:

1. Added to the rejection log
2. Stored in persistent SQLite memory
3. Converted into actionable feedback
4. Fed to the next generation attempt
5. Corrected automatically

---

# 🧠 Self-Evolving Memory

The system stores recurring failure patterns:

```text
Attempt fails
     ↓
Failure reason
     ↓
Recommended fix
     ↓
SQLite persistence
     ↓
Future prompt receives learned patterns
     ↓
Reduced chance of repeated failures
```

This memory persists across application runs.

---

# 📁 Project Structure

```text
genai-content-system/
├── app.py               # Streamlit UI
├── main.py              # CLI
├── service.py           # Application service
├── graph.py             # LangGraph workflow
├── llm.py               # Azure OpenAI client
├── prompts.py           # Prompts
├── schemas.py           # Pydantic schemas
├── memory.py            # SQLite persistence
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
└── output/
```

---

# 💡 Key Design Decisions

## Why LangGraph?

The problem requires conditional routing and retries. LangGraph makes the workflow explicit and guarantees state-based orchestration.

## Why hard pass/fail?

A numerical score can hide a serious failure. A lesson with an incorrect definition should not ship simply because its average score is high.

## Why structured output?

The evaluator must produce predictable machine-readable results. Pydantic schemas make PASS/FAIL decisions easier to validate.

## Why persistent memory?

Repeated failure patterns should improve future generations rather than disappearing after one run.

## Why separate evaluator deployment?

Using a separate deployment can reduce generator/evaluator coupling and allows independent model or configuration selection.

## Why maximum retries?

Agentic loops need guaranteed termination and predictable costs.

---

# 🔮 Production Improvements

For a production deployment:

- Azure Key Vault for secrets
- Managed Identity instead of API keys
- Azure Application Insights telemetry
- Azure AI Search for factual grounding
- Claim-level verification
- Separate generator/evaluator models
- Human review queue for max-retry failures
- Content versioning
- Evaluation dashboards

---

# 🎬 Recommended Loom Demo

1. Introduce the problem
2. Show architecture
3. Explain generator
4. Explain hard evaluator
5. Run normal workflow
6. Run deliberate error workflow
7. Show rejection
8. Show retry
9. Show SQLite memory
10. Show Streamlit dashboard
11. Explain production trade-offs
