import type { ActivityEvent, Agent, Incident } from "@/lib/types";

const sharedTimeline = [
  {
    time: "08:42 UTC",
    title: "Anomaly detected",
    description: "Monitor Agent detected a 6.8× jump in checkout API latency.",
    kind: "detection" as const,
  },
  {
    time: "08:45 UTC",
    title: "Incident declared",
    description: "Severity raised automatically after error budget burn exceeded the critical threshold.",
    kind: "update" as const,
  },
  {
    time: "08:49 UTC",
    title: "Log correlation completed",
    description: "Log Agent connected elevated 502s to the payments database connection pool.",
    kind: "ai" as const,
  },
  {
    time: "08:54 UTC",
    title: "Mitigation proposed",
    description: "Recommendation Agent prepared a safe rollback with projected recovery in 7 minutes.",
    kind: "action" as const,
  },
];

const sharedLogs = [
  {
    time: "08:41:58.911",
    level: "WARN" as const,
    source: "payment-api",
    message: "Connection pool utilization reached 94% (94 / 100 connections).",
  },
  {
    time: "08:42:11.332",
    level: "ERROR" as const,
    source: "payment-api",
    message: "POST /v2/charges returned 502 after 30,000ms upstream timeout.",
  },
  {
    time: "08:44:23.705",
    level: "ERROR" as const,
    source: "payments-db",
    message: "remaining connection slots are reserved for superuser connections",
  },
  {
    time: "08:47:09.114",
    level: "INFO" as const,
    source: "deployments",
    message: "Correlated deployment payments-api@2025.07.24-rc.8 with incident window.",
  },
];

