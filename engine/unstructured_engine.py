import re
import pandas as pd

THEMES = {
    "stockout": ["out of stock", "stockout", "unavailable", "sold out"],
    "delivery": ["late delivery", "delayed", "delivery late", "arrived late"],
    "quality": ["damaged", "broken", "defective", "quality"],
    "price": ["expensive", "price", "costly", "discount"],
    "checkout": ["checkout", "payment", "cart", "website"],
    "return": ["return", "refund", "exchange"]
}

POSITIVE = ["good", "great", "fast", "easy", "excellent", "happy", "love"]
NEGATIVE = ["bad", "late", "poor", "broken", "expensive", "difficult", "unhappy", "terrible"]

def sentiment_score(text):
    text = str(text).lower()
    pos = sum(word in text for word in POSITIVE)
    neg = sum(word in text for word in NEGATIVE)
    return (pos - neg) / max(pos + neg, 1)

def extract_themes(feedback_df):
    rows = []
    for text in feedback_df["feedback_text"].fillna(""):
        t = str(text).lower()
        found = [theme for theme, words in THEMES.items()
                 if any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in words)]
        rows.append({
            "feedback_text": text,
            "themes": ", ".join(found) if found else "other",
            "sentiment": sentiment_score(text)
        })

    out = pd.DataFrame(rows)
    theme_counts = {}
    for themes in out["themes"]:
        for theme in themes.split(", "):
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

    summary = (
        pd.DataFrame(
            [{"theme": k, "mentions": v} for k, v in theme_counts.items()]
        )
        .sort_values("mentions", ascending=False)
    )
    return out, summary
