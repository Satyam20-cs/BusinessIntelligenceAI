from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df

def load_all():
    return {
        "sales": load_csv("sales.csv"),
        "inventory": load_csv("inventory.csv"),
        "customer": load_csv("customer_metrics.csv"),
        "feedback_text": load_csv("customer_feedback.csv")
    }
