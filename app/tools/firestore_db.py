# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Firestore database client and function tools for SwingScout.

Hardcodes GCP project ID as a string to avoid project number issues on Agent Platform.
"""

from datetime import datetime, timezone
import functools
from typing import Any
from google.cloud import firestore

# Hardcode project ID as string as required (prevents numeric project ID issues on Agent Platform)
PROJECT_ID = "qwiklabs-gcp-04-58a029e5210a"
COLLECTION_NAME = "swing_setups"


@functools.cache
def get_db_client() -> firestore.Client:
    """Returns a singleton Firestore client with hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def get_stock_setup(ticker: str) -> dict[str, Any]:
    """Retrieve technical indicators, swing setup details, and trading advice for a stock ticker from Firestore.

    Args:
        ticker: The stock ticker symbol (e.g. 'NVDA', 'AMD', 'TSLA', 'AAPL', 'PLTR').

    Returns:
        A dictionary containing stock metrics (current_price, RSI, 50/200 SMA, MACD, support/resistance) and trade advice.
    """
    clean_ticker = ticker.strip().upper()
    db = get_db_client()
    doc_ref = db.collection(COLLECTION_NAME).document(clean_ticker)
    doc = doc_ref.get()

    if not doc.exists:
        return {
            "ticker": clean_ticker,
            "status": "not_found",
            "message": f"No swing trade setup found for ticker {clean_ticker} in the Firestore database.",
        }

    data = doc.to_dict() or {}
    data["status"] = "found"
    return data


def list_stock_setups(sector: str | None = None) -> list[dict[str, Any]]:
    """List all tracked swing trade setups from Firestore, optionally filtered by sector.

    Args:
        sector: Optional sector filter (e.g. 'Semiconductors', 'Enterprise Software & AI', 'Automotive & Clean Tech').

    Returns:
        A list of dictionaries for each tracked stock setup.
    """
    db = get_db_client()
    col_ref = db.collection(COLLECTION_NAME)

    docs = col_ref.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        if sector:
            doc_sector = str(data.get("sector", "")).lower()
            if sector.lower() not in doc_sector:
                continue
        results.append(data)

    return results


def save_stock_setup(
    ticker: str,
    advice: str,
    setup_type: str = "Momentum Swing",
    current_price: float | None = None,
    rsi_14: float | None = None,
    support_level: float | None = None,
    resistance_level: float | None = None,
    trend: str | None = None,
    sector: str | None = None,
) -> str:
    """Save or update a stock swing setup, technical metrics, and trading advice in Firestore.

    Args:
        ticker: The stock ticker symbol to save or update (e.g. 'NVDA', 'AMD').
        advice: Specific swing trading advice, entry trigger, stop-loss, or price targets.
        setup_type: The classification of the setup (e.g. 'Breakout Pullback', 'Mean Reversion', 'Trend Continuation').
        current_price: Optional current market price of the stock.
        rsi_14: Optional 14-period RSI value.
        support_level: Optional critical support price level.
        resistance_level: Optional key resistance price level.
        trend: Optional trend direction ('Bullish', 'Bearish', 'Consolidation').
        sector: Optional industry sector.

    Returns:
        A confirmation message indicating that the setup was successfully saved.
    """
    clean_ticker = ticker.strip().upper()
    db = get_db_client()
    doc_ref = db.collection(COLLECTION_NAME).document(clean_ticker)

    existing_doc = doc_ref.get()
    existing_data = existing_doc.to_dict() if existing_doc.exists else {}

    payload = {
        "ticker": clean_ticker,
        "advice": advice,
        "setup_type": setup_type,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    if current_price is not None:
        payload["current_price"] = current_price
    elif "current_price" in existing_data:
        payload["current_price"] = existing_data["current_price"]

    if rsi_14 is not None:
        payload["rsi_14"] = rsi_14
    elif "rsi_14" in existing_data:
        payload["rsi_14"] = existing_data["rsi_14"]

    if support_level is not None:
        payload["support_level"] = support_level
    elif "support_level" in existing_data:
        payload["support_level"] = existing_data["support_level"]

    if resistance_level is not None:
        payload["resistance_level"] = resistance_level
    elif "resistance_level" in existing_data:
        payload["resistance_level"] = existing_data["resistance_level"]

    if trend is not None:
        payload["trend"] = trend
    elif "trend" in existing_data:
        payload["trend"] = existing_data["trend"]

    if sector is not None:
        payload["sector"] = sector
    elif "sector" in existing_data:
        payload["sector"] = existing_data["sector"]

    # Preserve any company_name or sma/macd values from existing record if not provided
    for key in ("company_name", "sma_50", "sma_200", "macd_signal"):
        if key in existing_data and key not in payload:
            payload[key] = existing_data[key]

    doc_ref.set(payload, merge=True)
    return f"Successfully saved swing trade setup and advice for {clean_ticker} in Firestore."
