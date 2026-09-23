# Unit tests for Video Generator Tool using Gemini Omni Flash Preview

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.tools.video_generator import (
    BUCKET_NAME,
    LOCATION,
    MODEL_NAME,
    PROJECT_ID,
    generate_setup_video,
)


@pytest.mark.asyncio
async def test_generate_setup_video_success():
    fake_video_bytes = b"fakevideodatabytesforanimation"
    fake_b64_str = base64.b64encode(fake_video_bytes).decode("utf-8")

    mock_output_video = MagicMock()
    mock_output_video.data = fake_b64_str
    mock_output_video.mime_type = "video/mp4"

    mock_interaction = MagicMock()
    mock_interaction.output_video = mock_output_video

    mock_genai_client = MagicMock()
    mock_genai_client.interactions.create.return_value = mock_interaction

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
        result = await generate_setup_video(
            ticker="NVDA",
            prompt="Bullish breakout motion with volume surge",
            tool_context=mock_tool_context,
        )

        # Verify GenAI client initialization targeting global region
        mock_genai_cls.assert_called_once_with(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        # Verify interactions.create call
        mock_genai_client.interactions.create.assert_called_once()
        call_kwargs = mock_genai_client.interactions.create.call_args.kwargs
        assert call_kwargs["model"] == MODEL_NAME
        assert "NVDA" in call_kwargs["input"]

        # Verify tool_context.save_artifact was called
        mock_tool_context.save_artifact.assert_awaited_once()
        artifact_call_kwargs = mock_tool_context.save_artifact.call_args.kwargs
        assert "nvda" in artifact_call_kwargs["filename"]
        assert artifact_call_kwargs["filename"].endswith(".mp4")
        assert artifact_call_kwargs["artifact"] is not None

        # Verify Storage upload from memory (no local file)
        mock_storage_cls.assert_called_once_with(project=PROJECT_ID)
        mock_storage_client.bucket.assert_called_once_with(BUCKET_NAME)
        mock_blob.upload_from_string.assert_called_once_with(fake_video_bytes, content_type="video/mp4")

        # Verify result dictionary
        assert result["status"] == "success"
        assert result["ticker"] == "NVDA"
        assert result["public_url"].startswith(f"https://storage.googleapis.com/{BUCKET_NAME}/")
        assert result["filename"] in result["public_url"]


@pytest.mark.asyncio
async def test_generate_setup_video_no_video_returned():
    mock_interaction = MagicMock()
    mock_interaction.output_video = None

    mock_genai_client = MagicMock()
    mock_genai_client.interactions.create.return_value = mock_interaction

    with patch("google.genai.Client", return_value=mock_genai_client):
        result = await generate_setup_video(
            ticker="TSLA",
            prompt="Test prompt",
            tool_context=None,
        )
        assert result["status"] == "error"
        assert "No video could be generated" in result["message"]


@pytest.mark.asyncio
async def test_generate_setup_video_exception():
    mock_genai_client = MagicMock()
    mock_genai_client.interactions.create.side_effect = RuntimeError("API quota reached")

    with patch("google.genai.Client", return_value=mock_genai_client):
        result = await generate_setup_video(
            ticker="AAPL",
            prompt="Test prompt",
            tool_context=None,
        )
        assert result["status"] == "error"
        assert "Failed to generate swing setup video" in result["message"]
