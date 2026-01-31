# 🧪 Complete Swagger Testing Guide - HackTheAgent Email Brain

## Prerequisites
1. Backend server running at: http://localhost:8000
2. Open Swagger UI: http://localhost:8000/docs

---

## 📋 Step-by-Step Testing Workflow

### **Step 1: Health Check** ✅
**Purpose**: Verify the server is running

1. In Swagger UI, find the **GET /health** endpoint
2. Click on it to expand
3. Click **"Try it out"**
4. Click **"Execute"**

**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "HackTheAgent Email Brain",
  "version": "1.0.0"
}
```

---

### **Step 2: Load Emails** 📧
**Purpose**: Load the sample email dataset (25 emails)

1. Find the **GET /tool/emails/load** endpoint
2. Click **"Try it out"**
3. Click **"Execute"**

**Expected Response (200 OK):**
```json
{
  "emails": [
    {
      "id": "email_001",
      "from": "devday@ibm.com",
      "to": "developer@company.com",
      "subject": "IBM Dev Day Hackathon 2026 - Registration Confirmed",
      "date": "2026-01-15",
      "body": "Dear Developer,\n\nYour registration for IBM Dev Day..."
    },
    // ... 24 more emails
  ]
}
```

**What to verify:**
- ✅ Response contains 25 emails
- ✅ Each email has: id, from, to, subject, date, body
- ✅ Status code is 200

---

### **Step 3: Normalize Emails** 🔄
**Purpose**: Convert raw emails into structured messages for indexing

1. Find the **POST /tool/emails/normalize** endpoint
2. Click **"Try it out"**
3. **COPY the entire response from Step 2** (all 25 emails)
4. Paste it into the Request body
5. Click **"Execute"**

**Request Body Example:**
```json
{
  "emails": [
    {
      "id": "email_001",
      "from": "devday@ibm.com",
      "to": "developer@company.com",
      "subject": "IBM Dev Day Hackathon 2026 - Registration Confirmed",
      "date": "2026-01-15",
      "body": "Dear Developer,\n\nYour registration for IBM Dev Day..."
    }
    // ... paste all 25 emails here
  ]
}
```

**Expected Response (200 OK):**
```json
{
  "messages": [
    {
      "id": "email_001",
      "text": "From: devday@ibm.com\nTo: developer@company.com\nSubject: IBM Dev Day Hackathon 2026 - Registration Confirmed\nDate: 2026-01-15\n\nDear Developer,\n\nYour registration for IBM Dev Day...",
      "metadata": {
        "from": "devday@ibm.com",
        "to": "developer@company.com",
        "subject": "IBM Dev Day Hackathon 2026 - Registration Confirmed",
        "date": "2026-01-15"
      }
    }
    // ... 24 more normalized messages
  ]
}
```

**What to verify:**
- ✅ Response contains 25 normalized messages
- ✅ Each message has structured text and metadata
- ✅ Status code is 200

---

### **Step 4: Index Messages** 🗂️
**Purpose**: Create embeddings and store in vector database

1. Find the **POST /tool/semantic/index** endpoint
2. Click **"Try it out"**
3. **COPY the entire response from Step 3** (all normalized messages)
4. Paste it into the Request body
5. Click **"Execute"**

**Request Body Example:**
```json
{
  "messages": [
    {
      "id": "email_001",
      "text": "From: devday@ibm.com\nTo: developer@company.com...",
      "metadata": {
        "from": "devday@ibm.com",
        "to": "developer@company.com",
        "subject": "IBM Dev Day Hackathon 2026 - Registration Confirmed",
        "date": "2026-01-15"
      }
    }
    // ... paste all 25 normalized messages here
  ]
}
```

**Expected Response (200 OK):**
```json
{
  "status": "indexed",
  "chunks_indexed": 127,
  "stats": {
    "messages_indexed": 25,
    "chunks_created": 127,
    "avg_chunks_per_message": 5.08
  }
}
```

**What to verify:**
- ✅ Status is "indexed"
- ✅ chunks_indexed > 100 (depends on email length)
- ✅ All 25 messages were indexed
- ✅ Status code is 200

---

### **Step 5: Test Semantic Search** 🔍
**Purpose**: Find relevant emails using natural language queries

#### Test Query 1: Find Urgent Deadlines

1. Find the **POST /tool/semantic/search** endpoint
2. Click **"Try it out"**
3. Enter this request body:

```json
{
  "query": "urgent deadlines",
  "top_k": 5
}
```

4. Click **"Execute"**

**Expected Response (200 OK):**
```json
{
  "results": [
    {
      "id": "email_004",
      "subject": "URGENT: Production deployment scheduled for tonight",
      "date": "2026-01-22",
      "score": 0.8234,
      "snippet": "Team,\n\nWe have an urgent production deployment scheduled for tonight at 11 PM EST.\n\nDeployment checklist:\n1. Database migration scripts ready..."
    },
    {
      "id": "email_002",
      "subject": "You were assigned to issue #234: Fix authentication bug",
      "date": "2026-01-20",
      "score": 0.7891,
      "snippet": "You have been assigned to issue #234 in repository company/backend-api.\n\nIssue: Fix authentication bug\nPriority: High\nDeadline: January 25, 2026..."
    }
    // ... more results
  ]
}
```

**What to verify:**
- ✅ Results are ranked by relevance (score)
- ✅ Scores are between 0 and 1
- ✅ Results contain urgent/deadline-related emails
- ✅ Snippets show relevant content

---

#### Test Query 2: Find Hackathon Information

**Request Body:**
```json
{
  "query": "IBM Dev Day hackathon requirements",
  "top_k": 3
}
```

**Expected Response:**
```json
{
  "results": [
    {
      "id": "email_001",
      "subject": "IBM Dev Day Hackathon 2026 - Registration Confirmed",
      "date": "2026-01-15",
      "score": 0.9123,
      "snippet": "Dear Developer,\n\nYour registration for IBM Dev Day Hackathon 2026 is confirmed! The event will take place on February 15-16, 2026.\n\nKey Requirements:\n- Build an AI-powered application using watsonx..."
    }
    // ... more results
  ]
}
```

---

#### Test Query 3: Find Security Issues

**Request Body:**
```json
{
  "query": "security vulnerabilities",
  "top_k": 5
}
```

**Expected Response:**
```json
{
  "results": [
    {
      "id": "email_006",
      "subject": "Security Alert: Vulnerability detected in dependencies",
      "date": "2026-01-21",
      "score": 0.8756,
      "snippet": "SECURITY ALERT\n\nOur automated security scan has detected critical vulnerabilities in your project dependencies:\n\n1. lodash@4.17.15 - Prototype Pollution..."
    }
    // ... more results
  ]
}
```

---

#### Test Query 4: Find Payment Information

**Request Body:**
```json
{
  "query": "invoice payment due",
  "top_k": 3
}
```

**Expected Response:**
```json
{
  "results": [
    {
      "id": "email_003",
      "subject": "Invoice #INV-2026-0045 - Payment Due",
      "date": "2026-01-18",
      "score": 0.8912,
      "snippet": "Dear Customer,\n\nThis is a reminder that Invoice #INV-2026-0045 is due for payment.\n\nInvoice Details:\n- Amount: $2,450.00\n- Due Date: January 31, 2026..."
    }
    // ... more results
  ]
}
```

---

### **Step 6: Test RAG Answer** 🤖
**Purpose**: Get AI-generated answers with citations

#### Test Question 1: Hackathon Details

1. Find the **POST /tool/rag/answer** endpoint
2. Click **"Try it out"**
3. Enter this request body:

```json
{
  "question": "What are the requirements for the IBM Dev Day hackathon?",
  "top_k": 5
}
```

4. Click **"Execute"**

**Expected Response (200 OK):**
```json
{
  "answer": "Based on the retrieved emails, the IBM Dev Day Hackathon 2026 has the following requirements:\n\n1. Build an AI-powered application using watsonx\n2. Submit your project by February 16, 11:59 PM EST\n3. Demo presentation: 5 minutes maximum\n4. Team size: 1-4 members\n\nThe event takes place on February 15-16, 2026. Prizes include $10,000 for 1st place, $5,000 for 2nd place, and $2,500 for 3rd place.\n\n(Source: Email from devday@ibm.com dated 2026-01-15)",
  "citations": [
    {
      "id": "email_001",
      "subject": "IBM Dev Day Hackathon 2026 - Registration Confirmed",
      "date": "2026-01-15",
      "snippet": "Dear Developer,\n\nYour registration for IBM Dev Day Hackathon 2026 is confirmed! The event will take place on February 15-16, 2026.\n\nKey Requirements:\n- Build an AI-powered application using watsonx..."
    }
  ]
}
```

**What to verify:**
- ✅ Answer is grounded in email content
- ✅ Citations are provided
- ✅ Answer references specific emails
- ✅ No hallucination (all info from emails)

---

#### Test Question 2: Security Vulnerabilities

**Request Body:**
```json
{
  "question": "What security vulnerabilities were found and how should I fix them?",
  "top_k": 5
}
```

**Expected Response:**
```json
{
  "answer": "Based on Email #6 from security@company.com (2026-01-21), two critical vulnerabilities were detected:\n\n1. lodash@4.17.15 - Prototype Pollution (CVE-2020-8203)\n   - Severity: HIGH\n   - Fix: Upgrade to lodash@4.17.21\n\n2. axios@0.21.0 - SSRF vulnerability (CVE-2021-3749)\n   - Severity: MEDIUM\n   - Fix: Upgrade to axios@0.21.4\n\nAction Required: Update these dependencies within 48 hours.",
  "citations": [
    {
      "id": "email_006",
      "subject": "Security Alert: Vulnerability detected in dependencies",
      "date": "2026-01-21",
      "snippet": "SECURITY ALERT\n\nOur automated security scan has detected critical vulnerabilities..."
    }
  ]
}
```

---

#### Test Question 3: Payment Information

**Request Body:**
```json
{
  "question": "What invoices need to be paid and when are they due?",
  "top_k": 5
}
```

**Expected Response:**
```json
{
  "answer": "Based on Email #3 from finance@vendor.com (2026-01-18), Invoice #INV-2026-0045 needs to be paid:\n\n- Amount: $2,450.00\n- Due Date: January 31, 2026\n- Services: Cloud Infrastructure (December 2025)\n\nPayment methods available: Wire transfer, Credit card, or ACH.\n\nPlease process payment to avoid service interruption.",
  "citations": [
    {
      "id": "email_003",
      "subject": "Invoice #INV-2026-0045 - Payment Due",
      "date": "2026-01-18",
      "snippet": "Dear Customer,\n\nThis is a reminder that Invoice #INV-2026-0045 is due for payment..."
    }
  ]
}
```

---

#### Test Question 4: Urgent Tasks

**Request Body:**
```json
{
  "question": "What urgent tasks do I have and what are the deadlines?",
  "top_k": 5
}
```

**Expected Response:**
```json
{
  "answer": "Based on the retrieved emails, you have several urgent tasks:\n\n1. Production Deployment (Email #4, 2026-01-22)\n   - Scheduled: Tonight at 11 PM EST\n   - Expected downtime: 30 minutes\n   - Requires: Database migration scripts, rollback plan, monitoring alerts\n\n2. Authentication Bug Fix (Email #2, 2026-01-20)\n   - Issue: #234 in company/backend-api\n   - Priority: High\n   - Deadline: January 25, 2026\n   - Problem: OAuth2 token refresh failing after 1 hour\n\n3. Security Vulnerabilities (Email #6, 2026-01-21)\n   - Action Required: Update dependencies within 48 hours\n   - Critical: lodash and axios vulnerabilities",
  "citations": [
    {
      "id": "email_004",
      "subject": "URGENT: Production deployment scheduled for tonight",
      "date": "2026-01-22",
      "snippet": "Team,\n\nWe have an urgent production deployment scheduled..."
    },
    {
      "id": "email_002",
      "subject": "You were assigned to issue #234: Fix authentication bug",
      "date": "2026-01-20",
      "snippet": "You have been assigned to issue #234..."
    },
    {
      "id": "email_006",
      "subject": "Security Alert: Vulnerability detected in dependencies",
      "date": "2026-01-21",
      "snippet": "SECURITY ALERT\n\nOur automated security scan..."
    }
  ]
}
```

---

### **Step 7: Check System Statistics** 📊
**Purpose**: View indexing and system stats

1. Find the **GET /stats** endpoint
2. Click **"Try it out"**
3. Click **"Execute"**

**Expected Response (200 OK):**
```json
{
  "total_chunks": 127,
  "collection_name": "email_embeddings",
  "embedding_model": "all-MiniLM-L6-v2",
  "vector_db": "chroma",
  "llm_provider": "watsonx",
  "llm_available": false
}
```

**What to verify:**
- ✅ total_chunks matches Step 4 result
- ✅ Shows embedding model being used
- ✅ Shows LLM availability status

---

## 🎯 Success Criteria

After completing all steps, you should see:

✅ **Step 1**: Server is healthy
✅ **Step 2**: 25 emails loaded successfully
✅ **Step 3**: 25 messages normalized
✅ **Step 4**: ~127 chunks indexed
✅ **Step 5**: Semantic search returns relevant results with scores
✅ **Step 6**: RAG provides answers with citations
✅ **Step 7**: System stats show correct configuration

---

## 🔍 Additional Test Queries

Try these queries to explore the system:

**Semantic Search Queries:**
```json
{"query": "meetings and interviews", "top_k": 5}
{"query": "GitHub issues and bugs", "top_k": 5}
{"query": "training and learning opportunities", "top_k": 5}
{"query": "cost and budget information", "top_k": 5}
```

**RAG Questions:**
```json
{"question": "When is the interview scheduled and who is the candidate?", "top_k": 5}
{"question": "What GitHub issues am I assigned to?", "top_k": 5}
{"question": "What are the hackathon prizes?", "top_k": 5}
{"question": "What deployment is scheduled and when?", "top_k": 5}
```

---

## 🐛 Troubleshooting

**Issue**: No results returned
- **Solution**: Make sure you completed Steps 2-4 (load, normalize, index)

**Issue**: Low similarity scores
- **Solution**: This is normal - scores above 0.7 are good matches

**Issue**: RAG returns "LLM not configured" message
- **Solution**: This is expected without watsonx.ai credentials - system uses fallback mode

**Issue**: Server not responding
- **Solution**: Check if server is running at http://localhost:8000

---

## 📝 Notes

- **Semantic Search**: Works without LLM credentials
- **RAG Answers**: Requires watsonx.ai credentials for AI-generated answers
- **Fallback Mode**: Without LLM, RAG returns retrieved context
- **Scores**: Higher scores (closer to 1.0) mean better matches
- **Citations**: Always provided to prevent hallucination

---

**🎉 You've successfully tested the HackTheAgent Email Brain system!**