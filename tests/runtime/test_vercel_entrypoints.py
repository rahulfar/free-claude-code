"""Test that Vercel entrypoint modules properly initialize and export the FastAPI app."""

import importlib
import sys
from pathlib import Path


def test_index_entrypoint_exports_app(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("FCC_CONFIG_DIR", str(tmp_path / ".fcc"))
    monkeypatch.setenv("LOG_FILE", str(tmp_path / ".fcc" / "logs" / "server.log"))

    root_dir = Path(__file__).resolve().parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    import index

    assert hasattr(index, "app")
    assert index.app is not None


def test_app_aliases_export_app():
    import app
    import asgi
    import main

    assert hasattr(app, "app")
    assert hasattr(main, "app")
    assert hasattr(asgi, "app")
