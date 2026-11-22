# RG AI — MongoDB Backup, Restore & Disaster Recovery Guide

This document defines the comprehensive backup, restore, retention, and disaster recovery procedures for the **RG AI** Indian Stock Market Intelligence Platform (`rg_ai` database).

---

## 1. Overview of Persistent Collections

The `rg_ai` database consists of 12 collections with strict indexing and relational integrity:

| Collection | Description | Criticality | Recommended Backup Frequency |
| :--- | :--- | :--- | :--- |
| `users` | User credentials (PBKDF2-HMAC-SHA256) & profiles | High | Hourly / Continuous |
| `conversations` | Chat conversation threads & status metadata | High | Hourly / Continuous |
| `messages` | Chat messages with validated JSON analysis & telemetry | High | Hourly / Continuous |
| `watchlists` | User-curated NSE/BSE stock watchlists | Medium | Daily |
| `saved_analyses` | Validated financial analysis reports & recommendations | High | Daily |
| `prompt_templates` | Versioned system prompt templates | Low (code-seeded) | Weekly |
| `user_preferences` | User theme, default exchange, chart settings | Medium | Daily |
| `learning_courses` | Structured educational course catalog | Low (code-seeded) | Weekly |
| `learning_progress` | User module completions and syllabus progress | Medium | Daily |
| `learning_bookmarks` | Bookmarked financial lessons and notes | Medium | Daily |
| `quiz_attempts` | Quiz evaluation attempts, scores, and timestamps | Medium | Daily |
| `audit_logs` | Security events, password updates, admin actions | High (compliance) | Hourly / Continuous |

---

## 2. On-Premises & Self-Hosted Backup Procedures

### 2.1 Complete Database Backup with `mongodump`

Run `mongodump` with compression, archive packaging, and timestamping:

```bash
# Set timestamp and backup target directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/mongodb"
mkdir -p "${BACKUP_DIR}"

# Execute compressed archive dump
mongodump \
  --uri="mongodb://localhost:27017" \
  --db="rg_ai" \
  --gzip \
  --archive="${BACKUP_DIR}/rg_ai_${TIMESTAMP}.gz"
```

### 2.2 Isolated Collection Backup

To export a specific high-value collection (e.g. `saved_analyses` or `users`):

```bash
mongodump \
  --uri="mongodb://localhost:27017" \
  --db="rg_ai" \
  --collection="saved_analyses" \
  --gzip \
  --archive="${BACKUP_DIR}/rg_ai_saved_analyses_${TIMESTAMP}.gz"
```

---

## 3. Restoration Procedures with `mongorestore`

### 3.1 Full Database Restore

To restore an entire database from a compressed archive (with `--drop` to clean up target collections first):

> [!CAUTION]
> The `--drop` flag will replace existing data in the destination collections before restoring. Always verify you are targeting the intended database environment.

```bash
mongorestore \
  --uri="mongodb://localhost:27017" \
  --db="rg_ai" \
  --gzip \
  --drop \
  --archive="/var/backups/mongodb/rg_ai_20261117_120000.gz"
```

### 3.2 Single Collection Restore

To restore only one collection without impacting the rest of the database:

```bash
mongorestore \
  --uri="mongodb://localhost:27017" \
  --db="rg_ai" \
  --collection="saved_analyses" \
  --gzip \
  --drop \
  --archive="/var/backups/mongodb/rg_ai_saved_analyses_20261117_120000.gz"
```

### 3.3 Dry-Run Restoration Verification

Verify the archive is valid without writing to the database:

```bash
mongorestore \
  --uri="mongodb://localhost:27017" \
  --gzip \
  --dryRun \
  --archive="/var/backups/mongodb/rg_ai_20261117_120000.gz"
```

---

## 4. Automated Backup Script & Crontab Setup

Save this script as `/usr/local/bin/backup_rg_ai_mongo.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_ROOT="/var/backups/mongodb"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="rg_ai_backup_${TIMESTAMP}.gz"

mkdir -p "${BACKUP_ROOT}"

# Perform dump
mongodump \
  --uri="${MONGODB_URI:-mongodb://localhost:27017}" \
  --db="rg_ai" \
  --gzip \
  --archive="${BACKUP_ROOT}/${FILENAME}"

echo "[$(date)] Successfully created MongoDB backup: ${FILENAME}"

# Prune backups older than RETENTION_DAYS
find "${BACKUP_ROOT}" -type f -name "rg_ai_backup_*.gz" -mtime +${RETENTION_DAYS} -delete
echo "[$(date)] Pruned backups older than ${RETENTION_DAYS} days."
```

Make executable:
```bash
chmod +x /usr/local/bin/backup_rg_ai_mongo.sh
```

Add to cron (`crontab -e`):
```cron
# Run daily backup at 02:00 AM IST
0 2 * * * /usr/local/bin/backup_rg_ai_mongo.sh >> /var/log/mongo_backup.log 2>&1

# Optional: Run hourly backup for chat conversations & messages
0 * * * * mongodump --uri="mongodb://localhost:27017" --db="rg_ai" --collection="messages" --gzip --archive="/var/backups/mongodb/hourly_messages_$(date +\%H).gz"
```

---

## 5. MongoDB Atlas Managed Backup Strategy

For production cloud deployments on **MongoDB Atlas**:

1. **Continuous Cloud Backups**:
   - Enable **Point-in-Time Recovery (PITR)**: Allows restoring the cluster to any second within the past 7 days.
   - Useful for immediate rollback in case of data corruption or application logic bugs.
2. **Snapshot Schedule**:
   - **Hourly Snapshots**: Retained for 24 hours.
   - **Daily Snapshots**: Retained for 30 days.
   - **Weekly Snapshots**: Retained for 12 weeks.
   - **Monthly Snapshots**: Retained for 12 months.
3. **Cross-Region Snapshot Distribution**:
   - For mission-critical Indian equities resilience, replicate daily snapshots to a secondary cloud region (e.g., AWS `ap-south-1` Mumbai to `ap-southeast-1` Singapore).

---

## 6. Disaster Recovery & Validation Testing

### Periodic Restore Drills
Execute quarterly restore drills into an isolated staging environment (`rg_ai_staging`):
1. Extract the latest automated production dump.
2. Restore into `rg_ai_staging`.
3. Run the automated test suite:
   ```bash
   MONGODB_DATABASE=rg_ai_staging pytest -v backend/tests/test_mongodb.py
   ```
4. Verify user counts, conversation counts, and message integrity checks.
5. Drop `rg_ai_staging` after validation.
