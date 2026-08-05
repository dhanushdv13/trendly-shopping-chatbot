# Trendly Agentic Support Assistant

An enterprise-grade, agentic AI support assistant built for the Yellow.ai Forward Deployed Engineer screening assignment. This system functions as a robust customer service orchestrator, blending deterministic business logic with non-deterministic Large Language Model (LLM) reasoning to provide a seamless, secure, and accurate customer experience.

---

## 1. Complete Architecture

The system is built on a modern, decoupled architecture designed for high availability, low latency, and strict guardrails. It separates deterministic policy engines from generative AI, ensuring that the AI cannot hallucinate business decisions.

### A. Core Architectural Pillars
1. **Frontend Presentation Layer (`static/index.html`)**
   - A vanilla HTML, CSS (TailwindCSS), and JavaScript Single Page Application (SPA).
   - Served directly via the FastAPI static file server.
   - Designed to mimic a modern, sleek chat interface with a dark mode aesthetic.
   - Asynchronously communicates with the backend via REST HTTP POST requests.

2. **Backend API Layer (FastAPI)**
   - Acts as the central nervous system.
   - Handles incoming HTTP traffic, CORS, and schema validation via Pydantic models.
   - Manages asynchronous threading to prevent the AI inference from blocking the main event loop.

3. **Orchestration Layer (LangGraph State Machine)**
   - Replaces fragile linear prompting with a cyclic Directed Acyclic Graph (DAG) state machine.
   - Maintains conversational memory across turns using a checkpointer (`MemorySaver`).
   - Forces the LLM into a strict ReAct (Reason + Act) loop, ensuring it evaluates its own outputs before finalizing a response.

4. **Security & Guardrail Layer**
   - **Authentication:** Users must verify their email and order ID before accessing private data.
   - **Input Guardrails:** Regex and semantic checks prevent prompt injection (e.g., "ignore previous instructions") and jailbreaks.
   - **Output Guardrails:** Blocks the accidental exposure of PII (Personally Identifiable Information) or inappropriate language.

5. **Deterministic Rules Engine**
   - Business logic (e.g., calculating if an order is within the 30-day return window) is executed entirely by Python code (`app/core/rules/return_rules.py`), **not** the LLM. 
   - The LLM acts purely as a linguistic interface to narrate the engine's structured `Verdict`.

---

## 2. System Workflow

When a user interacts with the Trendly Assistant, the payload flows through a strict pipeline:

1. **User Input:** The user types a message in the UI (e.g., "I want to return my order").
2. **API Ingestion:** The frontend POSTs the message and a unique `session_id` to the FastAPI `/chat` endpoint.
3. **Input Validation:** The Guardrails module scans the payload for malicious intents or injections. If a threat is detected, the request is immediately rejected.
4. **State Restoration:** LangGraph loads the user's historical conversational context using the `session_id`.
5. **Agent Routing (LLM):** 
   - The LLM (powered by Groq for ultra-low latency) analyzes the intent.
   - It references the strict System Prompt instructions to determine if a tool is required.
6. **Tool Execution:**
   - If the user asks about policy, the `policy_store` RAG tool is invoked.
   - If the user asks about an order, the `verify_identity_tool` triggers. Once authenticated, the `order_store` tool is queried.
   - If the user requests a return, the LLM passes the order data to the **Deterministic Rules Engine**, which calculates the date deltas and returns a hard boolean eligibility status.
7. **Response Synthesis:** The LLM observes the tool's output and crafts a natural, polite response.
8. **Output Validation:** The Guardrails module scans the final synthesized text to ensure no sensitive data is leaked.
9. **Delivery:** FastAPI returns the JSON response to the frontend, rendering it in the UI.

---

## 3. Technology Stack

This project leverages modern, industry-standard tooling to achieve high performance:

