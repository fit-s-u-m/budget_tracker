FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# FROM python:3.12-slim
#
# # Install system deps
# RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
#
# # Install uv
# RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# ENV PATH="/root/.cargo/bin:$PATH"
# CMD [whcih,uv]
#
# WORKDIR /app
#
# # Copy only dependency files first (better caching)
# COPY pyproject.toml uv.lock ./
#
# # Install dependencies
# RUN uv sync --frozen
#
# # Copy the rest of the app
# COPY . .
#
# CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#
# FROM python:3.13-slim
#
# WORKDIR /app
