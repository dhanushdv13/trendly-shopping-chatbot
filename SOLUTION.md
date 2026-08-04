# Trendly Agentic Support Assistant: Solution Document

## 1. Architecture Overview

The system is built as a stateful, tool-calling agentic workflow rather than a traditional conversational chatbot. It is composed of three main layers:

1. **Frontend UI (Streamlit):** A lightweight chat interface that allows users to interact with the agent. It manages local session state and communicates via HTTP POST to the backend API.
2. **Backend API (FastAPI):** Exposes a `/chat` endpoint. It acts as the bridge between the frontend and the LangGraph orchestrator, handling CORS, health checks, and request validation.
3. **Agentic Orchestrator (LangGraph & LangChain):** 
   - **State Management:** Uses LangGraph's `MemorySaver` checkpointer to maintain a multi-turn conversation buffer, allowing the LLM to remember previously mentioned entities (like `order_id`) across turns.
   - **LLM Engine:** Powered by Groq (using `llama-3.1-8b-instant`), chosen for its high-speed inference and excellent tool-calling capabilities on a free tier.
   - **Tools Layer:** A suite of deterministic Python functions (`get_order`, `search_policy`, `check_return_eligibility`, `escalate_to_human`). The LLM is strictly instructed to fetch data via these tools rather than generating facts from its parametric memory.

```text
                    CUSTOMER
                       │
                       ▼
               ┌──────────────┐
               │ Streamlit UI │  
               └──────┬───────┘
                       │  HTTP POST /chat
                       ▼
               ┌──────────────┐
               │   FastAPI    │  
               └──────┬───────┘
                       ▼
             ┌───────────────────┐
             │   LangGraph Agent │  
             │  LLM: Groq (Llama)│
             └─────────┬─────────┘
                        │
          Agent decides which tool(s) to call
                        │
   ┌───────────┬────────┼────────┬───────────────┐
   ▼           ▼        ▼        ▼               ▼
get_order  search_   check_    escalate_to_    (Guardrail
           policy   eligibility   human          checks run
                                                 inline via
   │           │        │             │          Prompting)
   ▼           ▼        ▼             ▼               
orders.json  policy.md  (Logic)    escalation
                                   summary 
```

## 2. Key Trade-Offs

- **Keyword-based Policy Search vs. Vector Database (RAG):** 
  For a small `trendly_policy.md` file (under 600 words), a simple Python string split and keyword search is drastically lighter, faster, and easier to debug than setting up an embedding model and a vector database (like Chroma or FAISS). A vector DB introduces unnecessary latency and dependency bloat for simple, static text retrieval.
  
- **In-Memory Store vs. Relational Database:** 
  The `orders.json` is read from disk every time. In a real system, this would be an SQL/NoSQL database with ACID properties. Modifying returns/exchanges currently only returns successful dictionaries and doesn't write back to the JSON to avoid data races and keep the system stateless for demo deployment purposes.

- **Prompt-Based Guardrails vs. Deterministic Interceptors:** 
  We rely heavily on strict Prompt Engineering to enforce guardrails (e.g., refusing discounts, blocking jailbreaks, handling abuse). While this is highly flexible, prompt-based guardrails are probabilistic. The trade-off is development speed versus absolute certainty. For a strict production environment, deterministic output parsers or a secondary "Evaluator LLM" would be required to scrub outputs before sending them to the user.

- **Groq API vs. OpenAI:**
  Groq was selected to meet the "free-tier" constraint. The trade-off is that free-tier API rate limits (`HTTP 429`) can cause concurrent test failures, whereas a paid OpenAI tier would allow higher throughput.

## 3. Known Limitations

- **No True Authentication Context:** 
  The Streamlit UI does not require a login. In a real system, the `session_id` should be tied to a securely authenticated user context. This would eliminate the need for the LLM to guard against leaking "other users' orders," because the backend tools would simply reject any database query for an order not owned by the authenticated `user_id`.
  
- **Brittle Policy Parsing:** 
  The `search_policy` tool heavily relies on Markdown headers (`## `) and specific keyword matching. If the operations team reformats the markdown without updating the tool logic, the search will break.
  
- **Ephemeral Thread Memory:** 
  LangGraph's `MemorySaver` is currently used for thread persistence. However, because it runs in-memory, thread history is lost whenever the FastAPI server restarts. A production deployment requires a persistent checkpointer (e.g., PostgreSQL or Redis) to maintain multi-day chat histories.

- **Limited Tool Set:**
  The agent currently cannot perform actual mutations (like processing a real refund). It simulates the decision logic but lacks the POST tools to hit a payment gateway like Stripe.

## 4. Discovery Questions for Trendly Operations

Before building this into a real production system, I would need to align with Trendly's Ops and Support teams by asking the following:

1. **Policy Nuances:** What is the actual return window for different categories? Are there per-category exceptions (e.g., intimates, heavy items, electronics) that are not covered in the current markdown document?
2. **Escalation SLAs:** Who should escalations route to, and what Service Level Agreement (SLA) applies? For example, does a "missing package" escalation require a 2-hour response, whereas a "general question" has a 24-hour SLA?
3. **Autonomous Approvals:** Should the agent be allowed to autonomously approve returns and issue refunds under a specific dollar threshold (e.g., items under $20), or does every single financial transaction require human sign-off?
4. **Integration Surface:** What does the actual backend infrastructure look like? Is there a mature REST API, GraphQL endpoint, or Shopify integration we can call for order management, instead of reading a static JSON file?
5. **Brand Voice & Tone:** What are the strict tone and brand voice guidelines the agent must follow? Should the agent be highly formal and corporate, or casual and use emojis? How should it respond to sarcasm?
