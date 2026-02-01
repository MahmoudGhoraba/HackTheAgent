#!/bin/bash

# ================================================================
# HackTheAgent Native Agent Importer using Watson Orchestrate ADK
# ================================================================
# This script imports all 6 agents using the official ADK CLI
# ================================================================

set -e  # Exit on error

PROJECT_ROOT="/Users/ghorabas/Hackathon/HackTheAgent"
AGENTS_DIR="$PROJECT_ROOT/backend/agents"

echo ""
echo "=========================================="
echo "🚀 HackTheAgent Native Agent Importer"
echo "=========================================="
echo ""

# Check if ADK is installed
if ! command -v orchestrate &> /dev/null; then
    echo "❌ ADK CLI not installed"
    echo ""
    echo "Install with:"
    echo "  npm install -g @ibm-generative-ai/watson-orchestrate-adk"
    echo ""
    exit 1
fi

echo "✓ ADK CLI found: $(orchestrate --version)"
echo ""

# Check if agent files exist
if [ ! -d "$AGENTS_DIR" ]; then
    echo "❌ Agents directory not found: $AGENTS_DIR"
    exit 1
fi

AGENT_COUNT=$(ls -1 "$AGENTS_DIR"/*.yaml 2>/dev/null | wc -l)
if [ $AGENT_COUNT -eq 0 ]; then
    echo "❌ No YAML files found in: $AGENTS_DIR"
    exit 1
fi

echo "📁 Found $AGENT_COUNT agent YAML files"
echo ""

# List agents
echo "📋 Agents to import:"
for agent_file in "$AGENTS_DIR"/*.yaml; do
    agent_name=$(basename "$agent_file" .yaml)
    echo "  ✓ $agent_name"
done
echo ""

# Ask for confirmation
read -p "Import all agents? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "📤 Importing Agents"
echo "=========================================="
echo ""

IMPORT_COUNT=0
IMPORT_SUCCESS=0
IMPORT_FAILED=0

# Import each agent
for agent_file in "$AGENTS_DIR"/*.yaml; do
    agent_name=$(basename "$agent_file" .yaml)
    IMPORT_COUNT=$((IMPORT_COUNT + 1))
    
    echo -n "[$IMPORT_COUNT/6] Importing $agent_name... "
    
    if orchestrate agents import -f "$agent_file" > /dev/null 2>&1; then
        echo "✅"
        IMPORT_SUCCESS=$((IMPORT_SUCCESS + 1))
    else
        echo "⚠️ (may already exist)"
        # Try to describe it to check if it's already there
        if orchestrate agents describe "$agent_name" > /dev/null 2>&1; then
            echo "       Agent already exists in Orchestrate"
            IMPORT_SUCCESS=$((IMPORT_SUCCESS + 1))
        else
            echo "       Error importing"
            IMPORT_FAILED=$((IMPORT_FAILED + 1))
        fi
    fi
done

echo ""
echo "=========================================="
echo "✅ Import Summary"
echo "=========================================="
echo "  Total: $IMPORT_COUNT"
echo "  Success: $IMPORT_SUCCESS"
echo "  Failed: $IMPORT_FAILED"
echo ""

# List imported agents
echo "📋 Verifying Imports"
echo "=========================================="
echo ""

if orchestrate agents list > /dev/null 2>&1; then
    echo "Agents in Orchestrate:"
    orchestrate agents list | head -20
    echo ""
fi

# Offer to deploy
echo ""
read -p "Deploy agents now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "=========================================="
    echo "🚀 Deploying Agents"
    echo "=========================================="
    echo ""
    
    DEPLOY_COUNT=0
    
    for agent_file in "$AGENTS_DIR"/*.yaml; do
        agent_name=$(basename "$agent_file" .yaml)
        DEPLOY_COUNT=$((DEPLOY_COUNT + 1))
        
        echo -n "[$DEPLOY_COUNT/6] Deploying $agent_name... "
        if orchestrate agents deploy --name "$agent_name" > /dev/null 2>&1; then
            echo "✅"
        else
            echo "⚠️ (may already be deployed)"
        fi
    done
    
    echo ""
fi

# Next steps
echo "=========================================="
echo "✅ All Done!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "  1. Go to: https://orchestrate.cloud.ibm.com"
echo "  2. Click 'Manage Agents'"
echo "  3. See all 6 agents listed"
echo "  4. Create workflows using these agents"
echo ""
echo "View agent details:"
echo "  orchestrate agents describe <agent-name>"
echo ""
echo "List all agents:"
echo "  orchestrate agents list"
echo ""
