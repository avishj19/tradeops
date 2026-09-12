# AWS embedding

TradeOps stages every agent run onto an **S3 → EventBridge → Glue → Athena** contract.

- **Local default:** same key/event shapes under `$TRADEOPS_DATA/aws-mirror/` (no credentials).
- **Live:** `TRADEOPS_AWS_LIVE=1` plus `TRADEOPS_AWS_RAW_BUCKET`, `TRADEOPS_AWS_OPTIMIZED_BUCKET`, `TRADEOPS_AWS_GLUE_JOB` (optional workgroup / event bus / region). Agent code does not change — only the boto3 backend does.

`GET /api/aws/status` · `POST /api/aws/events` to plan Object Created handling.

Local archive approval never mutates S3 lifecycle or retention. For a private worker VPC, prefer an S3 gateway endpoint and add interface endpoints only for APIs you actually call; package dependencies before removing NAT.
