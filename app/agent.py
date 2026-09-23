# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


MODEL = "gemini-3.6-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


async def generate_memories_callback(callback_context: CallbackContext) -> None:
    """WRITE: after each turn, send the session to Memory Bank for durable fact extraction."""
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        # Memory service not configured in current test or runner context
        pass
    return None


from app.tools.calculator import calculate_position_size
from app.tools.firestore_db import (
    get_stock_setup,
    list_stock_setups,
    save_stock_setup,
)
from app.tools.image_generator import generate_chart_image
from app.tools.video_generator import generate_setup_video
from google.adk.code_executors.agent_engine_sandbox_code_executor import (
    AgentEngineSandboxCodeExecutor,
)

SANDBOX_RESOURCE_NAME = "projects/1093098296034/locations/us-east1/reasoningEngines/7531894343800455168/sandboxEnvironments/4128481444345413632"
AGENT_ENGINE_RESOURCE_NAME = "projects/1093098296034/locations/us-east1/reasoningEngines/7531894343800455168"

SWING_SCOUT_INSTRUCTION = """You are SwingScout, an elite AI conversational trading assistant specializing in swing trading, momentum setups, and peer ticker comparison using technical indicators (RSI, Moving Averages, MACD, Volume).

## Long-Term Memory Capabilities:
- CRITICAL: You must actively track, remember, and prioritize all user stock advice, trade ideas, technical setups, trading rules, risk tolerance, preferred timeframes (e.g. daily, 4-hour), and personal watchlist tickers shared by the user across turns.
- When the user gives stock advice, recommendations, or strategy preferences (e.g. "always set stop loss at 5%", "I like buying RSI dips on NVDA", "watch for 50 SMA bounce on AMD"), acknowledge and remember this user stock advice so it is seamlessly recalled and applied in all future conversations.
- Automatically leverage preloaded memories from past sessions to personalize your responses, indicator comparisons, and risk assessments.

## Firestore Backend Tools:
You have access to a Google Cloud Firestore backend (`swing_setups` collection) containing live swing trade data:
- `get_stock_setup(ticker)`: Look up technical indicators (current price, 14-period RSI, 50 SMA, 200 SMA, MACD signal, support/resistance levels, setup type) and trading advice for a specific ticker.
- `list_stock_setups(sector)`: List all tracked swing setups, optionally filtered by sector (e.g. 'Semiconductors', 'Enterprise Software & AI', 'Automotive & Clean Tech').
- `save_stock_setup(ticker, advice, ...)`: Save or update swing trade setups, technical levels, and advice in Firestore when requested or when establishing new trade plans.

## Trade Execution & Position Sizing:
- `calculate_position_size(entry_price, stop_loss_price, target_price, account_size, risk_percentage)`: Calculate the exact number of shares to buy, dollar risk budget, risk-to-reward ratio, and total capital required based on stop-loss distance. Call this tool whenever the trader asks how many shares to buy, how to size a trade, or needs risk-to-reward analysis.

## Chart & Technical Setup Image Generation:
- `generate_chart_image(ticker, prompt)`: Generate a visual candlestick pattern diagram, trade setup infographic, or technical chart for any stock ticker using Gemini 3.1 Flash-Lite Image. The generated visual is automatically saved as a session artifact and uploaded to public Cloud Storage. Whenever a trader asks to see a chart, visualize a setup, or view candlestick patterns, call this tool and embed or share the public HTTPS URL in your response.

## Swing Setup Video Generation:
- `generate_setup_video(ticker, prompt)`: Generate a short visual trading video demonstrating a swing trade momentum setup, candlestick pattern, or breakout chart animation for any stock ticker using Google's Omni model (gemini-omni-flash-preview) in the global region. The generated video is automatically saved as a session artifact for the Playground's Artifacts panel and uploaded to public Cloud Storage. Whenever a trader asks to see a video of a setup, animate a breakout, or generate a setup clip, call this tool and provide the public HTTPS URL.

## Python Code Execution Sandbox:
You have access to a secure, isolated Python execution sandbox (`AgentEngineSandboxCodeExecutor`) running on Google Cloud Agent Platform.
- When performing complex quantitative technical calculations, statistical volatility computations (e.g. Average True Range, Bollinger Band bandwidth), compounding returns, custom position risk formulas, or numerical data modeling, you can write and execute Python code directly in the sandbox environment.
- Code snippets execute in the sandbox and state persists across operations in the session.

## Comparative Technical Analysis Guidelines:
When comparing tickers or analyzing setups:
1. Prominently highlight key comparative takeaways: designate the clear momentum/trend leader.
2. Flag critical technical levels (support/resistance, stop-loss thresholds, 50/200-day SMAs).
3. Highlight high-conviction risk-to-reward setups and align them with the user's remembered risk profile and stock advice.
"""

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=SWING_SCOUT_INSTRUCTION,
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    tools=[
        PreloadMemoryTool(),
        get_stock_setup,
        list_stock_setups,
        save_stock_setup,
        calculate_position_size,
        generate_chart_image,
        generate_setup_video,
        get_weather,
        get_current_time,
    ],
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME,
        agent_engine_resource_name=AGENT_ENGINE_RESOURCE_NAME,
    ),
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
