import json
import os
from datetime import date

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def make_key(card_name: str, edition: str) -> str:
    return f"{card_name.strip().lower()}|{edition.strip().lower()}"


def should_notify(state: dict, card_name: str, edition: str, current_price: float, pct_change: float) -> bool:
    key = make_key(card_name, edition)
    entry = state.get(key)

    if entry is None:
        return True

    if current_price > entry.get("last_price", 0):
        return True

    return False


def record_notification(state: dict, card_name: str, edition: str, current_price: float, pct_change: float) -> None:
    key = make_key(card_name, edition)
    state[key] = {
        "last_price": current_price,
        "last_notified_pct": pct_change,
        "date": date.today().isoformat(),
    }
