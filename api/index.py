"""Vercel /api Entrypoint for Free Claude Code."""

import os
import sys
from pathlib import Path

# Ensure src/ is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = _PROJECT_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# Serverless environment configuration defaults (e.g. Vercel / AWS Lambda)
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    os.environ.setdefault("FCC_CONFIG_DIR", "/tmp/.fcc")
    os.environ.setdefault("LOG_FILE", "/tmp/.fcc/logs/server.log")

from free_claude_code.config.loader import get_settings
from free_claude_code.runtime.bootstrap import build_asgi_app

settings = get_settings()
app = build_asgi_app(settings)
