from datetime import datetime
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PATH = (
    ROOT
    / "data"
    / "feedback_log.json"
)


def _load_raw():

    if not PATH.exists():
        return []

    try:

        content = PATH.read_text(
            encoding="utf-8"
        )

        if not content.strip():
            return []

        return json.loads(content)

    except Exception:

        return []


def save_feedback(
    kind,
    note,
    persona,
):
    """
    Persist feedback from the user.
    """

    rows = _load_raw()

    rows.append(
        {
            "timestamp": (
                datetime.now()
                .isoformat(
                    timespec="seconds"
                )
            ),

            "kind": kind,

            "note": str(note),

            "persona": str(persona),
        }
    )

    PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    PATH.write_text(
        json.dumps(
            rows,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def load_feedback():
    """
    Return persisted feedback records.
    """

    return _load_raw()