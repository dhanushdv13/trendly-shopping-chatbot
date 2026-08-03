# Trendly Support Agent

An agentic customer support assistant built for the fictional fashion retailer, Trendly.

## Overview
This project uses LangGraph and LangChain to create an LLM-powered agent capable of securely retrieving order data, searching store policies, checking return eligibility, processing exchanges, and escalating complex issues to a human agent.

## Features
- **Strict Grounding:** The LLM strictly calls tools to fetch data and never invents order or policy details.
- **Guardrails:** Prevents unauthorized discounts and order information leakage using post-generation checks.
- **Multi-turn Memory:** Keeps context between interactions so the customer doesn't have to repeat their order ID.
- **Streamlit UI:** Provides an easy-to-use chat interface.

## Prerequisites
- Python 3.9+ or Docker & Docker Compose
- A [Groq API Key](https://console.groq.com/keys)

## Installation & Environment Variables

1. Clone this repository.
2. Create a `.env` file in the project root by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your real `GROQ_API_KEY`.

## Running the Application (One-Command)

The easiest way to run the entire stack (FastAPI Backend + Streamlit UI) is using Docker Compose:
```bash
docker-compose up --build
```
- **Streamlit UI:** `http://127.0.0.1:8501`
- **FastAPI Backend:** `http://127.0.0.1:8000`

### Running Locally without Docker
1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start the FastAPI backend:
   ```bash
   PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
3. In a new terminal, start the Streamlit UI:
   ```bash
   source venv/bin/activate
   streamlit run ui.py
   ```

## API Documentation

- **Base URL:** `http://127.0.0.1:8000` (or your public deployment URL)
- **Swagger Docs:** `GET /docs` (Auto-generated interactive API documentation)
- **Health Check:** `GET /health`
  - Returns: `{"status": "healthy"}`
- **Chat Endpoint:** `POST /chat`
  - Request Body: `{"session_id": "string", "message": "string"}`
  - Response Body: `{"reply": "string", "escalated": boolean}`

### Example Request
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "12345", "message": "What is the status of ORD105?"}'
```

## Deployment Information

This repository is ready to be deployed to **Render** or any platform supporting Docker/Web Services. 
A `render.yaml` blueprint is included to automatically deploy both the API and the UI as separate web services. Simply connect this repository to Render and use the blueprint.

To test the frontend against a deployed backend locally, update the `.env` file:
```env
API_URL=https://your-deployed-api-url.onrender.com/chat
```

## Running Tests
To run the automated test suite (requires an active API key):
```bash
PYTHONPATH=. pytest -v tests/test_agent.py
```

## AI vs Hand-Written
This codebase was primarily AI-generated (scaffolding, standard tool implementations, routing logic) based on detailed architecture instructions, but the system prompts, test cases, and precise strict guardrail rules were specified hand-in-hand with human instructions to ensure architectural alignment.
