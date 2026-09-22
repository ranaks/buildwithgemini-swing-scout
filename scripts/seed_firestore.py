#!/usr/bin/env python3
"""Seed initial stock setups into Google Cloud Firestore.

Hardcodes GCP project ID as a string to prevent issues on Agent Platform.
"""

from datetime import datetime, timezone
from google.cloud import firestore

# Hardcode project ID as string as required (prevents numeric project ID issues on Agent Platform)
PROJECT_ID = "qwiklabs-gcp-04-58a029e5210a"
COLLECTION_NAME = "swing_setups"

INITIAL_SETUPS = [
    {
        "ticker": "NVDA",
        "company_name": "NVIDIA Corporation",
        "sector": "Semiconductors",
        "current_price": 128.50,
        "rsi_14": 62.4,
        "sma_50": 121.20,
        "sma_200": 110.05,
        "macd_signal": "Bullish crossover above zero line",
        "trend": "Bullish",
        "support_level": 124.00,
        "resistance_level": 132.00,
        "setup_type": "Breakout Pullback",
        "advice": (
            "Strong swing momentum leader above 50 SMA. Look for entry on pullback "
            "near $125 with tight stop-loss at $121, targeting $135+."
        ),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "ticker": "AMD",
        "company_name": "Advanced Micro Devices, Inc.",
        "sector": "Semiconductors",
        "current_price": 155.20,
        "rsi_14": 48.1,
        "sma_50": 153.80,
        "sma_200": 158.40,
        "macd_signal": "Neutral / Flat",
        "trend": "Consolidation",
        "support_level": 149.00,
        "resistance_level": 162.00,
        "setup_type": "Range Bound / Base Building",
        "advice": (
            "Consolidating around 50 SMA. Lacks NVDA's relative momentum. "
            "Wait for confirmed breakout above $162 before entering swing long."
        ),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "ticker": "TSLA",
        "company_name": "Tesla, Inc.",
        "sector": "Automotive & Clean Tech",
        "current_price": 242.80,
        "rsi_14": 58.7,
        "sma_50": 230.15,
        "sma_200": 205.60,
        "macd_signal": "Bullish continuation",
        "trend": "Bullish",
        "support_level": 235.00,
        "resistance_level": 255.00,
        "setup_type": "Momentum Continuation",
        "advice": (
            "High beta swing setup holding support at 20 EMA and 50 SMA. "
            "Bullish swing continuation targeting $260 with stop-loss at $234."
        ),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "ticker": "PLTR",
        "company_name": "Palantir Technologies Inc.",
        "sector": "Enterprise Software & AI",
        "current_price": 37.40,
        "rsi_14": 68.2,
        "sma_50": 33.10,
        "sma_200": 27.50,
        "macd_signal": "Strong bullish expansion",
        "trend": "Bullish Uptrend",
        "support_level": 35.50,
        "resistance_level": 40.00,
        "setup_type": "Trend Following High Conviction",
        "advice": (
            "Clear enterprise software momentum leader. RSI approaching overbought at 68.2; "
            "wait for mild intraday dip to $36.00 for favorable risk/reward."
        ),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "sector": "Consumer Technology",
        "current_price": 224.30,
        "rsi_14": 52.0,
        "sma_50": 222.80,
        "sma_200": 208.50,
        "macd_signal": "Neutral consolidation",
        "trend": "Base Building",
        "support_level": 220.00,
        "resistance_level": 230.00,
        "setup_type": "Base Consolidation",
        "advice": (
            "Steady base near 50 SMA. Low volatility swing setup. "
            "Watch for volume expansion before taking aggressive positions."
        ),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
]


def seed_firestore():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for item in INITIAL_SETUPS:
        doc_id = item["ticker"]
        doc_ref = collection.document(doc_id)
        doc_ref.set(item)
        print(f"Seeded {doc_id} into collection '{COLLECTION_NAME}'")

    print(f"Seeding completed successfully! Total items seeded: {len(INITIAL_SETUPS)}")


if __name__ == "__main__":
    seed_firestore()
