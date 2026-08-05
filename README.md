# Trendly Agentic Support Assistant

An enterprise-grade, agentic AI support assistant built for the Yellow.ai Forward Deployed Engineer screening assignment. This system functions as a robust customer service orchestrator, blending deterministic business logic with non-deterministic Large Language Model (LLM) reasoning to provide a seamless, secure, and accurate customer experience.

---

## 1. Complete Architecture

The system is built on a modern, decoupled architecture designed for high availability, low latency, and strict guardrails. It separates deterministic policy engines from generative AI, ensuring that the AI cannot hallucinate business decisions.

### A. Core Architectural Pillars
1. **Frontend Presentation Layer (Streamlit UI)**
   - Built with Streamlit (`ui.py`) to provide a highly interactive, responsive, and reactive chat interface.
   - Customized with injected CSS to simulate a pitch-black, minimalist ChatGPT-style dark mode aesthetic.
   - Asynchronously communicates with the backend via REST HTTP POST requests.
   - Completely stateless; simply renders the responses from the FastAPI backend.

2. **Backend API Layer (FastAPI)**
   - Acts as the central nervous system and HTTP entry point.
   - Handles incoming HTTP traffic, CORS, and schema validation via strict Pydantic models.
   - Manages asynchronous threading (`uvicorn`) to prevent the AI inference from blocking the main event loop, ensuring high concurrency capabilities.

3. **Orchestration Layer (LangGraph State Machine)**
   - Replaces fragile linear prompting with a cyclic Directed Acyclic Graph (DAG) state machine.
   - Maintains conversational memory across turns using a checkpointer (`MemorySaver`).
   - Forces the LLM into a strict **ReAct (Reason + Act)** loop, ensuring it evaluates its own outputs before finalizing a response.
   - State edges are defined by conditional logic (e.g., `continue_to_tools` vs `end_conversation`).

4. **Security & Guardrail Layer**
   - **Authentication:** Users must verify their email and order ID before accessing private data. The AI refuses lookup tools without this.
   - **Input Guardrails:** Regex and semantic checks prevent prompt injection (e.g., "ignore previous instructions") and jailbreaks.
   - **Output Guardrails:** Blocks the accidental exposure of PII (Personally Identifiable Information), unauthorized discounts, or inappropriate language.

5. **Deterministic Rules Engine**
   - Business logic (e.g., calculating if an order is within the 30-day return window) is executed entirely by deterministic Python code, **not** the LLM. 
   - The LLM acts purely as a linguistic interface to narrate the engine's structured `Verdict` (Boolean success/failure and reasoning strings).

---

## 2. System Workflow & Node Transitions

When a user interacts with the Trendly Assistant, the payload flows through a strict pipeline:

1. **User Input & Ingestion:** The frontend POSTs the message and a unique `session_id` to the FastAPI `/chat` endpoint.
2. **Input Validation:** The Guardrails module scans the payload for malicious intents or injections. If a threat is detected, a canned rejection response is immediately returned.
3. **State Restoration:** LangGraph loads the user's historical conversational context using the `session_id`.
4. **Agent Routing (LLM Node):** 
   - The LLM (powered by Groq for ultra-low latency) analyzes the intent against the master System Prompt.
   - The LLM decides either to output a final text response (Edge: `END`) or invoke a tool (Edge: `ToolNode`).
5. **Tool Execution (ToolNode):**
   - **Policy Search (`search_policy_tool`):** A RAG-style lookup against the markdown policy document.
   - **Order Lookup (`get_order_tool`):** Looks up order status from the simulated JSON database.
   - **Return/Exchange (`process_return_exchange_tool`):** Passes the order data to the Deterministic Rules Engine, calculating date deltas and returning a hard boolean eligibility status.
   - **Escalate (`escalate_to_human_tool`):** Automatically triggers if the user is angry, mentions legal action, or requires manual intervention, returning structured escalation metadata.
6. **Re-Evaluation:** The tool output is fed back into the Agent Node. The LLM synthesizes the data and crafts a natural, polite response.
7. **Output Validation:** The Guardrails module scans the final synthesized text to ensure no sensitive data is leaked.
8. **Delivery:** FastAPI returns the JSON response, and Streamlit dynamically renders it in the UI.

---

## 3. Technology Stack & Tooling

This project leverages modern, industry-standard tooling to achieve high performance:

### Core Backend & Web Server
- **Python 3.9+**: The foundational language.
- **FastAPI**: A high-performance web framework for building APIs, chosen for its native async support and automatic OpenAPI documentation.
- **Uvicorn**: An ASGI web server implementation used to run FastAPI.
- **Pydantic**: For strict data validation and serialization.

