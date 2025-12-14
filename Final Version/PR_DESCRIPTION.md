# Pull Request: Fix KeyError 'history_messages' in apipeline_process_enqueue_documents

## Description

This PR fixes a `KeyError: 'history_messages'` that occurs when calling `insert()` or `ainsert()` methods. The error happens because `pipeline_status["history_messages"]` is accessed without first checking if the key exists.

## Bug Details

**Error Message:**

```
KeyError: 'history_messages'
```

**Location:** `lightrag/lightrag.py` in `apipeline_process_enqueue_documents()`

**Root Cause:** The code attempts to clear the `history_messages` list using `del pipeline_status["history_messages"][:]` without first verifying that the key exists in the dictionary.

## The Fix

```python
# Before (buggy):
del pipeline_status["history_messages"][:]

# After (fixed):
if "history_messages" in pipeline_status:
    del pipeline_status["history_messages"][:]
else:
    pipeline_status["history_messages"] = []
```

## Testing

- Tested with Python 3.12
- Tested with `lightrag-hku==1.3.6`
- Successfully ingested multiple documents without the KeyError
- All existing functionality works as expected

## Related Issues

This addresses the `KeyError: 'history_messages'` bug reported by multiple users when using the `insert()` function.

## Checklist

- [x] The fix is backward compatible
- [x] No breaking changes to the API
- [x] Tested locally with document insertion
- [x] Minimal change - only adds a defensive check
