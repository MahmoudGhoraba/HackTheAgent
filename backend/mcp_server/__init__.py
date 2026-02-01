"""
MCP Server Package for Email Brain
Exposes email intelligence tools to IBM Watson Orchestrate.

Path setup is handled here so other modules don't need to manage it.
"""
import sys
from pathlib import Path

# Configure path once for the entire package
_backend_path = Path(__file__).parent.parent
if str(_backend_path) not in sys.path:
    sys.path.insert(0, str(_backend_path))