### AI & Orchestration
- **LangChain**: Used for tool binding, prompt templating, and model interaction abstractions.
- **LangGraph**: Framework for building stateful, multi-actor applications with LLMs. Crucial for cyclic ReAct agents.
- **Groq API**: An ultra-fast inference engine utilizing LPU (Language Processing Unit) architecture. We utilize the `llama-3.3-70b-versatile` model to achieve near-instant reasoning speed (often generating >300 tokens per second).

### Data & State Management
- **In-Memory Datastores**: JSON and Markdown files loaded into memory at runtime for simulated database interactions.
- **LangGraph MemorySaver**: Manages In-memory persistence for conversational state tracking keyed by session IDs.

### Tooling, UI & Testing
- **Streamlit**: Python-based frontend framework for building the chat UI without writing React/Node.js.
- **Pytest**: For rigorous unit and integration testing of the agent's deterministic rules and guardrails.
- **Docker & Docker Compose**: For containerized, cloud-agnostic deployment.

---

## 4. API Documentation & Endpoints

The FastAPI backend exposes the following REST architecture:

### `GET /health`
Used by load balancers and deployment health-checks to verify the service is running.
- **Response:** `200 OK`
- **Body:** `{"status": "healthy"}`

### `POST /chat`
The primary interaction endpoint for the LangGraph agent.
- **Request Headers:** `Content-Type: application/json`
- **Request Body (JSON):**
  ```json
  {
    "session_id": "usr_998234",
    "message": "I want to return my order ORD101."
  }
  ```
- **Response Body (JSON):**
  ```json
  {
    "reply": "I can help with that. Could you please confirm the email address used for the order?",
    "escalated": false
  }
  ```

### `GET /docs`
Provides an interactive, auto-generated Swagger UI interface for testing the API directly in the browser.

---

## 5. Detailed Project Structure

```text
trendly-agent/
├── .env                        # Environment variables (e.g., GROQ_API_KEY)
├── .gitignore                  # Git exclusion rules
├── Dockerfile                  # Containerization instructions for the API
├── docker-compose.yml          # Multi-container orchestration (UI + API)
├── README.md                   # You are reading this
├── requirements.txt            # Python dependency definitions
├── start.sh                    # Deployment boot script
│
├── app/                        # Main Application Package
│   ├── __init__.py
│   ├── main.py                 # FastAPI application factory and routing
│   ├── agent.py                # LangGraph definition, MemorySaver, and ReAct loop
│   ├── prompts.py              # Master system prompts, tone instructions, and guardrails
│   ├── state.py                # TypedDict definitions for graph memory and message passing
│   └── tools.py                # LangChain tool bindings (Order, Policy, Escalation)
│
├── data/                       # Simulated Knowledge Base / Database
│   ├── orders.json             # Mock customer order database (status, dates, items)
│   └── trendly_policy.md       # The official store policy document for RAG lookups
│
├── ui.py                       # Streamlit Frontend application and custom CSS injection
│
└── tests/                      # Automated Test Suite
    ├── __init__.py
    └── test_agent.py           # Unit tests validating prompt logic and tool routing
```

---

## 6. Quickstart & Local Deployment

### Option A: Fully Containerized (Docker Compose) - Recommended
The easiest way to run the entire stack (FastAPI Backend + Streamlit UI).
1. Clone the repository.
2. Copy the environment file: `cp .env.example .env`
3. Add your `GROQ_API_KEY` to `.env`.
4. Run:
   ```bash
   docker-compose up --build
   ```
- The **Streamlit UI** will be available at `http://localhost:8501`.
- The **FastAPI Backend** will be available at `http://localhost:8000`.

### Option B: Local Development (Bare Metal)
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Groq API Key:
   ```bash
   export GROQ_API_KEY="your_api_key_here"
   ```
4. Start the backend server:
   ```bash
   PYTHONPATH=. uvicorn app.main:app --reload --port 8000
   ```
5. In a separate terminal, start the Streamlit UI:
   ```bash
   source venv/bin/activate
   streamlit run ui.py
   ```

---

## 7. Cloud Deployment (Production)

This repository is fully optimized for PaaS deployments (Render, AWS App Runner, Heroku, etc.).

### Backend (Render Web Service)
1. Connect this repository to Render.
2. Select **Web Service**.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `./start.sh` (or `uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
5. Add Environment Variable: `GROQ_API_KEY`.

### Frontend (Streamlit Community Cloud)
1. Connect this repository to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Select `ui.py` as the main file path.
3. The frontend is hardcoded to look for the deployed Render backend URL. No environment variables are required for the frontend to function!
