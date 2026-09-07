"""Vercel / ASGI entrypoint for Free Claude Code FastAPI proxy."""

import os
import sys
from pathlib import Path

# Add src/ to sys.path so free_claude_code can be imported when running from source
_root_dir = Path(__file__).resolve().parent
_src_dir = _root_dir / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

# Configure FCC directories to /tmp in serverless environments if not already set
if "FCC_CONFIG_DIR" not in os.environ and ("VERCEL" in os.environ or "AWS_LAMBDA_FUNCTION_NAME" in os.environ):
    os.environ["FCC_CONFIG_DIR"] = "/tmp/.fcc"

from fastapi import FastAPI
from free_claude_code.config.loader import get_settings
from free_claude_code.runtime.bootstrap import build_asgi_app

settings = get_settings()
app: FastAPI = build_asgi_app(settings)
