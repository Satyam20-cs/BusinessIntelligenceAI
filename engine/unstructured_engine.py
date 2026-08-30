import re

import pandas as pd


THEMES = {
    "stockout": [
        "out of stock",
        "stockout",
        "unavailable",
        "sold out",
    ],

    "delivery": [
        "late delivery",
        "delayed",
        "delivery late",
        "arrived late",
    ],

    "quality": [
        "damaged",
        "broken",
        "defective",
        "quality",
    ],

    "price": [
        "expensive",
        "price",
        "costly",
        "discount",
    ],

    "checkout": [
        "checkout",
        "payment",
        "cart",
        "website",
    ],

    "return": [
        "return",
        "refund",
        "exchange",
    ],
}


POSITIVE = [
    "good",
    "great",
    "fast",
    "easy",
    "excellent",
    "happy",
    "love",
]


NEGATIVE = [
    "bad",
    "late",
    "poor",
    "broken",
    "expensive",
    "difficult",
    "unhappy",
    "terrible",
]


def sentiment_score(text):
    """
    Lightweight deterministic sentiment score.

    Range:
    -1 = negative
     0 = neutral
    +1 = positive
    """

    text = str(text).lower()

    positive_count = sum(
        word in text
        for word in POSITIVE
    )

    negative_count = sum(
        word in text
        for word in NEGATIVE
    )

    total = (
        positive_count
        + negative_count
    )

    if total == 0:
        return 0.0

    return (
        positive_count
        - negative_count
    ) / total


def extract_themes(feedback_df):
    """
    Extract business-relevant themes
    from customer feedback.
    """

    rows = []

    if (
        feedback_df is None
        or feedback_df.empty
        or "feedback_text"
        not in feedback_df.columns
    ):

        return (
            pd.DataFrame(),
            pd.DataFrame(
                columns=[
                    "theme",
                    "mentions",
                ]
            )
        )

    for text in feedback_df[
        "feedback_text"
    ].fillna(""):

        text_lower = str(
            text
        ).lower()

        found_themes = []

        for theme, words in THEMES.items():

            matched = any(
                re.search(
                    r"\b"
                    + re.escape(word)
                    + r"\b",
                    text_lower,
                )
                for word in words
            )

            if matched:
                found_themes.append(
                    theme
                )

        if not found_themes:
            found_themes = [
                "other"
            ]

        rows.append(
            {
                "feedback_text": text,
                "themes": ", ".join(
                    found_themes
                ),
                "sentiment": round(
                    sentiment_score(text),
                    3
                ),
            }
        )

    output = pd.DataFrame(rows)

    theme_counts = {}

    for themes in output["themes"]:

        for theme in themes.split(", "):

            theme_counts[theme] = (
                theme_counts.get(
                    theme,
                    0
                )
                + 1
            )

    summary = (
        pd.DataFrame(
            [
                {
                    "theme": theme,
                    "mentions": count,
                }

                for theme, count
                in theme_counts.items()
            ]
        )
        .sort_values(
            "mentions",
            ascending=False
        )
        .reset_index(drop=True)
    )

    return output, summary