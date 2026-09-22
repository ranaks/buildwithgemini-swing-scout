# My agent: SwingScout

One-liner: A conversational trading assistant that helps swing traders identify momentum setups and compare peer tickers using technical indicators (RSI, Moving Averages, MACD, Volume).

Tool coverage:
- Memory: Trader's preferred swing timeframes (e.g., daily, 4-hour), max risk per trade, stop-loss rules, and active watchlist of tickers
- Tools: Ticker price and volume history lookup, technical indicator calculations (RSI, 20/50/200 SMA, MACD, ATR), and peer ticker discovery (e.g., sector competitors)
- Catalog/UI: Side-by-side indicator comparison tables, technical setup summary cards, and watchlist status cards rendered via A2UI (highlighting standout metrics, overbought/oversold RSI thresholds, and trend divergences)
- Image gen: Visual trade setup diagrams, candlestick pattern references, or chart trend infographics
- Sandbox: Position sizing calculations based on stop-loss distance, risk-to-reward ratio computations, and indicator crossover math

Analysis Instructions:
- Prominently highlight key comparative takeaways: designate the clear momentum/trend leader, flag critical technical levels (support/resistance, stop-loss), and highlight high-conviction risk-to-reward setups.

Core rails (everyone): memory, tools, eval, deploy, frontend
My stretch menu (pick later): A2UI comparison cards/tables, sandbox position sizing calculator, chart visualizations
First eval question: "Compare NVDA and AMD on the daily timeframe: which has the stronger swing momentum setup based on RSI and moving averages?"
