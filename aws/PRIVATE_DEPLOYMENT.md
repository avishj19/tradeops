## Embedded agent workflow (AWS API contract)

TradeOps embeds AWS in the agent path so specialist firms already on AWS adopt the product without rewriting orchestration:

1. Agents analyze logs locally (deterministic; no LLM).
2. Every run stages **raw + Parquet + report** onto the **S3** key layout (`raw/{run_id}/…`, `optimized/{run_id}/…`).
3. An **EventBridge**-shaped “TradeOps Run Completed” event is emitted.
4. An **Athena** query handle is opened from the Query agent SQL; **Glue** remains the transform worker for Object Created events.

**Local default:** without credentials, the same contract is written under `TRADEOPS_DATA/aws-mirror/` (isomorphic keys/events).  
**Live AWS:** set `TRADEOPS_AWS_LIVE=1` plus `TRADEOPS_AWS_RAW_BUCKET`, `TRADEOPS_AWS_OPTIMIZED_BUCKET`, `TRADEOPS_AWS_GLUE_JOB` (optional `TRADEOPS_AWS_ATHENA_WORKGROUP`, `TRADEOPS_AWS_EVENT_BUS`, `AWS_REGION`). The agent code path does not change—only the boto3 backend does.

Inspect status via `GET /api/aws/status`. Plan Object Created events via `POST /api/aws/events`. Archive/lifecycle mutations remain disabled until durable approvals exist.

---


## Two data paths

- Analytics: application log batches → S3 raw prefix → event-driven transform → S3 Parquet → Athena.
- Incidents: existing CloudWatch Agent/application logging → CloudWatch subscription filter → Lambda normalization and grouped signals → optional Bedrock explanation → optional SNS notification.

Keep original evidence on the analytics path: filtering the incident path loses context and must not replace raw retention. CloudWatch ingestion is still charged for data ingested before subscription filtering. A subscription does not make ingestion free. Neither continuous subscriptions, Bedrock nor SNS delivery is enabled by the local demo.

## Private connectivity

For a worker requiring strict customer-VPC egress isolation, place it in private subnets with no public IP and no default internet route. Use an S3 gateway endpoint for same-region bulk objects. Add interface endpoints only for APIs actually called by the worker, such as SNS or Bedrock Runtime; also inventory calls to CloudWatch Logs, Glue, STS and other APIs. Enable private DNS and restrict endpoint security-group ingress to the worker's HTTPS traffic. Maintain prefix-scoped IAM and endpoint policies.

No NAT gateway is proposed for this isolated worker. Dependencies must be packaged before deployment. A public subnet alone does not give a VPC-connected Lambda internet access. AWS-managed service invocation paths and the worker's outbound API connections are different; validate each hop rather than assuming all traffic traverses your VPC.

S3 gateway endpoints carry no additional endpoint charge; interface endpoints have per-AZ hourly and data-processing charges. Calculator defaults (editable assumptions): two endpoint services × two AZs × 730 hours × $0.01 = $29.20/month, plus 10 GB × $0.01 = $0.10. A $20 service allowance yields $49.30. This is not an all-in AWS quotation. VPN/private dashboard access, CloudWatch, Lambda, SNS, S3, Athena, KMS, transfer and any model usage need separate workload estimates. The service allowance is user-entered, not measured. One AZ lowers fixed cost but sacrifices availability.

## Security and cost policy

Use S3 Block Public Access, encryption, TLS-only bucket access, least-privilege identities and separate raw/optimized prefixes. Protect raw logs using retention and access policies specific to the firm; these presets do not establish regulatory compliance. Avoid blanket endpoint-only bucket denies that inadvertently block AWS service delivery; validate service-principal exceptions with the chosen delivery architecture.

Send only aggregate incident counts or a protected incident reference in notifications. Do not send raw lines, account identifiers or credentials to SNS or an LLM. The local inbox uses an allowlist of fixed fields rather than trying to regex-redact arbitrary messages. Raw and Parquet files still contain the supplied data and require filesystem/cloud access controls; the demo does not encrypt its local files.

Before enabling notifications, add durable event-id deduplication, incident grouping windows, cooldowns, bounded retries and a dead-letter queue. Local grouping covers only a single run and is not cross-run deduplication. Before enabling Bedrock, add model-specific pricing, input/output token limits and a durable budget gate. AWS budget notifications alone are not spending caps. Keep destructive actions behind authenticated approvals.

## Niche focus

- Boutique trading firms: retain execution evidence, prioritize gateway latency and errors, review all archival.
- Specialist fintech SaaS: isolate each customer’s log access and storage namespace; the current demo is single-workspace only.
- Specialist brokers: limit access to order/account evidence; define retention and approver responsibilities before production.

These are suggested operating priorities, not different compliance certifications.

## Article-to-product mapping

[Splunk log monitoring](https://www.splunk.com/en_us/blog/learn/log-monitoring.html) informs standardized signals, privacy-preserving summaries and private-cloud deployment planning. The demo does not implement Splunk's adaptive online learning or claim threat prevention.

[Divyam Sharma's AWS incident pipeline](https://medium.com/@divyam.sharma3/how-i-built-an-ai-driven-log-analysis-and-incident-alerting-system-on-aws-7cea7ec29e5d) informs the CloudWatch subscription → Lambda → optional Bedrock → SNS design. Local aggregate grouping addresses repeated alert noise; no external notification is sent. Human review remains essential.

Primary AWS references for implementation:
- [S3 gateway endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-s3.html)
- [PrivateLink pricing](https://aws.amazon.com/privatelink/pricing/)
- [Lambda VPC internet access](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc-internet.html)

No network resources, endpoints, subscriptions or paid services were created by this update.
