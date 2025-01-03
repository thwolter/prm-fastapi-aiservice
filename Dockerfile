# Use an official Python runtime as a parent image
FROM python:3.11

RUN pip install --no-cache-dir poetry

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install poetry-plugin-export
RUN poetry self add poetry-plugin-export

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies with Poetry
RUN poetry install --no-root --only main --no-dev

# Copy the application code
COPY . /app

# Expose the FastAPI default port
EXPOSE 8000

# Set the default command to run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]