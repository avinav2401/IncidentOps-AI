"""Incident Scenario Generator — realistic failure simulations.

Provides a library of 10 diverse incident scenarios, each with its own
logs, metrics, monitor status, and GitHub commit context. The simulator
randomly selects a scenario and injects it into the system, giving the
AI agents fresh, varied evidence to investigate each time.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class Scenario:
    """A complete incident scenario with all evidence for AI agents."""

    # Incident metadata
    title: str
    description: str
    service: str
    severity: str
    affected_users: int
    tags: list[str]

    # Evidence for agents
    logs: str
    metrics: dict[str, str]
    monitor_status: str
    monitor_details: str
    recent_commits: list[str]
    knowledge_context: list[dict] = field(default_factory=list)


# ── Scenario Library ─────────────────────────────────────────────────

SCENARIOS: list[Scenario] = [
    # 1. Payment API Timeout
    Scenario(
        title="Payment API Gateway Timeout",
        description="Payment authorization requests timing out after gateway config change. Error rate above 12% threshold.",
        service="Payment Service",
        severity="P1",
        affected_users=15000,
        tags=["payment", "gateway", "timeout", "critical"],
        logs=(
            "2026-08-03 10:05:01 ERROR [payment-svc] POST /api/v1/charge - Timeout after 30000ms\n"
            "2026-08-03 10:05:02 ERROR [payment-svc] Connection to razorpay.com refused\n"
            "2026-08-03 10:05:03 ERROR [payment-svc] POST /api/v1/charge - 504 Gateway Timeout\n"
            "2026-08-03 10:05:05 WARN  [payment-svc] Circuit breaker OPEN for razorpay-client\n"
            "2026-08-03 10:05:08 ERROR [payment-svc] Fallback: returning cached error response\n"
        ),
        metrics={"cpu": "15%", "memory": "42%", "error_rate": "95%", "latency": "30 sec", "requests": "12,000/min"},
        monitor_status="DOWN",
        monitor_details="Health endpoint /health returning 503. Payment gateway unreachable.",
        recent_commits=[
            "Commit a1b2c3d by Alice: Updated payment gateway integration config (2 hours ago)",
            "Commit e4f5g6h by Bob: Refactored connection pool settings for Razorpay (3 hours ago)",
        ],
        knowledge_context=[
            {
                "incident_number": "INC-142",
                "title": "Payment API Gateway Timeout",
                "resolution": "Rollback to previous deployment (v1.12.4). Misconfigured connection pool.",
                "similarity": 0.92,
            }
        ],
    ),
    # 2. Database Overload
    Scenario(
        title="Database Connection Pool Exhaustion",
        description="PostgreSQL primary database at 100% CPU. Application queries timing out across all services.",
        service="Database",
        severity="P1",
        affected_users=25000,
        tags=["database", "postgresql", "cpu", "critical"],
        logs=(
            "2026-08-03 14:22:01 ERROR [db-proxy] FATAL: remaining connection slots are reserved\n"
            "2026-08-03 14:22:02 ERROR [api-svc] Cannot acquire connection from pool (timeout 5000ms)\n"
            "2026-08-03 14:22:03 ERROR [api-svc] org.postgresql.util.PSQLException: Connection refused\n"
            "2026-08-03 14:22:05 WARN  [db-proxy] Active connections: 500/500\n"
            "2026-08-03 14:22:08 ERROR [order-svc] SELECT query timeout after 60s on orders table\n"
        ),
        metrics={"cpu": "100%", "memory": "88%", "error_rate": "78%", "latency": "60 sec", "requests": "200/min"},
        monitor_status="DEGRADED",
        monitor_details="Database CPU at 100%. Connection pool fully saturated at 500/500.",
        recent_commits=[
            "Commit x9y8z7w by Carol: Added new analytics query to dashboard endpoint (45 min ago)",
            "Commit m3n4o5p by Dave: Removed query result caching for real-time accuracy (1 hour ago)",
        ],
        knowledge_context=[
            {
                "incident_number": "INC-089",
                "title": "Database connection exhaustion in Order Service",
                "resolution": "Increased max_connections from 100 to 500 and restarted.",
                "similarity": 0.88,
            }
        ],
    ),
    # 3. Memory Leak
    Scenario(
        title="Memory Leak in Catalog Service",
        description="Catalog API pods being killed by OOM Killer. Memory usage climbing to 99% within minutes of restart.",
        service="Catalog API",
        severity="P1",
        affected_users=8500,
        tags=["memory", "oom", "catalog", "critical"],
        logs=(
            "2026-08-03 09:15:01 ERROR [catalog-svc] java.lang.OutOfMemoryError: Java heap space\n"
            "2026-08-03 09:15:02 ERROR [catalog-svc] Killed by Linux OOM Killer (pid 4521)\n"
            "2026-08-03 09:15:03 INFO  [k8s] Pod catalog-svc-7d4f9b restarted (CrashLoopBackOff)\n"
            "2026-08-03 09:17:01 WARN  [catalog-svc] Heap usage: 3.8GB / 4.0GB after 2 minutes\n"
            "2026-08-03 09:19:02 ERROR [catalog-svc] java.lang.OutOfMemoryError: Java heap space\n"
        ),
        metrics={"cpu": "45%", "memory": "99%", "error_rate": "100%", "latency": "N/A", "requests": "0/min"},
        monitor_status="DOWN",
        monitor_details="Pod in CrashLoopBackOff. 4 restarts in last 10 minutes.",
        recent_commits=[
            "Commit q1w2e3r by Eve: Added in-memory product image cache (30 min ago)",
            "Commit t4y5u6i by Frank: Increased product catalog batch size to 10000 (1 hour ago)",
        ],
        knowledge_context=[
            {
                "incident_number": "INC-201",
                "title": "OOM crash in Inventory Service",
                "resolution": "Identified unbounded cache growth. Added TTL eviction policy.",
                "similarity": 0.85,
            }
        ],
    ),
    # 4. Redis Cache Failure
    Scenario(
        title="Redis Cluster Failure",
        description="Redis sentinel lost quorum. Session store and rate limiter both unavailable.",
        service="Cache Layer",
        severity="P1",
        affected_users=30000,
        tags=["redis", "cache", "session", "critical"],
        logs=(
            "2026-08-03 16:00:01 ERROR [redis-sentinel] Lost quorum - cannot failover\n"
            "2026-08-03 16:00:02 ERROR [auth-svc] Failed to validate session: RedisConnectionError\n"
            "2026-08-03 16:00:03 ERROR [api-gateway] Rate limiter unavailable, falling back to permissive mode\n"
            "2026-08-03 16:00:05 WARN  [auth-svc] All login sessions invalidated\n"
            "2026-08-03 16:00:10 ERROR [cart-svc] Cannot retrieve cart data from Redis\n"
        ),
        metrics={"cpu": "5%", "memory": "12%", "error_rate": "65%", "latency": "200 ms", "requests": "45,000/min"},
        monitor_status="DOWN",
        monitor_details="Redis sentinel lost quorum. Primary node unreachable.",
        recent_commits=[
            "Commit a7s8d9f by Grace: Updated Redis sentinel configuration (20 min ago)",
            "Commit g1h2j3k by Hank: Migrated session store from Redis 6 to Redis 7 (1 hour ago)",
        ],
        knowledge_context=[],
    ),
    # 5. Kubernetes Pod Crash
    Scenario(
        title="Kubernetes Pod CrashLoopBackOff",
        description="Auth service pods crashing immediately on startup. Users cannot log in.",
        service="Auth Service",
        severity="P1",
        affected_users=50000,
        tags=["kubernetes", "crashloop", "auth", "critical"],
        logs=(
            "2026-08-03 11:30:01 ERROR [auth-svc] FileNotFoundError: /etc/secrets/jwt-signing-key not found\n"
            "2026-08-03 11:30:01 ERROR [auth-svc] Fatal: Cannot start without JWT signing key\n"
            "2026-08-03 11:30:02 INFO  [k8s] Container exited with code 1\n"
            "2026-08-03 11:30:05 INFO  [k8s] Back-off restarting failed container (attempt 5)\n"
            "2026-08-03 11:30:10 WARN  [k8s] Pod auth-svc-8b2a1c: CrashLoopBackOff\n"
        ),
        metrics={"cpu": "2%", "memory": "8%", "error_rate": "100%", "latency": "N/A", "requests": "0/min"},
        monitor_status="DOWN",
        monitor_details="Auth service pods in CrashLoopBackOff. 12 restarts in 5 minutes.",
        recent_commits=[
            "Commit z1x2c3v by Ivan: Migrated secrets from env vars to Kubernetes Secrets volume (15 min ago)",
            "Commit b4n5m6l by Jane: Updated deployment.yaml with new volume mounts (20 min ago)",
        ],
        knowledge_context=[
            {
                "incident_number": "INC-178",
                "title": "Config service crash after secrets migration",
                "resolution": "Fixed volume mount path in deployment.yaml. Secret was mounted at wrong path.",
                "similarity": 0.94,
            }
        ],
    ),
    # 6. API Rate Limit Exceeded
    Scenario(
        title="Third-Party API Rate Limit Exceeded",
        description="Stripe API returning 429 Too Many Requests. All checkout flows failing.",
        service="Checkout API",
        severity="P2",
        affected_users=3200,
        tags=["api", "rate-limit", "stripe", "checkout"],
        logs=(
            "2026-08-03 13:45:01 WARN  [checkout-svc] Stripe API returned 429 Too Many Requests\n"
            "2026-08-03 13:45:02 ERROR [checkout-svc] Rate limit exceeded: 1000/1000 requests per minute\n"
            "2026-08-03 13:45:03 WARN  [checkout-svc] Retry-After: 60 seconds\n"
            "2026-08-03 13:45:10 ERROR [checkout-svc] POST /checkout/complete failed: upstream rate limited\n"
            "2026-08-03 13:45:15 WARN  [checkout-svc] 847 requests queued in retry buffer\n"
        ),
        metrics={"cpu": "22%", "memory": "35%", "error_rate": "45%", "latency": "8 sec", "requests": "1,200/min"},
        monitor_status="DEGRADED",
        monitor_details="Checkout success rate dropped to 55%. Stripe API rate limited.",
        recent_commits=[
            "Commit p8o7i6u by Kevin: Removed request batching for real-time payment confirmation (40 min ago)",
            "Commit y5t4r3e by Lisa: Added retry loop for failed Stripe calls (1 hour ago)",
        ],
        knowledge_context=[],
    ),
    # 7. Disk Full
    Scenario(
        title="Disk Space Exhaustion on Log Volume",
        description="Application log volume at 100%. Services cannot write logs and are crashing.",
        service="Infrastructure",
        severity="P2",
        affected_users=0,
        tags=["disk", "storage", "logs", "infrastructure"],
        logs=(
            "2026-08-03 08:00:01 ERROR [logstash] No space left on device: /var/log/app\n"
            "2026-08-03 08:00:02 ERROR [api-svc] IOError: [Errno 28] No space left on device\n"
            "2026-08-03 08:00:03 WARN  [api-svc] Log rotation failed: target directory full\n"
            "2026-08-03 08:00:05 ERROR [k8s] Container api-svc failed liveness probe (write error)\n"
            "2026-08-03 08:00:10 INFO  [k8s] Evicting pods from node worker-3 (disk pressure)\n"
        ),
        metrics={"cpu": "30%", "memory": "55%", "error_rate": "40%", "latency": "500 ms", "requests": "5,000/min"},
        monitor_status="DEGRADED",
        monitor_details="Node worker-3 under disk pressure. /var/log at 100% capacity.",
        recent_commits=[
            "Commit w1e2r3t by Mark: Enabled verbose debug logging for payment investigation (2 hours ago)",
            "Commit y4u5i6o by Nancy: Disabled log rotation temporarily for audit (3 hours ago)",
        ],
        knowledge_context=[
            {
                "incident_number": "INC-156",
                "title": "Log volume disk full on worker-2",
                "resolution": "Cleaned up old logs and re-enabled log rotation with 7-day retention.",
                "similarity": 0.91,
            }
        ],
    ),
    # 8. SSL Certificate Expired
    Scenario(
        title="Expired SSL Certificate on API Gateway",
        description="TLS certificate expired on api.example.com. All HTTPS connections failing.",
        service="API Gateway",
        severity="P1",
        affected_users=100000,
        tags=["ssl", "tls", "certificate", "gateway", "critical"],
        logs=(
            "2026-08-03 00:00:01 ERROR [nginx] SSL_do_handshake() failed (SSL: error:14094415:SSL routines:ssl3_read_bytes:certificate expired)\n"
            "2026-08-03 00:00:02 ERROR [nginx] client SSL certificate verify error: (10:certificate has expired)\n"
            "2026-08-03 00:00:03 WARN  [cert-manager] Certificate api.example.com expired at 2026-08-02T23:59:59Z\n"
            "2026-08-03 00:00:05 ERROR [nginx] 48,291 TLS handshake failures in last 5 minutes\n"
            "2026-08-03 00:00:10 WARN  [cert-manager] Auto-renewal failed: DNS challenge timed out\n"
        ),
        metrics={"cpu": "8%", "memory": "15%", "error_rate": "100%", "latency": "N/A", "requests": "0/min"},
        monitor_status="DOWN",
        monitor_details="HTTPS endpoint returning TLS handshake failures. Certificate expired.",
        recent_commits=[
            "Commit c5v6b7n by Omar: Updated cert-manager ClusterIssuer config (3 days ago)",
            "Commit m8l9k0j by Priya: Changed DNS provider in cert-manager from Route53 to Cloudflare (5 days ago)",
        ],
        knowledge_context=[],
    ),
    # 9. DNS Resolution Failure
    Scenario(
        title="Internal DNS Resolution Failure",
        description="CoreDNS pods restarting. Internal service-to-service communication broken.",
        service="Networking",
        severity="P1",
        affected_users=75000,
        tags=["dns", "coredns", "networking", "critical"],
        logs=(
            "2026-08-03 15:10:01 ERROR [coredns] SERVFAIL for payment-svc.default.svc.cluster.local\n"
            "2026-08-03 15:10:02 ERROR [api-svc] Could not resolve hostname: database-primary.default.svc\n"
            "2026-08-03 15:10:03 ERROR [order-svc] DNS lookup failed: NXDOMAIN\n"
            "2026-08-03 15:10:05 WARN  [k8s] CoreDNS pod restarted (OOMKilled) - 3rd time in 10 min\n"
            "2026-08-03 15:10:08 ERROR [coredns] memory usage exceeded limit: 170Mi / 170Mi\n"
        ),
        metrics={"cpu": "10%", "memory": "25%", "error_rate": "82%", "latency": "45 sec", "requests": "1,500/min"},
        monitor_status="DOWN",
        monitor_details="Internal DNS resolution failing across cluster. CoreDNS pods OOMKilled.",
        recent_commits=[
            "Commit f2g3h4j by Quinn: Reduced CoreDNS memory limit from 512Mi to 170Mi (1 hour ago)",
            "Commit k5l6m7n by Raj: Added 200 new service entries to cluster (2 hours ago)",
        ],
        knowledge_context=[
            {
                "incident_number": "INC-112",
                "title": "CoreDNS memory limit too low after cluster expansion",
                "resolution": "Increased CoreDNS memory limit to 1Gi and added HPA for auto-scaling.",
                "similarity": 0.90,
            }
        ],
    ),
    # 10. Wrong Environment Variable
    Scenario(
        title="Production Using Staging Database Credentials",
        description="Production API connecting to staging database after deployment. Customer data queries returning empty.",
        service="User Service",
        severity="P1",
        affected_users=40000,
        tags=["config", "environment", "database", "critical"],
        logs=(
            "2026-08-03 12:00:01 INFO  [user-svc] Connected to database: staging-db.internal:5432/users_staging\n"
            "2026-08-03 12:00:02 WARN  [user-svc] Query returned 0 results for GET /api/users (expected >100k)\n"
            "2026-08-03 12:00:05 ERROR [user-svc] User lookup failed: user_id=12345 not found\n"
            "2026-08-03 12:00:08 ERROR [checkout-svc] Cannot validate user address: user service returned 404\n"
            "2026-08-03 12:00:10 WARN  [user-svc] Database: staging-db.internal (THIS IS NOT PRODUCTION)\n"
        ),
        metrics={"cpu": "5%", "memory": "20%", "error_rate": "60%", "latency": "50 ms", "requests": "8,000/min"},
        monitor_status="DEGRADED",
        monitor_details="User service healthy but returning unexpected empty results.",
        recent_commits=[
            "Commit s1d2f3g by Sara: Updated deployment pipeline to use new secrets manager (25 min ago)",
            "Commit h4j5k6l by Tom: Refactored environment variable loading in config.py (30 min ago)",
        ],
        knowledge_context=[
            {
                "incident_number": "INC-067",
                "title": "Staging credentials deployed to production",
                "resolution": "Rolled back deployment and added environment validation check on startup.",
                "similarity": 0.97,
            }
        ],
    ),
]


def get_random_scenario() -> Scenario:
    """Return a randomly selected incident scenario."""
    return random.choice(SCENARIOS)


def get_scenario_by_index(index: int) -> Scenario:
    """Return a specific scenario by its index (0-based)."""
    return SCENARIOS[index % len(SCENARIOS)]
