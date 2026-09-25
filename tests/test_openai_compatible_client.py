import asyncio
import json

import httpx
import pytest

from pricing_agents.openai_compatible_client import OpenAICompatibleModelClient


def decision_content(**overrides):
    result = {
        "price": 1.62,
        "justification": "Test decision.",
        "used_competitor_info": False,
        "notes": "Retain this test price.",
    }
    result.update(overrides)
    return json.dumps(result)


def completion(content=None):
    return {
        "id": "mock-response-1",
        "model": "mock-returned-model",
        "choices": [{"message": {"content": content or decision_content()}}],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "completion_tokens_details": {"reasoning_tokens": 7},
            "total_tokens": 30,
        },
    }


async def generate_with_mock(handler, **settings):
    client = OpenAICompatibleModelClient(
        model="gemini-3.7-flash",
        api_key="dummy-secret-key",
        base_url="https://provider.example/v1",
        **settings,
    )
    assert client._client.follow_redirects is False
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), follow_redirects=False
    )
    try:
        return await client.generate(system_prompt="system", user_prompt="user")
    finally:
        await client.close()


def test_paper_payload_metadata_and_secret_free_receipt(tmp_path):
    captured = []

    def handle(request):
        assert str(request.url) == "https://provider.example/v1/chat/completions"
        captured.append(json.loads(request.content))
        return httpx.Response(200, json=completion())

    receipt_path = tmp_path / "private" / "receipts.jsonl"
    result = asyncio.run(generate_with_mock(
        handle, seed=0, temperature=1.2, reasoning_effort="high", receipt_path=receipt_path
    ))
    payload = captured[0]
    assert payload["seed"] == 0
    assert payload["temperature"] == 1.2
    assert payload["reasoning_effort"] == "high"
    schema_envelope = payload["response_format"]["json_schema"]
    assert schema_envelope["strict"] is True
    assert schema_envelope["name"] == "pricing_decision"
    schema = schema_envelope["schema"]
    assert list(schema["properties"]) == [
        "price", "justification", "used_competitor_info", "notes"
    ]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["price"]["minimum"] == 1.0
    assert schema["properties"]["price"]["maximum"] == 3.0
    assert result.price == 1.62
    assert result.api_metadata["model_returned"] == "mock-returned-model"
    assert result.api_metadata["seed_requested"] == 0
    assert result.api_metadata["temperature_requested"] == 1.2
    assert result.api_metadata["usage"]["thought_tokens"] == 7
    receipt = json.loads(receipt_path.read_text())
    assert receipt["request"] == payload
    assert receipt["response"]["id"] == "mock-response-1"
    assert "headers" not in receipt
    assert "dummy-secret-key" not in receipt_path.read_text()


def test_optional_sampling_settings_omitted():
    def handle(request):
        payload = json.loads(request.content)
        assert "seed" not in payload
        assert "temperature" not in payload
        assert "reasoning_effort" not in payload
        return httpx.Response(200, json=completion())

    asyncio.run(generate_with_mock(handle))


@pytest.mark.parametrize("content", [
    "not JSON", decision_content(price=3.1), decision_content(justification="  "),
    decision_content(notes="x" * 2001), decision_content(extra_field=True),
])
def test_invalid_decision_rejected_inside_client(content):
    with pytest.raises(ValueError):
        asyncio.run(generate_with_mock(lambda request: httpx.Response(
            200, json=completion(content)
        )))


@pytest.mark.parametrize("body", [None, [], {}, {"choices": []},
    {"choices": [{"message": {"content": ""}}]}])
def test_missing_output_is_rejected(body):
    with pytest.raises(RuntimeError):
        asyncio.run(generate_with_mock(lambda request: httpx.Response(200, json=body)))


def test_redirect_is_not_followed_and_error_body_is_not_logged(tmp_path):
    calls = []

    def handle(request):
        calls.append(str(request.url))
        return httpx.Response(
            307, headers={"Location": "https://different.example/steal"},
            text="private-provider-error",
        )

    receipt_path = tmp_path / "receipts.jsonl"
    with pytest.raises(RuntimeError, match="HTTP 307"):
        asyncio.run(generate_with_mock(handle, receipt_path=receipt_path))
    assert len(calls) == 1
    receipt_text = receipt_path.read_text()
    assert "private-provider-error" not in receipt_text
    assert "different.example" not in receipt_text
    assert json.loads(receipt_text)["http_status"] == 307


def test_request_error_is_sanitized(tmp_path):
    def handle(request):
        raise httpx.ConnectError("private error with dummy-secret-key", request=request)

    receipt_path = tmp_path / "receipts.jsonl"
    with pytest.raises(RuntimeError, match="ConnectError") as failure:
        asyncio.run(generate_with_mock(handle, receipt_path=receipt_path))
    assert "dummy-secret-key" not in str(failure.value)
    assert "dummy-secret-key" not in receipt_path.read_text()


@pytest.mark.parametrize("base_url", [
    "http://provider.example/v1", "https://user:secret@provider.example/v1",
    "https://provider.example/v1?key=secret", "https://provider.example/v1#token",
    "https://provider.example/v1?", "https://", "https://provider.example:bad",
])
def test_unsafe_endpoint_rejected_before_client_creation(base_url):
    with pytest.raises(ValueError, match="HTTPS"):
        OpenAICompatibleModelClient(model="test", api_key="dummy", base_url=base_url)


def test_no_default_endpoint(monkeypatch):
    monkeypatch.delenv("GEMINI_OPENAI_COMPATIBLE_BASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="BASE_URL is not set"):
        OpenAICompatibleModelClient(model="test", api_key="dummy")
