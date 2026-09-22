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

"""Position sizing and trade risk calculation tool for SwingScout."""

from typing import Any


def calculate_position_size(
    entry_price: float,
    stop_loss_price: float,
    target_price: float,
    account_size: float = 10000.0,
    risk_percentage: float = 2.0,
) -> dict[str, Any]:
    """Calculate exact position sizing, share quantity, risk-to-reward ratio, and capital allocation for a swing trade.

    Args:
        entry_price: Planned entry price per share in USD.
        stop_loss_price: Price level where the trade will be exited to protect capital.
        target_price: Profit target price level where gains will be taken.
        account_size: Total account trading capital in USD (defaults to $10,000.00).
        risk_percentage: Maximum percentage of the account the trader is willing to lose on this trade (defaults to 2.0%).

    Returns:
        A dictionary with exact share counts, dollar risk, potential profit, risk-to-reward ratio, and allocation notes.
    """
    if entry_price <= 0:
        return {"error": "Entry price must be greater than zero."}

    risk_per_share = abs(entry_price - stop_loss_price)
    if risk_per_share <= 0:
        return {"error": "Stop loss price cannot equal entry price (zero risk per share)."}

    reward_per_share = abs(target_price - entry_price)
    risk_reward_ratio = round(reward_per_share / risk_per_share, 2)

    # Dollar budget allowed to lose on this single trade
    dollar_risk_budget = round(account_size * (risk_percentage / 100.0), 2)

    # Number of whole shares to purchase based on strict risk limit
    shares = int(dollar_risk_budget // risk_per_share)
    if shares == 0:
        return {
            "status": "warning",
            "message": (
                f"With a {risk_percentage}% risk limit (${dollar_risk_budget:.2f}) and a "
                f"${risk_per_share:.2f} stop-loss distance, you cannot purchase even 1 share "
                f"without exceeding your risk tolerance. Consider widening risk percentage or "
                f"selecting a tighter stop-loss setup."
            ),
            "dollar_risk_budget": dollar_risk_budget,
            "risk_per_share": round(risk_per_share, 2),
            "risk_reward_ratio": risk_reward_ratio,
        }

    total_capital_required = round(shares * entry_price, 2)
    percent_account_allocated = round((total_capital_required / account_size) * 100.0, 2)
    potential_dollar_loss = round(shares * risk_per_share, 2)
    potential_dollar_profit = round(shares * reward_per_share, 2)

    trade_quality = (
        "Excellent (High Conviction)"
        if risk_reward_ratio >= 3.0
        else "Solid (Favorable)"
        if risk_reward_ratio >= 2.0
        else "Marginal (Risk/Reward below 2:1 standard)"
    )

    notes = []
    if total_capital_required > account_size:
        notes.append(
            f"Note: Total investment of ${total_capital_required:,.2f} exceeds cash account size (${account_size:,.2f}); requires margin/leverage."
        )
    if risk_reward_ratio < 2.0:
        notes.append("Warning: Risk-to-reward ratio is below the standard 2:1 minimum for swing trading.")

    return {
        "status": "success",
        "shares_to_buy": shares,
        "entry_price": round(entry_price, 2),
        "stop_loss_price": round(stop_loss_price, 2),
        "target_price": round(target_price, 2),
        "risk_per_share": round(risk_per_share, 2),
        "reward_per_share": round(reward_per_share, 2),
        "risk_reward_ratio": f"{risk_reward_ratio}:1",
        "dollar_risk_budget": dollar_risk_budget,
        "actual_dollar_risk": potential_dollar_loss,
        "potential_dollar_profit": potential_dollar_profit,
        "total_capital_required": total_capital_required,
        "percent_account_allocated": f"{percent_account_allocated}%",
        "trade_quality": trade_quality,
        "notes": notes,
    }
