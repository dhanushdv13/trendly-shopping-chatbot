# Solution Details

## Architecture Summary
```
                    CUSTOMER
                       │
                       ▼
               ┌──────────────┐
               │ Streamlit UI │  
               └──────┬───────┘
                       │  HTTP
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
   ┌───────────┬────────┼────────┬───────────────┬───────────────┐
   ▼           ▼        ▼        ▼               ▼               ▼
get_order  search_   check_    create_return/  escalate_to_    (guardrail
           policy   eligibility   exchange       human           checks run
                                                                  inline in
                                                                  prompt +
                                                                  post-check)
   │           │        │             │               │
   ▼           ▼        ▼             ▼               ▼
orders.json  policy.md  (combines   orders.json    escalation
                         both)      (write)        summary object
   └───────────┴────────┴─────────────┴───────────────┘
                        │
                        ▼
                 Conversation State
              (order_id, intent, history)
                        │
                        ▼
                  Response to customer
```

## Key Trade-Offs
- **Keyword-based Policy Search vs Vector DB:** For a small `trendly_policy.md` file (under 600 words), a simple python string split and keyword search is drastically lighter, faster, and easier to debug than setting up an embedding model and a vector DB (like Chroma or FAISS). A vector DB would be overkill and complicate the setup.
- **In-Memory Store vs Database:** The `orders.json` is read from disk every time. In a real system, this would be an SQL/NoSQL DB. Modifying returns/exchanges currently only returns successful dictionaries and doesn't write back to the JSON to avoid data races and keep it stateless for demo purposes.
- **Hardcoded Post-Generation Guardrails vs Prompt Guardrails:** Asking the LLM to strictly refuse discounts is effective but imperfect. Adding Python logic (post-generation Regex/string checks) ensures absolute prevention of "discounts" and leakage of other users' orders.

## Known Limitations
- **No Real Authentication:** The Streamlit UI doesn't require a login. In a real system, the `session_id` should be tied to a securely authenticated user context, meaning the agent wouldn't even need a guardrail for "other users' orders" because the backend would strictly query the DB only for the logged-in user.
- **Brittle Policy Parsing:** The keyword search heavily relies on headers (`## `) and specific wording. Reformatting the markdown could break the search logic.
- **Non-Persistent Thread Memory:** LangGraph's MemorySaver is used, but it's ephemeral (in memory) since it restarts with the server. A proper Checkpointer with SQLite/Postgres is needed for production.

## Discovery Questions for Trendly Operations
1. What's the actual return window and are there per-category exceptions (e.g., intimates, heavy items)?
2. Who should escalations route to, and what Service Level Agreement (SLA) applies (e.g., 2 hours vs 24 hours)?
3. Should the agent be allowed to auto-approve refunds under some dollar threshold, or always require human sign-off?
4. Is there a real order-management REST API or GraphQL endpoint to integrate with instead of a static JSON file?
5. What tone/brand voice guidelines should the agent follow when talking to customers? (e.g., highly formal, casual, emojis allowed?)
