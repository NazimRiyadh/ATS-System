# LightRAG Mix Mode Implementation Guide

## Overview

This guide explains how to use the newly implemented mix mode feature for the LightRAG ATS system, including storage cleanup and retrieval mode options.

## What Changed

### 1. Storage Cleanup Script

- **File**: `clean_rag_storage.py`
- **Purpose**: Clean all LightRAG storage (PostgreSQL, Neo4j, local JSON files) to enable fresh schema creation
- **Usage**: Run before re-ingesting data to fix schema issues

### 2. Mix Mode Support

- **Files**: `main.py`, `src/job_manager.py`
- **Features**:
  - Support for all LightRAG retrieval modes: `naive`, `local`, `global`, `hybrid`, `mix`
  - Automatic fallback from mix mode to naive mode if errors occur
  - Detailed logging for debugging

### 3. Mode Validation Script

- **File**: `validate_modes.py`
- **Purpose**: Test all retrieval modes to verify functionality

## Step-by-Step Usage

### Step 1: Clean Existing Storage (Optional but Recommended)

If you're experiencing schema issues or want a fresh start:

```powershell
python clean_rag_storage.py
```

**What it does:**

- Drops all PostgreSQL tables
- Clears Neo4j graph database
- Removes local JSON files in `rag_storage/`

**Warning:** This deletes all indexed data! Make sure you have resume files backed up.

### Step 2: Re-ingest Resume Data

After cleaning storage, re-ingest all resumes:

```powershell
python batch_ingest.py --dir ./resumes --batch 10
```

**What it does:**

- Processes resumes in batches of 10
- Creates proper schema in PostgreSQL and Neo4j
- Generates embeddings and knowledge graph

**Expected time:** 2-5 seconds per resume

### Step 3: Validate Modes (Optional)

Test which modes are working:

```powershell
python validate_modes.py
```

**What it does:**

- Tests all 5 retrieval modes
- Shows which modes succeed/fail
- Provides troubleshooting guidance

### Step 4: Start the API

```powershell
python main.py
```

API will be available at `http://localhost:8000`

### Step 5: Use Mix Mode in Chat

#### Example with cURL:

```bash
# Using mix mode (default)
curl -X POST http://localhost:8000/chat_job \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JOB_001",
    "message": "Who has Python experience?",
    "mode": "mix"
  }'

# Using naive mode (fallback)
curl -X POST http://localhost:8000/chat_job \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JOB_001",
    "message": "Who has Python experience?",
    "mode": "naive"
  }'
```

#### Example with Python:

```python
import requests

url = "http://localhost:8000/chat_job"
payload = {
    "job_id": "JOB_001",
    "message": "Who has the best AWS experience?",
    "mode": "mix"  # Options: naive, local, global, hybrid, mix
}

response = requests.post(url, json=payload)
print(response.json()["response"])
```

## Retrieval Mode Comparison

| Mode     | Description        | Speed      | Reliability | Use Case                           |
| -------- | ------------------ | ---------- | ----------- | ---------------------------------- |
| `naive`  | Vector search only | ⚡ Fast    | ✅ High     | Production default, simple queries |
| `local`  | Local KG search    | 🐢 Slow    | ⚠️ Medium   | Entity-specific queries            |
| `global` | Global KG search   | 🐢 Slow    | ⚠️ Medium   | Broad relationship queries         |
| `hybrid` | Local + Global KG  | 🐌 Slowest | ⚠️ Low      | Complex multi-hop reasoning        |
| `mix`    | KG + Vector        | 🐢 Slow    | ✅ High\*   | Comprehensive search               |

\*Mix mode has high reliability due to automatic fallback to naive mode

## Automatic Fallback Behavior

The system implements intelligent fallback:

```
User requests mode → Try requested mode → Success? → Return results
                                       ↓ Failure
                                    Try naive mode → Success? → Return results
                                                    ↓ Failure
                                                Return error message
```

**Example logs:**

```
🔍 Querying with mode='mix' (2500 chars context)...
⚠️  Mode 'mix' failed: 'NoneType' object is not subscriptable
🔄 Falling back to mode='naive'...
✅ Fallback to naive mode succeeded
```

## Troubleshooting

### Issue: Mix mode fails even after cleanup

**Solution 1:** Use naive mode explicitly

```json
{ "mode": "naive" }
```

**Solution 2:** Check if data was ingested properly

```powershell
python validate_modes.py
```

### Issue: No candidates found

**Possible causes:**

1. Storage not initialized - Run cleanup and re-ingest
2. Query too specific - Broaden search terms
3. Vector embeddings mismatch - Ensure consistent embedding model

### Issue: Clean script fails on PostgreSQL

**Cause:** Wrong credentials in `.env`

**Solution:** Update `.env` with correct credentials:

```
POSTGRES_URI=postgresql+asyncpg://postgres:YOUR_PASSWORD@127.0.0.1:5432/postgres
```

## Performance Tips

1. **For production**: Use `mode="naive"` for fastest, most reliable results
2. **For exploration**: Use `mode="mix"` to leverage both graph and vector search
3. **For debugging**: Run `validate_modes.py` after any storage changes

## Next Steps

1. ✅ Storage cleanup implemented
2. ✅ Mix mode with fallback implemented
3. ✅ API documentation updated
4. ⏳ Test with real resume data
5. ⏳ Monitor mode usage in production

## Files Modified

- ✅ `clean_rag_storage.py` - Storage cleanup script (NEW)
- ✅ `validate_modes.py` - Mode validation script (NEW)
- ✅ `main.py` - Added mode parameter to `/chat_job`
- ✅ `src/job_manager.py` - Implemented mode support with fallback
- ✅ `API_DOCUMENTATION.md` - Documented mode parameter

## Support

If you encounter issues:

1. Check logs for error details
2. Run `validate_modes.py` to diagnose
3. Try fallback to `mode="naive"`
4. Re-run storage cleanup if needed