### Core Backend
- **Python 3.9+**: The foundational language.
- **FastAPI**: A high-performance web framework for building APIs, chosen for its native async support and automatic OpenAPI documentation.
- **Uvicorn**: An ASGI web server implementation used to run FastAPI.

### AI & Orchestration
- **LangChain**: Used for tool binding, prompt templating, and model interaction abstractions.
- **LangGraph**: Framework for building stateful, multi-actor applications with LLMs. Crucial for cyclic ReAct agents.
- **Groq API**: An ultra-fast inference engine utilizing LPU (Language Processing Unit) architecture. We utilize the `llama-3.3-70b-versatile` model to achieve near-instant reasoning speed.

### Data & State Management
- **In-Memory Datastores**: JSON and Markdown files loaded into memory at runtime for simulated database interactions.
- **LangGraph MemorySaver**: Manages SQLite/In-memory persistence for conversational state tracking.

### Tooling & Testing
- **Pytest**: For rigorous unit and integration testing of the agent's deterministic rules and guardrails.
- **Docker**: For containerized, cloud-agnostic deployment.

---

## 4. Detailed Project Structure

```text
trendly-agent/
├── .env                        # Environment variables (e.g., GROQ_API_KEY)
├── .gitignore                  # Git exclusion rules
├── Dockerfile                  # Containerization instructions
├── README.md                   # You are reading this
├── requirements.txt            # Python dependency definitions
│
├── app/                        # Main Application Package
│   ├── __init__.py
│   ├── main.py                 # FastAPI application factory and endpoints
│   ├── config.py               # Centralized configuration and environment loading
│   │
│   ├── api/                    # API Routing Layer
│   │   └── v1/                 # Versioned API routes (e.g., chat, health)
│   │
│   ├── core/                   # Core Business Logic
│   │   ├── agent/              # LangGraph orchestration
│   │   │   ├── graph.py        # DAG definition and state compilation
│   │   │   ├── state.py        # TypedDict definitions for graph memory
│   │   │   ├── prompts.py      # Master system prompts and constraints
│   │   │   └── tools.py        # LangChain tool bindings (Order, Policy, Escalation)
│   │   │
│   │   └── rules/              # Deterministic Engines
│   │       └── return_rules.py # Python logic for calculating eligibility dates
│   │
│   ├── services/               # Data Access Layer
│   │   ├── order_store.py      # JSON parser and simulated DB for orders
│   │   └── policy_store.py     # Markdown parser and semantic search simulation
│   │
│   └── utils/                  # Cross-cutting concerns
│       └── logger.py           # Structured application logging
│
├── data/                       # Simulated Knowledge Base
│   ├── orders.json             # Mock customer order database
│   └── trendly_policy.md       # The official store policy document
│
├── static/                     # Frontend Assets
│   └── index.html              # The compiled Tailwind UI chat interface
│
└── tests/                      # Automated Test Suite
    ├── conftest.py             # Pytest fixtures and mock setups
    ├── integration/            # End-to-end flow tests
    │   ├── test_agent.py       # LangGraph behavioral tests
    │   ├── test_api.py         # FastAPI endpoint tests
    │   └── test_guardrails.py  # Threat simulation and block verification
    │
    └── unit/                   # Isolated function testing
        ├── test_order_store.py # Data retrieval validation
        ├── test_policy_store.py# Search logic validation
        └── test_rules_engine.py# Deterministic math/date calculations
```

---

## 5. Quickstart & Deployment

### Local Development
1. Create and activate a virtual environment: `python3 -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Set your Groq API Key: `export GROQ_API_KEY="your_api_key_here"`
4. Run tests: `pytest tests/ -v`
5. Start the server: `uvicorn app.main:app --reload`
6. Open your browser to `http://localhost:8000`

### Docker Deployment
The application is fully containerized and ready for PaaS platforms like AWS App Runner or Render.
```bash
docker build -t trendly-agent .
docker run -p 8000:8000 -e GROQ_API_KEY=$GROQ_API_KEY trendly-agent
```
