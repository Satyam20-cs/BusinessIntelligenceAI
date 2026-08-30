from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def load_csv(filename: str) -> pd.DataFrame:
    """
    Load a CSV from the project's data directory.

    Automatically converts the 'date' column to pandas datetime
    when present.
    """

    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {path}"
        )

    df = pd.read_csv(path)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    return df


def load_all():
    """
    Load all datasets required by InsightX.
    """

    return {
        "sales": load_csv("sales.csv"),
        "inventory": load_csv("inventory.csv"),
        "customer": load_csv("customer_metrics.csv"),
        "feedback_text": load_csv("customer_feedback.csv"),
    }