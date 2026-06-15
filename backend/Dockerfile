FROM python:3.13-slim-bookworm

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Generate lock file and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Copy the rest of the application
COPY . .

EXPOSE 8000
