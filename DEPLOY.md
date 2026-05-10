# Deployment Instructions

The full project source code and deployment artifacts are available at: https://github.com/Alwinray37/CivicLens

## Current Deployment Status

CivicLens is not currently documented here as a public production deployment with a live URL. The repository does include Docker-based deployment files and environment templates that allow the project to be started in a deployment-like environment.

## Requirements

- Docker Desktop or Docker Engine with Docker Compose
- Node.js and npm, if running the frontend outside Docker
- NVIDIA GPU support for the default Ollama container setup
- Native Ollama installation for the no-GPU development setup
- A `.env` file based on `.env.example`

## Configuration

Copy the root environment template and fill in the required values:

```bash
cp .env.example .env
```

Do not commit real `.env` files. The repository includes `.env.example` and `frontend/.env.example` as configuration references.

## GPU Docker Deployment

Use this path on a machine with NVIDIA GPU support:

```bash
docker compose up --watch
```

Services are defined in `docker-compose.yaml`.

Expected local endpoints:

- Frontend: `http://localhost:80`
- API: `http://localhost:8000`

## No-GPU / Mac Deployment

Use this path on a Mac or machine without NVIDIA GPU support. Ollama must run natively on the host.

Install and start Ollama:

```bash
brew install ollama
ollama pull smollm:135m
ollama pull nomic-embed-text:latest
ollama serve
```

Start the Docker services:

```bash
docker compose -f docker-compose.dev.yaml up
```

Expected local endpoints:

- Frontend: `http://localhost:80`
- API: `http://localhost:8000`

## Production Compose Files

The repository also includes:

- `docker-compose.prod.yaml`
- `docker-compose.local.yaml`
- `docker-compose.dev.yaml`

These files support different runtime environments. Production deployment requires real environment values, persistent volumes, and server-specific networking.

## Validation

After startup, validate the deployment with:

```bash
curl http://localhost:8000/
curl http://localhost:8000/dbTestConnection
```

For frontend checks:

```bash
cd frontend
npm install
npm run lint
npm run test -- --run
npm run build
```

## Branching Model

- `main`: stable production-oriented branch
- `development`: active integration branch
- feature/task branches: used for focused changes before merging

The current working branch is `development`.
