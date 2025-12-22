# Fixing PostgreSQL Port Conflict

## Problem

You have TWO PostgreSQL instances running on port 5432:

1. Local PostgreSQL 16 (without pgvector extension)
2. Docker PostgreSQL with pgvector (ats-db container)

Python is connecting to the local instance, which is why ingestion fails with "type vector does not exist".

## Solution Options

### Option 1: Stop Local PostgreSQL (Recommended)

**Step 1:** Open PowerShell as Administrator

**Step 2:** Stop the local PostgreSQL service:

```powershell
Stop-Service postgresql-x64-16
```

**Step 3:** Verify Docker PostgreSQL is accessible:

```powershell
docker exec ats-db psql -U postgres -c "SELECT version();"
```

**Step 4:** Retry ingestion:

```powershell
cd "d:\KT Informatik\ATS project\Fine_tuned_approach"
python batch_ingest.py --dir ./resumes --batch 10
```

### Option 2: Change Docker Port

If you need to keep both PostgreSQL instances running:

**Step 1:** Stop and remove current Docker container:

```powershell
docker stop ats-db
docker rm ats-db
```

**Step 2:** Start Docker PostgreSQL on different port (e.g., 5433):

```powershell
docker run -d --name ats-db -p 5433:5432 -e POSTGRES_PASSWORD=password pgvector/pgvector:pg16
```

**Step 3:** Update `.env` file:

```
POSTGRES_URI=postgresql+asyncpg://postgres:password@127.0.0.1:5433/postgres
```

**Step 4:** Retry ingestion

## Verification

After fixing, test the connection:

```powershell
python check_pg_tables.py
```

Should see no errors about missing vector extension.

## Current Status

- ✅ Docker PostgreSQL with pgvector: RUNNING
- ❌ Port conflict: Both on 5432
- ❌ Python connecting to: Local PostgreSQL (wrong one)
- ⏳ Waiting for: Port conflict resolution

## Which Option?

**Recommendation**: Option 1 (stop local PostgreSQL) is simpler if you only need pgvector for this project.
