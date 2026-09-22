# 🎯 SwingScout — AI Swing Trading Assistant

> A conversational trading assistant that helps swing traders identify momentum setups, compare peer tickers, and manage risk using technical indicators and quantitative sizing.

<div align="center">

![SwingScout Demo](demo.gif)

[![Build with Gemini](https://img.shields.io/badge/Build%20with%20Gemini-Track%203-4285F4?logo=google&logoColor=white)](https://antigravity.google)
[![Agent Development Kit](https://img.shields.io/badge/ADK-2.2.0-34A853)](https://google.github.io/adk-docs/)
[![Google Cloud Agent Runtime](https://img.shields.io/badge/Google%20Cloud-Agent%20Runtime-EA4335?logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![A2UI Enabled](https://img.shields.io/badge/UI-A2UI%20v0.8-FBBC04)](https://adk.dev/integrations/a2ui/)

</div>

---

## 📖 Overview

**SwingScout** is an intelligent swing trading assistant built with the **Agent Development Kit (ADK)** and deployed on **Google Cloud Vertex AI Agent Runtime**. 

Designed for active swing traders who evaluate stocks on multi-day to multi-week time horizons, SwingScout combines objective technical indicators (RSI, 20/50/200 SMA, MACD, Volume) with personalized risk management and rich visual UI cards. It eliminates emotional trading decisions by enforcing strict risk-to-reward ratios and disciplined position sizing.

---

## ✨ Key Features

- **📊 Technical Swing Setup Analysis**: Evaluates trend strength, support/resistance levels, moving average alignment (Golden/Death Crosses), and overbought/oversold conditions (RSI).
- **⚔️ Peer Ticker Comparison**: Compares sector competitors (e.g. NVDA vs AMD) side-by-side to pinpoint momentum leaders and relative strength divergences.
- **🧮 Quantitative Position Sizing**: Uses an isolated code execution sandbox to compute exact share allocations and risk parameters based on portfolio equity and stop-loss distance.
- **🗃️ Persistent Watchlists & Trade Setups**: Stores, tracks, and retrieves setups from a Cloud Firestore database.
- **📈 Visual Chart & Pattern Generation**: Synthesizes candlestick pattern illustrations and technical chart diagrams.
- **📚 Grounded Trading Principles**: Grounded in classic market literature (*The Pitfalls of Speculation* by Thomas Gibson) to provide time-tested trading wisdom.
- **🪟 Interactive A2UI Cards**: Renders structured visual cards, indicator summaries, and comparison tables directly inside the chat stream.

---

## 🛠️ Google Cloud Tools & Architecture

| Google Cloud Tool | Role in SwingScout | Implementation |
|---|---|---|
| 🧠 **Vertex AI Memory Bank** | Cross-session long-term memory | Remembers trader preferences (account size, risk percentage per trade, preferred timeframes) and active watchlists across sessions via `PreloadMemoryTool` and callback hooks. |
| 🗄️ **Cloud Firestore** | Persistent NoSQL database | Stores, queries, and compares trade setups and watchlists in the `setups` collection (`lookup_setup`, `save_setup`, `compare_setups`). |
| 🖼️ **Cloud Storage (GCS)** | Public object storage | Hosts generated technical chart diagrams and candlestick graphics (`swingscout-charts-...`) for reliable inline display. |
| 📖 **Vertex AI RAG Engine** | Document grounding | Grounded on classic financial literature (*The Pitfalls of Speculation*) to offer disciplined risk psychology. |
| 🎨 **Gemini Image Generation** | Media generation | Uses `gemini-3.1-flash-lite-image` to generate annotated technical charts and candlestick setups, automatically publishing them to Cloud Storage and the Playground. |
| 🧪 **Vertex AI Code Sandbox** | Safe code execution | Uses `AgentEngineSandboxCodeExecutor` to run Python math in an isolated container for exact position sizing and risk/reward calculations. |
| 🪟 **A2UI (v0.8) & Basic Catalog** | Rich agent-first UI | Built with `A2uiSchemaManager` and `a2ui_utils.py` to stream structured cards (`Card`, `Column`, `Row`, `Text`, `Image`) directly to the user. |
| 🌐 **Agent Runtime & A2A Proxy** | Production serving | Deployed to Vertex AI Reasoning Engine / Agent Runtime and interfaced via a FastAPI proxy over the Agent-to-Agent (A2A) protocol. |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Google Cloud SDK (`gcloud`) authenticated with your project
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- `agents-cli` (`uv tool install google-agents-cli`)

### 1. Run Locally with Agents Playground

```bash
# Install dependencies
agents-cli install

# Launch the interactive local playground
agents-cli playground
```

### 2. Run the Custom Frontend (FastAPI + A2A Web Chat)

```bash
cd frontend

# Install frontend dependencies
pip install -r requirements.txt

# Set deployment and agent environment variables
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"

# Start the web chat interface
python main.py
```
Open [http://localhost:8080](http://localhost:8080) in your browser.

---

## 📂 Project Structure

```
swing-scout/
├── app/
│   ├── agent.py                 # Core ADK agent definition & system instructions
│   ├── a2ui_utils.py            # A2UI response formatting & schema callback
│   ├── fast_api_app.py          # FastAPI application wrapper
│   └── tools/
│       ├── calculator.py        # Position sizing & risk calculator
│       ├── firestore_db.py      # Firestore trade setup & watchlist database
│       └── image_generator.py   # Gemini image generation & Cloud Storage uploader
├── frontend/
│   ├── main.py                  # A2A protocol proxy connecting UI to Agent Engine
│   ├── requirements.txt         # Frontend proxy dependencies
│   └── static/
│       └── index.html           # Web chat UI with native A2UI card renderer
├── agents-cli-manifest.yaml     # Agents CLI project metadata
├── deployment_metadata.json     # Agent Runtime deployment details
├── project_brief.md             # Project requirements and domain specification
└── pyproject.toml               # Project dependencies and configuration
```

---

## 📄 License

This project was built for the **Build with Gemini World Tour** (Track 3: Agent-First Apps) and is licensed under the Apache 2.0 License.
