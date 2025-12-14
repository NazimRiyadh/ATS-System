# LightRAG Bug Report (LOCALLY FIXED)

**NOTE: These bugs have been fixed locally in venv312. Report to upstream for permanent fix.**

## Bug Title

DocProcessingStatus.**init**() fails with unexpected keyword argument 'track_id' and async storage initialization race conditions

## Version

- lightrag-hku: 1.3.6 and 1.4.9.8
- Python: 3.12 and 3.14

## Description

Multiple issues when performing document insertion with `ainsert()`:

### Issue 1: track_id kwarg error (FIXED)

**File:** `lightrag/kg/json_doc_status_impl.py` line 93

**Problem:**

```python
result[k] = DocProcessingStatus(**data)
```

This unpacks all JSON fields including extra ones like `track_id` that don't exist in the `DocProcessingStatus` dataclass.

**Solution:**
Filter to only known fields before instantiation:

```python
known_fields = {
    "content", "content_summary", "content_length", "file_path",
    "status", "created_at", "updated_at", "chunks_count", "error", "metadata"
}
filtered_data = {k: v for k, v in data.items() if k in known_fields}
result[k] = DocProcessingStatus(**filtered_data)
```

### Issue 2: NoneType async context manager

**Error:** `'NoneType' object does not support the asynchronous context manager protocol`

**Root Cause:** `self._storage_lock` is None when accessed in `async with self._storage_lock` before `initialize()` completes.

### Issue 3: 'history_messages' KeyError

**Error:** `'history_messages'` key missing from pipeline_status dict

**Root Cause:** Pipeline status dictionary not properly initialized with all required keys before access in operate.py.

## Steps to Reproduce

```python
import asyncio
from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
import numpy as np

async def embed(texts):
    if isinstance(texts, str):
        texts = [texts]
    return np.random.rand(len(texts), 1024).astype(np.float32)

async def llm(prompt, **kwargs):
    return 'Test response'

async def main():
    rag = LightRAG(
        working_dir='./test_rag',
        llm_model_func=llm,
        embedding_func=EmbeddingFunc(embedding_dim=1024, max_token_size=8192, func=embed),
    )
    # Insert multiple documents in sequence triggers the race condition
    await rag.ainsert('Document 1 content')
    await rag.ainsert('Document 2 content')
    await rag.ainsert('Document 3 content')

asyncio.run(main())
```

## Environment

- OS: Windows 11
- Python: 3.12.10, 3.14
- lightrag-hku: 1.3.6, 1.4.9.8

## Suggested Fix

1. Filter unknown fields in `json_doc_status_impl.py` (see Solution above)
2. Initialize `_storage_lock` with a default asyncio.Lock() in **post_init**
3. Initialize pipeline_status with all required keys including 'history_messages' before use
