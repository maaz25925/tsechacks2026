"""
Hackathon-friendly entrypoint.

Preferred dev command (uses uv):
  uv run uvicorn app.main:app --reload --port 8000
"""

from app.main import app  # noqa: F401

