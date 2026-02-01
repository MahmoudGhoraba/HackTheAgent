# MCP Server Integration Guide

## Quick Start

```bash
cd d:\HackTheAgent\backend
python run_mcp.py
```

**Environment Variables:**
- `MCP_PORT`: Server port (default: 8001)

## Watson Orchestrate Setup

1. Go to **Add MCP Server**
2. Enter:
   - **URL**: `http://<your-server>:8001/sse`
   - **Transport**: Server-Sent Events (SSE)

## Available Tools (18)

### Gmail (5)
| Tool | Description |
|------|-------------|
| `check_gmail_auth` | Check Gmail authentication |
| `gmail_fetch_emails` | Fetch emails with query |
| `gmail_search` | Search with Gmail syntax |
| `gmail_get_labels` | Get all labels |
| `gmail_get_profile` | Get user profile |

### Outlook (5)
| Tool | Description |
|------|-------------|
| `check_outlook_auth` | Check Outlook authentication |
| `outlook_fetch_emails` | Fetch emails with query |
| `outlook_search` | Search Outlook emails |
| `outlook_get_folders` | Get mail folders |
| `outlook_get_profile` | Get user profile |

### Unified (1)
| Tool | Description |
|------|-------------|
| `get_all_providers_status` | Check all email providers |

### Search & RAG (2)
| Tool | Description |
|------|-------------|
| `search_emails_semantic` | Semantic search |
| `answer_question` | RAG Q&A with citations |

### Analysis (5)
| Tool | Description |
|------|-------------|
| `classify_loaded_emails` | Classify emails |
| `detect_email_threads` | Detect threads |
| `analyze_emails` | Email analytics |
| `get_vector_index_stats` | Index stats |
| `get_search_analytics` | Search stats |

## OAuth Setup

### Gmail
1. Complete OAuth via web frontend at `http://localhost:3000`

### Outlook
1. Configure `.env` with Azure credentials:
   ```
   OUTLOOK_CLIENT_ID=your-azure-app-id
   OUTLOOK_CLIENT_SECRET=your-azure-app-secret
   OUTLOOK_TENANT_ID=common
   ```
2. Register app at [Azure Portal](https://portal.azure.com)
3. Add permissions: `Mail.Read`, `User.Read`

## File Structure

```
backend/
├── app/
│   └── email_providers/
│       ├── base.py      # EmailProvider protocol
│       ├── gmail.py     # Gmail wrapper
│       └── outlook.py   # Outlook (Graph API)
├── mcp_server/
│   ├── __init__.py
│   └── server.py        # All 18 tools
└── run_mcp.py
```
