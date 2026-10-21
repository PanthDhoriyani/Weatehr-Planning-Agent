"""
memory.py — Unit 3 Extension: Long-Term Memory
------------------------------------------------
Implements a simple but demonstrable memory system for the Weather Agent.

Short-Term Memory  = the messages list in AgentState (already handled by LangGraph)
Long-Term Memory   = this file → persists to memory.json so it survives restarts

What gets stored:
  - cities the user has asked about
  - last recommendation per city
  - query count (so we can say "You've asked about Pune 3 times")
"""

import json
import os
from datetime import datetime

# where to store the long-term memory file (same folder as project root)
MEMORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "memory.json"
)


def _load_raw() -> dict:
    """Load raw memory dict from disk, or return empty structure."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"cities": {}, "total_queries": 0, "last_active": None}


def _save_raw(data: dict) -> None:
    """Persist memory dict to disk."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------
# Public API
# ---------------------------------------------------------------

def remember_city(city: str, recommendation: str) -> None:
    """
    Record that the user asked about a city and what we recommended.
    Called AFTER the agent gives its answer.
    """
    data = _load_raw()

    city_key = city.strip().lower()

    if city_key not in data["cities"]:
        data["cities"][city_key] = {
            "display_name": city.strip().title(),
            "query_count": 0,
            "last_queried": None,
            "last_recommendation": None
        }

    entry = data["cities"][city_key]
    entry["query_count"] += 1
    entry["last_queried"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry["last_recommendation"] = recommendation[:200]  # keep it short

    data["total_queries"] += 1
    data["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    _save_raw(data)


def get_memory_context() -> str:
    """
    Returns a short string that gets injected into the system prompt.
    This is how the LLM 'knows' what the user has asked before.
    """
    data = _load_raw()

    if not data["cities"]:
        return "No previous queries recorded yet."

    lines = []
    for key, val in data["cities"].items():
        count = val["query_count"]
        last  = val["last_queried"] or "unknown"
        rec   = val["last_recommendation"] or "N/A"
        lines.append(
            f"  • {val['display_name']}: asked {count}x, last on {last}. "
            f"Last recommendation: {rec}"
        )

    total = data["total_queries"]
    summary = f"User has made {total} total weather quer{'y' if total==1 else 'ies'}.\n"
    summary += "Cities previously asked about:\n" + "\n".join(lines)
    return summary


def get_all_memory() -> dict:
    """Return the full raw memory dict (used by the UI to display memory panel)."""
    return _load_raw()


def clear_memory() -> None:
    """Wipe all long-term memory (used by the clear button in UI)."""
    _save_raw({"cities": {}, "total_queries": 0, "last_active": None})
