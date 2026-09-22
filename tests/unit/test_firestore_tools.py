# Unit tests for SwingScout Firestore tools

from unittest.mock import MagicMock, patch
from app.tools.firestore_db import get_stock_setup, list_stock_setups, save_stock_setup


def test_get_stock_setup_found():
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "ticker": "NVDA",
        "current_price": 128.50,
        "advice": "Strong momentum",
    }
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    with patch("app.tools.firestore_db.get_db_client", return_value=mock_db):
        res = get_stock_setup("nvda")
        assert res["status"] == "found"
        assert res["ticker"] == "NVDA"
        assert res["current_price"] == 128.50


def test_get_stock_setup_not_found():
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    with patch("app.tools.firestore_db.get_db_client", return_value=mock_db):
        res = get_stock_setup("XYZ")
        assert res["status"] == "not_found"


def test_save_stock_setup():
    mock_db = MagicMock()
    mock_doc_ref = MagicMock()
    mock_existing_doc = MagicMock()
    mock_existing_doc.exists = False
    mock_doc_ref.get.return_value = mock_existing_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    with patch("app.tools.firestore_db.get_db_client", return_value=mock_db):
        msg = save_stock_setup(
            ticker="TSLA",
            advice="Bullish breakout",
            current_price=242.0,
            rsi_14=58.0,
        )
        assert "Successfully saved" in msg
        mock_doc_ref.set.assert_called_once()
