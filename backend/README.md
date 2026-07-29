# IncidentOps AI backend

A small FastAPI service for an incident-response dashboard. It uses Pydantic
models and starts with realistic operational data, so it can be run without a
database. Set `INCIDENTOPS_DATA_FILE` to persist the demo state as JSON.

## Run locally

```powershell
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for Swagger UI. The canonical API is under
`/api/v1`; every endpoint is also available at the root for simple frontend
integration (for example, `GET /incidents` and `GET /api/v1/incidents`).

If `python` is not on your Windows PATH, use the Python launcher (`py`) or your
preferred virtual environment's Python executable.

## Demo credentials

All seeded users use password `demo123`:

| Name | Email | Role |
| --- | --- | --- |
| Maya Chen | `maya.chen@incidentops.dev` | Incident commander |
| Samir Patel | `samir.patel@incidentops.dev` | Responder |
| Lena Ortiz | `lena.ortiz@incidentops.dev` | Admin |

Sign in with:

```json
{ "email": "maya.chen@incidentops.dev", "password": "demo123" }
```

The returned token is an opaque, non-production demo token. In this default
demo mode the incident endpoints remain permissive so a local dashboard can be
explored without extra configuration; do not use this authentication behavior
or the seeded passwords in a production deployment.

## Endpoints

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Liveness check |
| `POST` | `/login` | Demo login and bearer-like token |
| `GET`, `POST` | `/incidents` | List/filter or create incidents |
| `GET`, `PATCH`, `DELETE` | `/incidents/{incident_id}` | Incident detail and CRUD operations |
| `GET` | `/incidents/{incident_id}/logs` | Incident timeline |
| `POST` | `/incidents/{incident_id}/approve` | Approve/reject an AI recommendation |
| `POST` | `/incidents/{incident_id}/resolve` | Mark an incident resolved |
| `GET` | `/analytics` | Dashboard metrics, severity/status counts, trend |
| `GET` | `/agents/status` | AI agent fleet state |
| `GET` | `/audit-logs` | Audit trail, optionally filtered by `incident_id` |
| `POST` | `/slack/test` | Record a safe Slack connectivity test |
| `POST` | `/jira/test` | Record a safe Jira connectivity test |

Incident states are `Open`, `Investigating`, `Waiting Approval`, `Resolved`,
and `Closed`. The seeded data includes incident logs, audit records, AI
recommendations, agent status, Jira sync data, and Slack messages.

## Persistence and configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `INCIDENTOPS_DATA_FILE` | unset | Path to a JSON state file. When unset, every process starts with a fresh seed. |
| `INCIDENTOPS_CORS_ORIGINS` | `*` | Comma-separated allowed browser origins. |

Example persistent run:

```powershell
$env:INCIDENTOPS_DATA_FILE = "$PWD\data\incidentops.json"
uvicorn app.main:app --reload --port 8000
```

## Test

```powershell
cd backend
pytest -q
```

## Docker

```powershell
cd backend
docker build -t incidentops-api .
docker run --rm -p 8000:8000 incidentops-api
```

For durable Docker demo data, mount a directory at `/data` and set
`INCIDENTOPS_DATA_FILE=/data/incidentops.json`.
