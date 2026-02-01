#!/usr/bin/env python
"""
MCP Server Entry Point
Runs Email Brain MCP server with SSE transport.

Environment variables:
  MCP_PORT: Port to run on (default: 8001)
  MCP_HOST: Host to bind to (default: 0.0.0.0)
"""
import os
import sys
from pathlib import Path

# Ensure backend is in path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Set data directory
os.environ.setdefault("DATA_DIR", str(backend_dir / "app" / "data"))

from mcp_server.server import mcp

if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", 8001))
    
    print("=" * 50)
    print("Email Brain MCP Server")
    print("=" * 50)
    print(f"Transport: SSE | Port: {port}")
    print(f"URL: http://localhost:{port}/sse")
    print("=" * 50)
    
    mcp.run(transport="sse", port=port)
