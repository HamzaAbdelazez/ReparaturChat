## Getting Started

### Running with Docker Compose:

```bash
# Build the Docker images defined in the docker-compose.yml without cache
docker compose build --no-cache

# Start containers in the foreground (attach to logs)
docker compose up

# End containers
docker compose down
```
# Go to backend folder
cd backend

# Install dependencies using Poetry

poetry install

# Run the FastAPI app with Uvicorn
poetry run uvicorn api.main:app --reload --app-dir src


# API will be available at:
# http://127.0.0.1:8000/docs

