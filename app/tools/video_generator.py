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

"""Tool for generating trade setup and chart motion videos using Gemini Omni Flash Preview."""

import base64
import logging
import uuid
from typing import Any, Dict

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

logger = logging.getLogger(__name__)

# Hardcoded project ID and Cloud Storage bucket name
PROJECT_ID = "qwiklabs-gcp-04-58a029e5210a"
BUCKET_NAME = "swingscout-charts-58a029e5210a"
MODEL_NAME = "gemini-omni-flash-preview"
LOCATION = "global"


async def generate_setup_video(
    ticker: str,
    prompt: str = "",
    tool_context: ToolContext = None,
) -> Dict[str, Any]:
    """Generates a short visual trading video demonstrating a swing trade momentum setup, candlestick pattern, or breakout chart animation for a stock ticker.

    Uses Google's Omni model (gemini-omni-flash-preview) in the global region.
    The generated video is saved to the session artifacts panel via tool_context and uploaded
    directly from memory to the public Cloud Storage bucket, returning its public HTTPS URL.

    Args:
        ticker: The stock ticker symbol (e.g. 'NVDA', 'AMD', 'TSLA', 'AAPL').
        prompt: Optional specific description of the chart motion, breakout movement, or technical pattern.
        tool_context: Context object automatically injected by the ADK framework.

    Returns:
        A dictionary containing the status, public Cloud Storage URL, filename, and message.
    """
    clean_ticker = ticker.strip().upper()
    descriptive_prompt = (
        f"A sleek financial motion graphic showing a swing trading technical chart breakout for ticker {clean_ticker}. "
        f"{prompt.strip() if prompt else 'Dynamic green Japanese candlesticks rising across the screen, breaking above key horizontal resistance level with surging volume bars and upward momentum.'} "
        "Professional trading terminal aesthetic, smooth animation."
    )

    try:
        # Initialize Google GenAI client targeting Vertex AI in the global region
        genai_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )

        interaction = genai_client.interactions.create(
            model=MODEL_NAME,
            input=descriptive_prompt,
        )

        video_bytes = None
        mime_type = "video/mp4"

        if interaction and getattr(interaction, "output_video", None):
            out_vid = interaction.output_video
            if getattr(out_vid, "data", None):
                raw_data = out_vid.data
                if isinstance(raw_data, str):
                    video_bytes = base64.b64decode(raw_data)
                else:
                    video_bytes = raw_data
            if getattr(out_vid, "mime_type", None):
                mime_type = out_vid.mime_type

        if not video_bytes:
            return {
                "status": "error",
                "message": f"No video could be generated for ticker {clean_ticker}.",
            }

        filename = f"video_{clean_ticker.lower()}_{uuid.uuid4().hex[:8]}.mp4"

        # 1. Save artifact to tool_context so it appears in the Playground's Artifacts panel
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            try:
                await tool_context.save_artifact(filename=filename, artifact=artifact_part)
                logger.info("Saved video artifact %s in tool_context", filename)
            except Exception as e:
                logger.warning("Could not save video artifact %s to tool_context: %s", filename, e)

        # 2. Upload video bytes directly to Cloud Storage (no local file created)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "ticker": clean_ticker,
            "filename": filename,
            "public_url": public_url,
            "message": f"Successfully generated swing setup video for {clean_ticker}. Viewable at: {public_url}",
        }
    except Exception as exc:
        logger.error("Error generating swing setup video for %s: %s", clean_ticker, exc)
        return {
            "status": "error",
            "message": f"Failed to generate swing setup video: {str(exc)}",
        }
