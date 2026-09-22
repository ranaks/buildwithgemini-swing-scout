# Unit tests for A2UI integration

import json
from unittest.mock import MagicMock
from google.genai import types
from google.adk.models.llm_response import LlmResponse
from app.agent import root_agent, schema_manager
from app.a2ui_utils import a2ui_callback


def test_agent_a2ui_configured():
    assert root_agent.after_model_callback is not None
    assert root_agent.after_model_callback == a2ui_callback
    assert "<a2ui-json>" in root_agent.instruction
    assert "A2UI" in root_agent.instruction
    assert "Card" in root_agent.instruction
    assert schema_manager._version == "0.8"


def test_a2ui_callback_rewraps_valid_surface():
    ctx = MagicMock()
    valid_a2ui_text = json.dumps([
        {"beginRendering": {"surfaceId": "test_surface", "root": "card_1"}},
        {
            "surfaceUpdate": {
                "surfaceId": "test_surface",
                "components": [
                    {
                        "id": "card_1",
                        "component": {
                            "Card": {
                                "child": "text_1"
                            }
                        }
                    },
                    {
                        "id": "text_1",
                        "component": {
                            "Text": {
                                "text": {"literalString": "NVDA Bullish Breakout"},
                                "usageHint": "h1"
                            }
                        }
                    }
                ]
            }
        }
    ])
    raw_response = LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=valid_a2ui_text)]
        )
    )

    result = a2ui_callback(ctx, raw_response)
    assert result is not None
    assert result.custom_metadata == {"a2a:response": "true"}
    assert len(result.content.parts) == 2
    for part in result.content.parts:
        assert part.inline_data is not None
        assert part.inline_data.mime_type == "text/plain"
        assert b"<a2a_datapart_json>" in part.inline_data.data
        assert b"application/json+a2ui" in part.inline_data.data
