# 🔐 Security Guide - HackTheAgent

## Critical Security Fixes Applied

This document outlines the security improvements made to prevent credential leaks and unauthorized access.

### 1. **Environment Variables - All Credentials Now Use `.env`**

**Before:** Hardcoded API keys and instance IDs scattered throughout files
```python
# ❌ INSECURE
WATSON_ORCHESTRATE_BASE_URL = "https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4/v1"
self.instance_id = "0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4"
```

**After:** All credentials loaded from environment
```python
# ✅ SECURE
self.api_key = os.getenv("WATSON_ORCHESTRATE_API_KEY")
self.instance_id = os.getenv("WATSON_INSTANCE_ID", "")
self.base_url = os.getenv("WATSON_ORCHESTRATE_BASE_URL", "...")
```

### 2. **Files Modified for Security**

| File | Changes |
|------|---------|
| `import_agents_via_api.py` | ✅ URLs and API endpoints now use environment variables |
| `watson_orchestrate.py` | ✅ Instance ID and region moved to environment |
| `check_api_key.py` | ✅ Removed hardcoded example API keys |
| `find_correct_endpoint.py` | ✅ Removed hardcoded instance ID |
| `orchestrate_workflow_setup.py` | ✅ IAM URL and API endpoints now configurable |
| `fix_401_error.py` | ✅ Regex-based cleanup to remove any hardcoded keys |
| `analytics_tracker.py` | ✅ All metrics and defaults now use environment variables |
| `.gitignore` | ✅ Expanded to prevent accidental credential commits |

### 3. **How to Use `.env` File**

#### Step 1: Copy the example file
```bash
cp .env.example .env
```

#### Step 2: Fill in your credentials
```bash
# Get credentials from IBM Cloud Dashboard
WATSON_ORCHESTRATE_API_KEY=your-actual-api-key
WATSON_ORCHESTRATE_BASE_URL=https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/your-instance-id
WATSON_INSTANCE_ID=your-instance-id
WATSON_REGION=us-south

# Gmail OAuth
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret
```

#### Step 3: Verify `.env` is in `.gitignore`
```bash
# The .env file should NEVER be committed
git status .env  # Should show as ignored
```

### 4. **Getting Your Credentials**

#### IBM Watson Orchestrate
1. Go to [IBM Cloud Console](https://cloud.ibm.com/)
2. Navigate to **Watson Orchestrate**
3. Select your instance
4. Go to **Access Management → API Keys**
5. Create or copy your API key
6. Find your **Instance ID** from the instance details
7. Note your **Region** (us-south, jp-tok, eu-gb, etc.)

#### Gmail OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Gmail API**
4. Create **OAuth 2.0 Desktop Credentials**
5. Download the JSON file
6. Extract `client_id` and `client_secret`

### 5. **Security Best Practices**

✅ **DO:**
- Store all secrets in `.env` file
- Use `os.getenv()` to load credentials
- Rotate API keys regularly
- Use different keys for dev/staging/production
- Keep `.env` in `.gitignore`
- Add sensitive file patterns to `.gitignore`
- Use environment variables in CI/CD pipelines

❌ **DON'T:**
- Commit `.env` files to version control
- Hardcode API keys in source code
- Share API keys in emails or Slack
- Use the same key across environments
- Print full credentials in logs
- Store passwords in plain text
- Commit credential files (JSON, PEM, etc.)

### 6. **Detecting Leaked Credentials**

If you accidentally commit credentials:

1. **Remove from git history:**
```bash
# Option 1: Use BFG Repo-Cleaner (faster)
bfg --delete-files .env

# Option 2: Use git filter-branch
git filter-branch --index-filter 'git rm --cached --ignore-unmatch .env' HEAD
```

2. **Rotate compromised credentials immediately:**
   - Go to IBM Cloud Console
   - Regenerate API keys
   - Update `.env` file
   - Redeploy application

### 7. **Credential Scope Best Practice**

Each credential should have minimal required permissions:

```
WATSON_ORCHESTRATE_API_KEY
  ├─ Required: Orchestrate service access
  ├─ Region: Specific to your instance region
  └─ Not required: Other IBM services

GMAIL_CLIENT_SECRET
  ├─ Required: Gmail API read/modify access
  ├─ Redirect URI: Exactly http://localhost:3000/oauth/callback
  └─ Scope: Only email.readonly + email.modify

WATSON_INSTANCE_ID
  ├─ Sensitive: Identifies your resource
  ├─ Can be inferred from base URL
  └─ Store in environment to prevent hardcoding
```

### 8. **Environment-Specific Configurations**

Create separate `.env` files for different environments:

```bash
# Development
.env.local              # Your machine (git-ignored)
.env                    # Shared template

# Staging/Production
.env.staging            # Staging secrets (not in repo)
.env.production         # Production secrets (not in repo)
```

In CI/CD, inject secrets via pipeline secrets:
```yaml
# GitHub Actions example
env:
  WATSON_ORCHESTRATE_API_KEY: ${{ secrets.WATSON_ORCHESTRATE_API_KEY }}
  GMAIL_CLIENT_SECRET: ${{ secrets.GMAIL_CLIENT_SECRET }}
```

### 9. **Scanning for Exposed Credentials**

Run these tools to find any remaining exposed credentials:

```bash
# Using grep
grep -r "apikey\|api_key\|secret\|password" src/ --include="*.py" \
  | grep -v ".env" | grep -v "__pycache__"

# Using truffleHog (detects credential patterns)
pip install truffleHog
truffleHog filesystem . --json

# Using git hooks
pip install detect-secrets
detect-secrets scan --baseline .secrets.baseline
```

### 10. **Verification Checklist**

- [ ] `.env` file created and never committed
- [ ] All hardcoded API keys removed
- [ ] Instance IDs moved to environment variables
- [ ] OAuth secrets in `.env`
- [ ] `.gitignore` updated with sensitive patterns
- [ ] No credentials in example/demo files
- [ ] No credentials in documentation (except placeholders)
- [ ] CI/CD pipelines use secrets management
- [ ] API keys rotated if ever exposed
- [ ] Team members briefed on credential handling

---

**Questions?** Refer to the sections above or contact the security team.

For more information:
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12-Factor App - Config](https://12factor.net/config)
- [IBM Cloud Security Best Practices](https://cloud.ibm.com/docs/security-compliance?topic=security-compliance-best-practices)
