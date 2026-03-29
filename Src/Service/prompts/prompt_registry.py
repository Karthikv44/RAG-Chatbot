"""
Prompt version registry.
Add new versions as new .txt files and update ACTIVE_VERSION to switch.
All versions are tracked in git for full history.
"""

import os

ACTIVE_VERSION = "v1"
_PROMPT_DIR = os.path.dirname(__file__) + "/prompts"


def load_prompt(version: str = ACTIVE_VERSION) -> str:
    path = os.path.join(_PROMPT_DIR, f"rag_prompt_{version}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt version '{version}' not found at {path}")
    with open(path) as f:
        return f.read()


def get_active_prompt() -> str:
    return load_prompt(ACTIVE_VERSION)


def list_versions() -> list[str]:
    return [
        f.replace("rag_prompt_", "").replace(".txt", "")
        for f in os.listdir(_PROMPT_DIR)
        if f.startswith("rag_prompt_") and f.endswith(".txt")
    ]
