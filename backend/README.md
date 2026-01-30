# HackTheAgent Backend

This is the **backend for HackTheAgent**, a multi-agent email aggregation and query system built for the IBM Watsonx AI Hackathon.

The backend **does not handle email APIs directly** — instead, it acts as a **bridge between your frontend and Watsonx Orchestrate agents**, calling Orchestrator workflows for Gmail, Outlook, ingestion, and query processing.

---

## Features

- Fetch emails from Gmail and Outlook via Orchestrator Agents
- Merge and normalize messages for uniform processing
- Query messages based on keywords or search parameters
- Expose endpoints for a **custom frontend**
- Fully decoupled — Orchestrator handles all OAuth and agent logic

---

## Backend Folder Structure

backend/
├── app/
│ ├── main.py # FastAPI app, exposes endpoints for frontend
│ ├── orchestrator.py # helper functions to call Orchestrator API
│ ├── config.py # store workflow IDs, API keys, base URLs
│ └── utils.py # optional helpers
├── requirements.txt # Python dependencies
└── README.md # this file




---

## Requirements

Still working on it


---

## Workflow Overview

Gmail Agent: List emails from Gmail account

Outlook Agent: List emails from Outlook account

Ingestion/Normalization Agent: Merge and clean messages

Query Agent: Search and summarize messages

The backend simply calls these Orchestrator agents — all AI reasoning and multi-agent orchestration happens in Watsonx Orchestrate.