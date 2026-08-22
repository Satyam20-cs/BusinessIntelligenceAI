from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df

def load_all():
    return {
        "sales": load_csv("sales.csv"),
        "inventory": load_csv("inventory.csv"),
        "customer_metrics": load_csv("customer_metrics.csv"),
    }
