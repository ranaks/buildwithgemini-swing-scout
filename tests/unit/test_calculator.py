# Unit tests for SwingScout Position Sizing Calculator

from app.tools.calculator import calculate_position_size


def test_calculate_position_size_standard():
    res = calculate_position_size(
        entry_price=100.0,
        stop_loss_price=95.0,
        target_price=115.0,
        account_size=10000.0,
        risk_percentage=2.0,
    )
    assert res["status"] == "success"
    # Budget = $200. Risk/share = $5. Shares = 40.
    assert res["shares_to_buy"] == 40
    assert res["actual_dollar_risk"] == 200.0
    assert res["potential_dollar_profit"] == 600.0
    assert res["risk_reward_ratio"] == "3.0:1"
    assert res["trade_quality"] == "Excellent (High Conviction)"


def test_calculate_position_size_zero_risk_error():
    res = calculate_position_size(
        entry_price=100.0,
        stop_loss_price=100.0,
        target_price=110.0,
    )
    assert "error" in res


def test_calculate_position_size_low_risk_warning():
    res = calculate_position_size(
        entry_price=500.0,
        stop_loss_price=400.0,
        target_price=600.0,
        account_size=1000.0,
        risk_percentage=1.0,  # $10 budget vs $100 risk/share
    )
    assert res["status"] == "warning"
