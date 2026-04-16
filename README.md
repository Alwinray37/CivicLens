# COMP490
Group project for CSUN Senior Design. 

CivicLens helps users follow local civic meetings by combining meeting videos with AI-generated summaries, agenda breakdowns, transcripts, and a meeting-specific chatbot.

Group Members:
- Alwin Ray Roble
- Alexander Leontiev
- Thomas Scott
- Nikita Ulianov

## Tech Stack
- Frontend: React + Vite
- Backend API: Python (FastAPI)
- Data/Infrastructure: Docker Compose

## Project Structure

```text
COMP490/
├── frontend/      # React + Vite web app
│   ├── src/               # Main application source code
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Route-level page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── styles/        # Shared styling modules/files
│   │   ├── util/          # Helper and utility functions
│   │   └── assets/        # Static assets used by the app
│   │       └── images/    # Image files used in UI/docs
│   ├── public/            # Public static files served as-is
│   └── tests/             # Frontend test files
├── BackendAPI/    # FastAPI backend service
│   ├── src/
│   │   └── models/
│   └── tests/
│       └── integration_tests/
├── Models/        # AI/processing scripts and generated meeting artifacts
│   ├── Agenda_Items/
│   ├── ASR_Whisperx/
│   ├── Summaries/
│   └── tests/
│       └── chunker/
├── DB/            # SQL scripts and database backups
├── Docs/          # Project documentation (API docs, user guide)
└── docker-compose.yaml
```

- `frontend/`: UI pages, components, hooks, and client-side assets.
- `BackendAPI/`: API endpoints, backend models, and backend tests.
- `Models/`: meeting processing logic, summaries, transcripts, and related outputs.
- `DB/`: database schema/setup scripts and backup data.
- `Docs/`: project documentation for users and developers.

## Prerequisites
- Node.js (LTS recommended) and npm
- Docker Desktop (or Docker Engine with Compose support)

## Quick Start (from repo root)

### 1) Install frontend dependencies
```bash
cd frontend
npm install
cd ..
```

### 2) Start backend services
```bash
docker compose up --watch
```

### 3) Start frontend
```bash
cd frontend
npm run dev
```

The frontend will run locally and connect to backend services started via Docker Compose.

## Frontend Commands

Run these commands from the `frontend/` directory.

### Start the frontend dev server
```bash
npm run dev
```

### Run frontend unit tests
```bash
npm run test -- --run
```

This runs the Vitest unit tests under `frontend/tests/unit` once and exits, which matches how CI runs them.

### Run the frontend integration-style regression test
```bash
npm run test:integration
```

This is separate from the unit test suite because it exercises the API-dependent regression test.

### Lint the frontend
```bash
npm run lint
```

### Build the frontend
```bash
npm run build
```

## Troubleshooting
- Make sure Docker is running before starting backend services.
- If data is not loading, remove containers and restart from repo root:

```bash
docker compose down -v
docker compose up --watch
```
