# Unit tests for Image Generator Tool

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.tools.image_generator import (
    BUCKET_NAME,
    MODEL_NAME,
    PROJECT_ID,
    generate_chart_image,
)


@pytest.mark.asyncio
async def test_generate_chart_image_success():
    fake_image_bytes = b"\x89PNG\r\n\x1a\nfakeimagebytes"

    mock_part = MagicMock()
    mock_part.text = None
    mock_part.inline_data.data = fake_image_bytes
    mock_part.inline_data.mime_type = "image/png"

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.return_value = mock_response

    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket

    mock_tool_context = MagicMock()
    mock_tool_context.save_artifact = AsyncMock()

    with (
        patch("google.genai.Client", return_value=mock_genai_client) as mock_genai_cls,
        patch("google.cloud.storage.Client", return_value=mock_storage_client) as mock_storage_cls,
    ):
        result = await generate_chart_image(
            ticker="NVDA",
            prompt="Bullish breakout over 50 SMA",
            tool_context=mock_tool_context,
        )

        # Verify GenAI client initialization
        mock_genai_cls.assert_called_once_with(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        # Verify model call
        mock_genai_client.models.generate_content.assert_called_once()
        call_kwargs = mock_genai_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == MODEL_NAME
        assert "NVDA" in call_kwargs["contents"]

        # Verify tool_context.save_artifact was called
        mock_tool_context.save_artifact.assert_awaited_once()
        artifact_call_kwargs = mock_tool_context.save_artifact.call_args.kwargs
        assert "nvda" in artifact_call_kwargs["filename"]
        assert artifact_call_kwargs["artifact"] is not None

        # Verify Storage upload
        mock_storage_cls.assert_called_once_with(project=PROJECT_ID)
        mock_storage_client.bucket.assert_called_once_with(BUCKET_NAME)
        mock_blob.upload_from_string.assert_called_once_with(fake_image_bytes, content_type="image/png")

        # Verify result dictionary
        assert result["status"] == "success"
        assert result["ticker"] == "NVDA"
        assert result["public_url"].startswith(f"https://storage.googleapis.com/{BUCKET_NAME}/")
        assert result["filename"] in result["public_url"]


@pytest.mark.asyncio
async def test_generate_chart_image_no_image_returned():
    mock_candidate = MagicMock()
    mock_candidate.content.parts = []
    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.return_value = mock_response

    with patch("google.genai.Client", return_value=mock_genai_client):
        result = await generate_chart_image(
            ticker="AMD",
            prompt="Test prompt",
            tool_context=None,
        )
        assert result["status"] == "error"
        assert "No image could be generated" in result["message"]
