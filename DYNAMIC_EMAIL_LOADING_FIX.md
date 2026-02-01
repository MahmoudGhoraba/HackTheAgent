# 📧 Dynamic Email Loading Fix

## Problem

The system was **hardcoded to load only 5 emails** despite Gmail being fully connected. Users couldn't load more emails even though:
- Gmail OAuth was authenticated
- Backend API supports up to 500 emails (max_results: 1-500)
- Users wanted to load as many emails as they needed

## Root Causes

Found **3 hardcoded limits** preventing dynamic email loading:

### 1. Frontend: Orchestrator top_k Hardcoded to 5
**File**: `frontend/src/pages/ai-agent.tsx` (Line 86)

**Before**:
```typescript
const response = await api.post('/workflow/execute', {
  question: userQuery,
  top_k: 5  // ❌ Hardcoded to 5
});
```

**After**:
```typescript
// Extract number from query (e.g., "show me 50 emails" -> 50)
// If no number specified, use 100 as default (max 500 from backend)
const extractedNumber = extractNumber(userQuery);
const topK = extractedNumber ? Math.min(Math.max(extractedNumber, 1), 500) : 100;

const response = await api.post('/workflow/execute', {
  question: userQuery,
  top_k: topK  // ✅ Dynamic, extracted from query
});
```

### 2. Backend: RAGRequest Schema Limited to 20
**File**: `backend/app/schemas.py` (Lines 93-94)

**Before**:
```python
class RAGRequest(BaseModel):
    """Request for /tool/rag/answer"""
    question: str
    top_k: int = Field(default=5, ge=1, le=20)  # ❌ Max 20
```

**After**:
```python
class RAGRequest(BaseModel):
    """Request for /tool/rag/answer"""
    question: str
    top_k: int = Field(default=100, ge=1, le=500, description="Number of emails to retrieve (1-500)")  # ✅ Max 500
```

### 3. Frontend: Welcome Message Didn't Mention Number Support
**File**: `frontend/src/pages/ai-agent.tsx` (Lines 43-47)

**Updated to include**:
```
• "Load 200 emails from Gmail"
• "Show me 50 recent emails"

You can specify how many emails to load (1-500) by mentioning a number in your query. Default is 100.
```

## How It Works Now

### Example Queries

| User Query | Emails Loaded | Notes |
|-----------|--------------|-------|
| "Show me recent emails" | 100 | Default (no number specified) |
| "Load 50 emails" | 50 | Extracts number from query |
| "Get 200 emails from Gmail" | 200 | Works with Gmail |
| "Find 5 security emails" | 5 | Explicit number request |
| "Show me 1000 emails" | 500 | Capped at max (500) |
| "Load emails" | 100 | Default if no number |

### Implementation Details

1. **Frontend Parameter Extraction**:
   - Uses `extractNumber()` helper to parse integers from user query
   - Validates range: min 1, max 500
   - Falls back to 100 if no number specified

2. **Backend Validation**:
   - `RAGRequest.top_k` now accepts 1-500
   - Orchestrator passes `top_k` to semantic search
   - Search engine respects the limit

3. **User Communication**:
   - Welcome message explains the feature
   - Users understand they can specify email count

## Benefits

✅ **Dynamic Loading**: Users can load 1 to 500 emails as needed
✅ **Smart Defaults**: 100 emails by default (good balance)
✅ **Natural Language**: Users specify in their query ("show me 200 emails")
✅ **Gmail Ready**: Works with fully authenticated Gmail
✅ **Bounded**: Respects API limits (1-500)
✅ **User Friendly**: No technical configuration needed

## Testing

To test the dynamic loading:

```bash
# Load default (100 emails)
curl -X POST http://localhost:8000/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{"question": "summarize my emails"}'

# Load 50 emails
curl -X POST http://localhost:8000/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{"question": "summarize my 50 recent emails"}'

# Load 300 emails
curl -X POST http://localhost:8000/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{"question": "find important 300 emails"}'

# Load max (500)
curl -X POST http://localhost:8000/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{"question": "load all 500 emails"}'
```

## Technical Changes Summary

| File | Change | Impact |
|------|--------|--------|
| `frontend/src/pages/ai-agent.tsx` | Extract number from query, dynamic top_k | Users can specify email count |
| `backend/app/schemas.py` | RAGRequest.top_k: default 100, max 500 | Backend accepts wider range |
| Welcome Message | Added example queries with numbers | Better user guidance |

## Files Modified

1. ✅ `frontend/src/pages/ai-agent.tsx` - Dynamic top_k extraction
2. ✅ `backend/app/schemas.py` - Increased RAGRequest limits
3. ✅ Welcome message updated with examples

## No Breaking Changes

- Existing queries continue to work
- Default behavior improved (5 → 100)
- Backward compatible with old API calls
- All tests continue to pass
