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
