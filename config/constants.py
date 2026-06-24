# config/constants.py
"""Configuration — single source of truth.

All environment variables are loaded here. Never use os.getenv() directly
in application code — import from this module instead.

Usage:
    from config.constants import LOG_LEVEL, MCP_BASE_URL
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ── LLM Service ──────────────────────────────────────────────────────────────
# Configure your LLM endpoint (OpenAI-compatible API, Ollama, vLLM, etc.)
WORKER_LLM_URL = os.getenv("WORKER_LLM_URL", "http://localhost:8000/v1")
WORKER_MODEL_NAME = os.getenv("WORKER_MODEL_NAME", "your-model-name")

# ── External Service (MCP/API) ───────────────────────────────────────────────
# Base URL for external tool services
MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://localhost:8080")

# ── Security ─────────────────────────────────────────────────────────────────
# Security scanning mode: 'none' | 'lite' | 'full' | 'remote'
SECURITY_MODE = os.getenv("SECURITY_MODE", "lite")
SECURITY_SERVICE_URL = os.getenv("SECURITY_SERVICE_URL", "")

# Advanced security configuration (if using semantic analysis)
SECURITY_TIMEOUT = int(os.getenv("SECURITY_TIMEOUT", "30"))
SECURITY_THRESHOLD = float(os.getenv("SECURITY_THRESHOLD", "0.5"))
SECURITY_INPUT_THRESHOLD = float(os.getenv("SECURITY_INPUT_THRESHOLD", "0.6"))
sec_out_thresh = float(os.getenv("SECURITY_OUTPUT_THRESHOLD", "0.6"))
SECURITY_OUTPUT_THRESHOLD = sec_out_thresh

# Security bypass — categories to skip (empty = block all)
sec_bypass = os.getenv("SECURITY_BYPASS_CATEGORIES", "")
SECURITY_BYPASS_CATEGORIES = sec_bypass.strip()

# ── Observability ────────────────────────────────────────────────────────────
# Tracing & monitoring (Langfuse, LangSmith, etc.)
OBSERVABILITY_HOST = os.getenv("OBSERVABILITY_HOST", "http://localhost:3000")
OBSERVABILITY_PUBLIC_KEY = os.getenv("OBSERVABILITY_PUBLIC_KEY", "")
OBSERVABILITY_SECRET_KEY = os.getenv("OBSERVABILITY_SECRET_KEY", "")

# ── Application ──────────────────────────────────────────────────────────────
APP_TEMP_DIR = os.getenv("APP_TEMP_DIR", "./temp_data")
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