export const incidents: Incident[] = [
  {
    id: "INC-4821",
    title: "Checkout API elevated error rate",
    severity: "critical",
    service: "Payments API",
    status: "mitigating",
    assignee: "Maya Chen",
    createdAt: "Today, 08:42",
    updatedAt: "2 min ago",
    description: "Customers are intermittently unable to complete checkout as payment charge requests time out.",
    impact: "Checkout conversion is degraded across web and mobile.",
    affectedUsers: "18.4% of active checkouts",
    duration: "37 min",
    tags: ["customer-impacting", "database", "release"],
    timeline: sharedTimeline,
    logs: sharedLogs,
    analysis: {
      confidence: 92,
      summary: "A connection-pool exhaustion pattern started three minutes after the payments-api release. Error shape and timing match a known pool cleanup regression.",
      signals: ["502 rate increased 14.2×", "DB pool saturation at 94%", "Regression aligned with rc.8 rollout"],
      rootCause: "The rc.8 release retained idle transaction connections during retry backoff, exhausting the payments database pool under peak checkout traffic.",
      recommendation: {
        action: "Roll back payments-api from rc.8 to rc.7 and temporarily raise the pool ceiling to 130.",
        rationale: "The rollback removes the regression while the temporary ceiling drains in-flight retries. The change has been replayed successfully in the staging traffic shadow.",
        risk: "Low",
        estimatedRecovery: "7–10 min",
      },
    },
    auditHistory: [
      { time: "08:54", actor: "Recommendation Agent", action: "Prepared remediation", detail: "Rollback plan generated with low-risk assessment." },
      { time: "08:49", actor: "Log Agent", action: "Attached evidence", detail: "4 correlated log clusters and deployment metadata added." },
      { time: "08:45", actor: "Monitor Agent", action: "Escalated severity", detail: "Error budget burn rate crossed critical policy." },
    ],
  },
  {
    id: "INC-4820",
    title: "Delayed order confirmation emails",
    severity: "high",
    service: "Notifications",
    status: "investigating",
    assignee: "Arun Patel",
    createdAt: "Today, 08:15",
    updatedAt: "6 min ago",
    description: "Order confirmation messages are accumulating in the transactional email queue.",
    impact: "Customers receive confirmation later than expected; order processing is unaffected.",
    affectedUsers: "6,208 queued messages",
    duration: "64 min",
    tags: ["queue", "email"],
    timeline: sharedTimeline.map((event, index) => ({ ...event, time: ["08:15 UTC", "08:21 UTC", "08:29 UTC", "08:37 UTC"][index] })),
    logs: sharedLogs,
    analysis: {
      confidence: 78,
      summary: "Queue consumer throughput dropped after a provider throttle response. Backlog is growing but retry volume is stable.",
      signals: ["Provider 429 responses", "Consumer throughput down 61%", "No message loss detected"],
      rootCause: "The email provider quota bucket was exhausted following a campaign retry burst.",
      recommendation: { action: "Shift 35% of transactional traffic to the secondary provider.", rationale: "This preserves message ordering while bringing the queue below its SLA threshold.", risk: "Low", estimatedRecovery: "15 min" },
    },
    auditHistory: [{ time: "08:37", actor: "Recommendation Agent", action: "Prepared traffic shift", detail: "Secondary provider capacity verified." }],
  },
  {
    id: "INC-4819",
    title: "Search indexing backlog growing",
    severity: "medium",
    service: "Search Platform",
    status: "monitoring",
    assignee: "Noah Williams",
    createdAt: "Today, 07:48",
    updatedAt: "12 min ago",
    description: "Product updates are taking longer than the index freshness target to appear in search.",
    impact: "New catalog changes may not appear in search for up to 22 minutes.",
    affectedUsers: "Catalog team and discovery users",
    duration: "1h 31m",
    tags: ["indexing", "capacity"],
    timeline: sharedTimeline,
    logs: sharedLogs,
    analysis: {
      confidence: 85,
      summary: "A noisy reindex job consumed worker capacity. Autoscaling has now restored healthy processing lag.",
      signals: ["Worker queue depth peaked at 42k", "One tenant triggered full reindex", "Lag now declining"],
      rootCause: "A malformed catalog update initiated an unnecessary full tenant reindex.",
      recommendation: { action: "Allow autoscaling to drain the queue and add a reindex guardrail.", rationale: "Capacity has recovered; stopping workers would extend the backlog.", risk: "Low", estimatedRecovery: "20 min" },
    },
    auditHistory: [{ time: "08:03", actor: "Maya Chen", action: "Enabled burst workers", detail: "Added 12 indexing workers for queue recovery." }],
  },
  {
    id: "INC-4818",
    title: "Mobile session refresh failures",
    severity: "high",
    service: "Identity",
    status: "investigating",
    assignee: "Lena Ortiz",
    createdAt: "Today, 07:32",
    updatedAt: "18 min ago",
    description: "A subset of mobile users must reauthenticate unexpectedly when refreshing expired sessions.",
    impact: "Mobile session continuity is affected in the latest app version.",
    affectedUsers: "3.1% of mobile sessions",
    duration: "1h 47m",
    tags: ["mobile", "auth"],
    timeline: sharedTimeline,
    logs: sharedLogs,
    analysis: {
      confidence: 69,
      summary: "Token audience validation errors correlate with Android 7.14 traffic, but a second contributing factor remains possible.",
      signals: ["JWT audience mismatch", "Android 7.14 cohort only", "No web impact"],
      rootCause: "Likely mismatch in the new Android token audience claim.",
      recommendation: { action: "Disable silent refresh for Android 7.14 through the feature flag.", rationale: "Limits impact while the client fix is prepared.", risk: "Medium", estimatedRecovery: "5 min" },
    },
    auditHistory: [{ time: "07:51", actor: "Root Cause Agent", action: "Linked app version", detail: "First seen in Android 7.14 cohort." }],
  },
  {
    id: "INC-4817",
    title: "Warehouse sync job retrying",
    severity: "low",
    service: "Fulfillment",
    status: "resolved",
    assignee: "Ethan Brooks",
    createdAt: "Today, 06:55",
    updatedAt: "42 min ago",
    description: "A downstream warehouse endpoint briefly rejected batch payloads.",
    impact: "Fulfillment status updates were delayed, with no data loss.",
    affectedUsers: "1,040 shipment updates",
    duration: "38 min",
    tags: ["warehouse", "sync"],
    timeline: sharedTimeline,
    logs: sharedLogs,
    analysis: {
      confidence: 96,
      summary: "Partner endpoint returned invalid schema errors after a version deployment and recovered after rollback.",
      signals: ["Schema validation errors", "Partner deployment event", "Queue fully drained"],
      rootCause: "Partner warehouse API deployed an incompatible schema.",
      recommendation: { action: "Close incident and add schema contract test.", rationale: "Partner rollback restored stable delivery and all retries cleared.", risk: "Low", estimatedRecovery: "Complete" },
    },
    auditHistory: [{ time: "07:33", actor: "Ethan Brooks", action: "Resolved incident", detail: "Confirmed replayed deliveries and queue drain." }],
  },
  {
    id: "INC-4816",
    title: "Analytics export timeout spike",
    severity: "medium",
    service: "Data Platform",
    status: "monitoring",
    assignee: "Maya Chen",
    createdAt: "Today, 06:21",
    updatedAt: "1h ago",
    description: "Large analytics exports intermittently timed out during a warehouse compaction task.",
    impact: "A small segment of customers cannot download larger reports immediately.",
    affectedUsers: "0.8% of export jobs",
    duration: "2h 16m",
    tags: ["analytics", "latency"],
    timeline: sharedTimeline,
    logs: sharedLogs,
    analysis: {
      confidence: 88,
      summary: "Compute contention from a warehouse compaction task caused export worker timeouts. Contention has eased.",
      signals: ["Warehouse CPU at 97%", "Timeouts matched compaction window", "Error rate normalizing"],
      rootCause: "Scheduled compaction overlapped with peak export workload.",
      recommendation: { action: "Move compaction to the low-traffic window.", rationale: "Scheduling avoids resource contention without reducing export capacity.", risk: "Low", estimatedRecovery: "Complete" },
    },
    auditHistory: [{ time: "07:18", actor: "Data Platform", action: "Rescheduled compaction", detail: "Next run moved to 02:00 UTC." }],
  },
];

