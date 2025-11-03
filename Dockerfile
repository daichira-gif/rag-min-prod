# ---- Builder Stage ----
# Installs dependencies into a virtual environment.
FROM python:3.11-slim as builder

ENV POETRY_VIRTUALENVS_CREATE=false PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for building python packages
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install only production requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# ---- Final Stage ----
# Copies the virtual environment and source code, resulting in a smaller image.
FROM python:3.11-slim

ENV POETRY_VIRTUALENVS_CREATE=false PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
