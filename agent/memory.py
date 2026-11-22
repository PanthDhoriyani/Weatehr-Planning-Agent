"""
memory.py — AgriShield AI: Persistent Long-Term Memory
-------------------------------------------------------
Manages two tiers of persistent state stored in memory.json:
1. Farm Profile: Default location, primary crop, growth stage, soil type, acreage.
2. Agro-Advisory History: Audit trail of past queries, specialist advice, and threat levels.

Persists across app restarts and is injected dynamically into the Supervisor and LLM nodes.
"""

import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "memory.json"
)

DEFAULT_FARM_PROFILE = {
    "location": "Pune",
    "crop": "Cotton",
    "growth_stage": "Flowering / Boll Formation",
    "soil_type": "Black Cotton Soil (Vertisol)",
    "acreage": 5.0
}


def _load_raw() -> dict:
    """Load raw memory dict from disk, or initialize if missing."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "farm_profile" not in data:
                    data["farm_profile"] = DEFAULT_FARM_PROFILE.copy()
                if "advisories" not in data:
                    data["advisories"] = []
                return data
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "farm_profile": DEFAULT_FARM_PROFILE.copy(),
        "advisories": [],
        "total_advisories": 0,
        "last_active": None
    }


def _save_raw(data: dict) -> None:
    """Persist memory dictionary to disk."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_farm_profile() -> dict:
    """Retrieve the current farm profile."""
    data = _load_raw()
    return data.get("farm_profile", DEFAULT_FARM_PROFILE.copy())


def update_farm_profile(location: str, crop: str, growth_stage: str, soil_type: str = None, acreage: float = 5.0) -> None:
    """Update and persist the farm profile."""
    data = _load_raw()
    data["farm_profile"] = {
        "location": location.strip().title(),
        "crop": crop.strip().title(),
        "growth_stage": growth_stage.strip(),
        "soil_type": soil_type.strip() if soil_type else "Medium Loam",
        "acreage": float(acreage)
    }
    data["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    _save_raw(data)


def remember_agri_advisory(location: str, crop: str, agent_name: str, query: str, advice_summary: str, threat_level: str = "MODERATE") -> None:
    """Record an agronomic recommendation in the advisory history log."""
    data = _load_raw()

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "location": location.strip().title(),
        "crop": crop.strip().title(),
        "agent": agent_name,
        "query": query[:120],
        "advice_summary": advice_summary[:250],
        "threat_level": threat_level
    }

    if "advisories" not in data:
        data["advisories"] = []

    # Prepend latest advisory and retain last 15 entries
    data["advisories"].insert(0, entry)
    data["advisories"] = data["advisories"][:15]

    data["total_advisories"] = data.get("total_advisories", 0) + 1
    data["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    _save_raw(data)


def get_memory_context() -> str:
    """
    Returns an agronomic context string injected into the LLM system prompt.
    """
    data = _load_raw()
    profile = data.get("farm_profile", DEFAULT_FARM_PROFILE)
    advisories = data.get("advisories", [])

    lines = [
        f"Active Farm Profile:",
        f"  • Location: {profile.get('location', 'Pune')}",
        f"  • Primary Crop: {profile.get('crop', 'Cotton')} (Growth Stage: {profile.get('growth_stage', 'Flowering')})",
        f"  • Soil Type: {profile.get('soil_type', 'Black Cotton Soil')}",
        f"  • Farm Size: {profile.get('acreage', 5.0)} Acres",
    ]

    if advisories:
        lines.append("\nRecent Farm Advisories:")
        for adv in advisories[:3]:
            lines.append(
                f"  • [{adv.get('timestamp', 'N/A')}] {adv.get('agent', 'Agent')} for {adv.get('crop', 'Crop')}: "
                f"Threat={adv.get('threat_level', 'LOW')} | Advice: {adv.get('advice_summary', '')}"
            )
    else:
        lines.append("\nNo previous advisory records found for this farm.")

    return "\n".join(lines)


def get_all_memory() -> dict:
    """Return complete memory structure for UI panels."""
    return _load_raw()


def clear_memory() -> None:
    """Reset advisories while preserving farm profile schema."""
    data = {
        "farm_profile": DEFAULT_FARM_PROFILE.copy(),
        "advisories": [],
        "total_advisories": 0,
        "last_active": None
    }
    _save_raw(data)
