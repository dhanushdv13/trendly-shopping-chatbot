#!/bin/bash
# Start FastAPI backend in the background
# We bind to 0.0.0.0 and a port specified by $PORT, defaulting to 8000
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" &

# Wait briefly to let the API start
sleep 2

# Start Streamlit frontend in the foreground
# Streamlit will bind to a different port (8501)
# Note: Streamlit's API_URL will default to 127.0.0.1:8000, 
# communicating locally with the FastAPI background process
streamlit run ui.py --server.port 8501 --server.address 0.0.0.0
