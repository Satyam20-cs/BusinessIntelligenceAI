from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "feedback.json"

def save_feedback(feedback_type, note):
    rows = []
    if PATH.exists():
        try:
            rows = json.loads(PATH.read_text(encoding="utf-8"))
        except Exception:
            rows = []
    rows.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "feedback": feedback_type,
        "note": note
    })
    PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")

def load_feedback():
    if not PATH.exists():
        return []
    try:
        return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
