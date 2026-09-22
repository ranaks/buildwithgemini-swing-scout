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

"""Tool for generating trade setup and chart diagram images using Gemini 3.1 Flash-Lite Image."""

import base64
import logging
import uuid
from typing import Any, Dict

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types
from google.genai.types import GenerateContentConfig, Modality

logger = logging.getLogger(__name__)

# Hardcoded project ID and Cloud Storage bucket name
PROJECT_ID = "qwiklabs-gcp-04-58a029e5210a"
BUCKET_NAME = "swingscout-charts-58a029e5210a"
MODEL_NAME = "gemini-3.1-flash-lite-image"
LOCATION = "global"


async def generate_chart_image(
    ticker: str,
    prompt: str = "",
    tool_context: ToolContext = None,
) -> Dict[str, Any]:
    """Generates a visual trade setup diagram or technical chart pattern infographic for a stock ticker.

    The generated image is saved to the session artifacts panel via tool_context and uploaded
    directly from memory to the public Cloud Storage bucket, returning its public HTTPS URL.

    Args:
        ticker: The stock ticker symbol (e.g. 'NVDA', 'AMD', 'TSLA', 'AAPL').
        prompt: Optional specific description of the trade setup, candlestick pattern, or technical indicators to depict.
        tool_context: Context object automatically injected by the ADK framework.

    Returns:
        A dictionary containing the status, public Cloud Storage URL, filename, and message.
    """
    clean_ticker = ticker.strip().upper()
    descriptive_prompt = (
        f"Technical candlestick chart and swing trade pattern visualization for ticker {clean_ticker}. "
        f"{prompt.strip() if prompt else 'Clean daily candlestick swing trading setup diagram with key support and resistance lines, 50-day moving average, and RSI indicator visual.'} "
        "Clean modern financial trading infographic, professional presentation."
    )

    try:
        # Initialize Google GenAI client targeting Vertex AI in the global region
        genai_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )

        response = genai_client.models.generate_content(
            model=MODEL_NAME,
            contents=descriptive_prompt,
            config=GenerateContentConfig(
                response_modalities=[Modality.TEXT, Modality.IMAGE],
            ),
        )

        image_bytes = None
        mime_type = "image/png"
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    raw_data = part.inline_data.data
                    if isinstance(raw_data, str):
                        image_bytes = base64.b64decode(raw_data)
                    else:
                        image_bytes = raw_data
                    if part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
                    break

        if not image_bytes:
            return {
                "status": "error",
                "message": f"No image could be generated for ticker {clean_ticker}.",
            }

        file_ext = "jpg" if "jpeg" in mime_type.lower() else "png"
        filename = f"chart_{clean_ticker.lower()}_{uuid.uuid4().hex[:8]}.{file_ext}"

        # 1. Save artifact to tool_context so it appears in the Playground's Artifacts panel
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            try:
                await tool_context.save_artifact(filename=filename, artifact=artifact_part)
                logger.info("Saved artifact %s in tool_context", filename)
            except Exception as e:
                logger.warning("Could not save artifact %s to tool_context: %s", filename, e)

        # 2. Upload image bytes directly to Cloud Storage (no local file created)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "ticker": clean_ticker,
            "filename": filename,
            "public_url": public_url,
            "message": f"Successfully generated chart diagram for {clean_ticker}. Viewable at: {public_url}",
        }
    except Exception as exc:
        logger.error("Error generating chart image for %s: %s", clean_ticker, exc)
        return {
            "status": "error",
            "message": f"Failed to generate chart image: {str(exc)}",
        }
