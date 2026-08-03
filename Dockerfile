FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports for both FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501

# Copy the start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Run both services
CMD ["/start.sh"]
