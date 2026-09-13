FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose web port
EXPOSE 8000

# Seed initial database if not existing, then start FastAPI server
CMD ["sh", "-c", "python seed_data.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