export const dashboardMetrics = [
  { label: "Active", value: "12", change: "+2 since yesterday", trend: "up", tone: "cyan" },
  { label: "Critical", value: "3", change: "1 needs attention", trend: "up", tone: "rose" },
  { label: "Resolved today", value: "18", change: "+20% from baseline", trend: "down", tone: "emerald" },
  { label: "Avg. resolution", value: "24m", change: "6m faster this week", trend: "down", tone: "violet" },
] as const;

export const agents: Agent[] = [
  { name: "Monitor Agent", state: "Running", description: "Watching telemetry, SLOs, and anomaly thresholds across 42 services.", metric: "42 services observed", updated: "Updated just now", color: "cyan" },
  { name: "Log Agent", state: "Completed", description: "Correlated logs, deploys, and traces for the active payment incident.", metric: "4 evidence clusters", updated: "Completed 2m ago", color: "emerald" },
  { name: "Root Cause Agent", state: "Thinking", description: "Testing causal hypotheses against release and infrastructure changes.", metric: "3 hypotheses ranked", updated: "Reasoning now", color: "amber" },
  { name: "Recommendation Agent", state: "Completed", description: "Prepared a staged rollback and recovery plan with safety checks.", metric: "1 action awaiting review", updated: "Completed 3m ago", color: "violet" },
];

export const activityEvents: ActivityEvent[] = [
  { time: "09:17", agent: "Monitor Agent", message: "Observed payment API error rate fall below the critical threshold.", tone: "success" },
  { time: "09:12", agent: "Recommendation Agent", message: "Created a reversible rollback plan for INC-4821.", tone: "info" },
  { time: "09:06", agent: "Root Cause Agent", message: "Raised confidence in the connection-pool regression hypothesis to 92%.", tone: "warning" },
  { time: "08:49", agent: "Log Agent", message: "Attached correlated deployment and database evidence to INC-4821.", tone: "info" },
  { time: "08:45", agent: "Monitor Agent", message: "Escalated INC-4821 to critical based on error budget burn.", tone: "warning" },
];

export const weeklyIncidents = [8, 11, 7, 14, 10, 6, 9];
export const weeklyLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
export const severityBreakdown = [
  { name: "Critical", value: 12, color: "#fb7185" },
  { name: "High", value: 24, color: "#fbbf24" },
  { name: "Medium", value: 38, color: "#38bdf8" },
  { name: "Low", value: 26, color: "#818cf8" },
];
export const mttrSeries = [39, 34, 31, 29, 27, 25, 24];
export const resolutionRate = 94.8;

export function getIncident(id: string): Incident | undefined {
  return incidents.find((incident) => incident.id.toLowerCase() === id.toLowerCase());
}
