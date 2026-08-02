# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| Latest release | :white_check_mark: |
| Older releases | :x: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, report them via **GitHub Security Advisories**:

1. Go to the [Security tab](../../security) of this repository
2. Click "Report a vulnerability"
3. Fill out the advisory form with details

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 5 business days
- **Regular updates**: At least every 7 days until resolved

## Security Best Practices

When deploying IncidentOps AI:

### Secrets Management

- **Never commit secrets** to version control
- Set a unique `JWT_SECRET_KEY` through environment variables or a secrets manager
- Use separate credentials for dev/staging/prod
- Rotate credentials regularly
- The app will **refuse to start** in production if `JWT_SECRET_KEY` is left at its default

### Webhook Security

- Configure `GITHUB_WEBHOOK_SECRET` for GitHub webhook signature verification (HMAC-SHA256)
- Configure `PAGERDUTY_WEBHOOK_SECRET` for PagerDuty webhook signature verification
- Configure `SLACK_SIGNING_SECRET` for Slack request verification
- All webhook endpoints use constant-time comparison to prevent timing attacks

### Network Security

- Deploy behind a reverse proxy (nginx, Traefik, etc.)
- Use TLS for all external communications
- Restrict API access to authorized networks
- Enable audit logging

### Authentication & Authorization

- Enable proper JWT-based authentication for production
- Set `DEMO_MODE=false` in production (the default)
- Review the seeded demo users and remove them in production

### Agent Sandboxing

- AI agent pipeline actions are logged in the audit trail
- All AI recommendations require human approval before execution
- Monitor agent actions via the audit log API

## Secure Coding Guidelines & Code Review Checklist

When contributing to IncidentOps AI, all PRs must adhere to the following secure coding guidelines. 

### 1. Authorization & Role-Based Access Control (RBAC)
- **Role-Permission Matrix:** Verify that the 9-role matrix (Owner, Admin, Auditor, Incident Commander, Responder, SME, Observer, External Stakeholder, Automation) is strictly enforced.
- **Endpoint Protection:** Ensure every new endpoint utilizes the `@require_role(...)` dependency to explicitly whitelist authorized roles. Do not rely solely on `@get_current_user`.

### 2. IDOR (Insecure Direct Object Reference) Prevention
- **Workspace Isolation:** Verify every endpoint and database query scopes data access to the user's `workspace_id`.
- **Ownership Checks:** Even with a valid JWT and role, endpoints modifying resources (e.g., updating/deleting incidents) must verify the resource belongs to the user's current workspace.

### 3. Input Validation & Injection Prevention
- **Pydantic Schemas:** Use Pydantic schemas (`BaseModel`) for all incoming request payloads. Avoid accessing `request.json()` directly.
- **ORM Parameterization:** Use SQLAlchemy ORM or parameterized queries exclusively to prevent SQL injection.
- **String Constraints:** Apply `min_length`, `max_length`, and regex `pattern` validation on string inputs to prevent buffer overflows and unexpected input formatting.

### 4. XSS (Cross-Site Scripting) Prevention
- **Frontend Sanitization:** React escapes values by default. Avoid `dangerouslySetInnerHTML` entirely.
- **Rich Text / Markdown:** If rendering markdown for incident descriptions or AI recommendations, use a strict sanitizer (e.g., `DOMPurify`) before rendering.

### 5. File Upload Security (Attachments Module)
- **Type Validation:** Validate MIME types explicitly. Do not rely solely on file extensions.
- **Storage Isolation:** Store uploaded artifacts in a secure, isolated bucket or directory with restricted permissions.
- **Execution Prevention:** Disable execution permissions on the upload directory and serve files with `Content-Disposition: attachment` to prevent inline execution of malicious scripts.

## Known Security Considerations

### AI Agent Execution

IncidentOps AI agents analyze incidents and propose remediation actions. All proposed actions require human approval.

**Mitigations:**
- Human-in-the-loop approval workflow
- Full audit trail of all AI recommendations
- Confidence scoring for all root cause hypotheses

### LLM Prompt Injection

Like all LLM-powered tools, IncidentOps AI may be susceptible to prompt injection attacks.

**Mitigations:**
- Input validation and sanitization
- Separate system and user contexts
- Human approval for all recommended actions

### Data Privacy

The system processes incident data including logs and metrics.

**Mitigations:**
- Audit logging for all data access
- RBAC for sensitive operations
- Environment-variable-based configuration (no hardcoded secrets)

## Security Features

- **Webhook signature verification** (HMAC-SHA256 for GitHub, PagerDuty, Slack)
- **JWT-based authentication** with configurable expiry
- **Production secret validation** (app refuses to start with default secrets)
- **Audit logging** (all user and system actions tracked)
- **Human-in-the-loop approval** for AI recommendations
- **Gitleaks CI integration** (secret scanning on every push)
- **Structured JSON logging** (searchable, filterable production logs)
