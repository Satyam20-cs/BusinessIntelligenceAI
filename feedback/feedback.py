from pathlib import Path
from datetime import datetime
import json

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "feedback_log.json"

def save_feedback(kind, note, persona):
    rows = []
    if PATH.exists():
        try:
            rows = json.loads(PATH.read_text(encoding="utf-8"))
        except Exception:
            rows = []

    rows.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "kind": kind,
        "note": note,
        "persona": persona
    })
    PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")

def load_feedback():
    if not PATH.exists():
        return []
    try:
        return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
