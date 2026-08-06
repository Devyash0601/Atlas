"""Unit tests for Sprint 1.2 Production Ollama Runtime Subsystem."""

import asyncio
import json
import time
from unittest.mock import patch

import httpx
import pytest

from src.infrastructure.llm.context_window import ContextWindowManager
from src.infrastructure.llm.exceptions import (
    ContextOverflow,
    InvalidModelResponse,
    ModelNotInstalled,
    QueueOverflow,
    StreamingCancelled,
)
from src.infrastructure.llm.generation import GenerationConfig, GenerationRequest
from src.infrastructure.llm.health_monitor import RuntimeHealthMonitor
from src.infrastructure.llm.model_manager import ModelManager
from src.infrastructure.llm.model_registry import ModelRegistry
from src.infrastructure.llm.ollama_runtime import OllamaRuntime
from src.infrastructure.llm.prompt_package import PromptPackage
from src.infrastructure.llm.runtime_metrics import RuntimeMetrics
from src.infrastructure.llm.runtime_queue import RuntimeQueue
from src.infrastructure.llm.streaming import StreamingEngine


def test_model_registry_discovery() -> None:
    """Verify ModelRegistry specs, installed tracking, and discovery."""
    registry = ModelRegistry()
    spec = registry.get_spec("qwen2.5-coder:7b-instruct-q5_k_m")
    assert spec.estimated_ram_mb == 5500
    assert spec.quantization == "Q5_K_M"

    assert len(registry.list_installed()) == 4

    with pytest.raises(ModelNotInstalled):
        registry.get_spec("unregistered_model")


def test_model_manager_idle_unloading() -> None:
    """Verify ModelManager lazy loading, memory calculation, and idle unloading."""
    manager = ModelManager(idle_timeout_seconds=0.1)
    spec = manager.load_model("reasoning")
    assert spec.estimated_ram_mb == 5500
    assert manager.get_memory_usage_mb() == 5500

    time.sleep(0.15)

    unloaded = manager.unload_idle_models()
    assert "qwen2.5-coder:7b" in unloaded
    assert manager.get_memory_usage_mb() == 0


def test_runtime_queue_concurrency_and_priority() -> None:
    """Verify RuntimeQueue FIFO priority ordering, cancellation, and overflow handling."""
    queue = RuntimeQueue(max_capacity=2, max_concurrency=1)
    pkg = PromptPackage(
        system_prompt="S", developer_prompt="D", user_prompt="U", retrieved_context=""
    )

    req1 = GenerationRequest(prompt_package=pkg, request_id="r1", priority=1)
    req2 = GenerationRequest(prompt_package=pkg, request_id="r2", priority=10)

    queue.enqueue(req1)
    queue.enqueue(req2)

    # Dequeue req2 (priority 10) then req1 (priority 1)
    dequeued1 = queue.dequeue()
    assert dequeued1 is not None
    assert dequeued1.request_id == "r2"

    dequeued2 = queue.dequeue()
    assert dequeued2 is not None
    assert dequeued2.request_id == "r1"

    req3 = GenerationRequest(prompt_package=pkg, request_id="r3")
    req4 = GenerationRequest(prompt_package=pkg, request_id="r4")
    queue.enqueue(req3)
    queue.enqueue(req4)

    req5 = GenerationRequest(prompt_package=pkg, request_id="r5")
    # Queue full test
    with pytest.raises(QueueOverflow):
        queue.enqueue(req5)

    # Cancellation test
    queue.cancel("r3")
    dequeued3 = queue.dequeue()
    assert dequeued3 is not None
    assert dequeued3.request_id == "r4"
    queue.release()


def test_context_window_manager_trimming() -> None:
    """Verify ContextWindowManager trimming non-citation text preserving citations."""
    manager = ContextWindowManager()

    text = (
        "Paragraph 1: Background info.\n\n"
        "Paragraph 2 [Smith 2024]: Critical scientific citation evidence."
    )
    trimmed = manager.trim_context(text, max_tokens=30, preserve_citations=["Smith 2024"])
    assert "Smith 2024" in trimmed

    with pytest.raises(ContextOverflow):
        manager.trim_context(
            "Paragraph 1 [Smith 2024]: " + ("Huge text " * 1000),
            max_tokens=1,
            preserve_citations=["Smith 2024"],
        )


def test_runtime_metrics_and_health_monitor() -> None:
    """Verify RuntimeMetrics recording and RuntimeHealthMonitor status checks."""
    metrics = RuntimeMetrics()
    metrics.record_generation(prompt_tokens=10, completion_tokens=50, latency_seconds=2.0)
    stats = metrics.get_stats()
    assert stats["total_prompt_tokens"] == 10
    assert stats["avg_tokens_per_second"] == 25.0

    manager = ModelManager()
    monitor = RuntimeHealthMonitor(manager)
    health = monitor.check_health()
    assert health["status"] == "healthy"
    assert health["memory_usage_mb"] == 0


@pytest.mark.asyncio
async def test_streaming_engine_cancellation() -> None:
    """Verify StreamingEngine async token generation and cancellation event handling."""
    cancel_evt = asyncio.Event()
    cancel_evt.set()

    with pytest.raises(StreamingCancelled):
        async for _ in StreamingEngine.stream_tokens(
            "Quick test", timeout_seconds=1.0, cancel_event=cancel_evt
        ):
            pass


@pytest.mark.asyncio
async def test_ollama_runtime_generation_flow() -> None:
    """Verify OllamaRuntime warmup, generate, generate_json, streaming, and shutdown."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/generate":
            payload = json.loads(request.content.decode())
            if payload.get("stream"):
                stream_content = '{"response": "token1"}\n{"response": "token2"}\n'
                return httpx.Response(200, text=stream_content)
            return httpx.Response(
                200,
                json={
                    "model": "qwen2.5-coder:7b",
                    "response": '{"status": "ok", "value": 42}',
                    "done": True,
                    "prompt_eval_count": 10,
                    "eval_count": 5,
                    "total_duration": 50000000,
                },
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    orig_client = httpx.AsyncClient

    def mock_client(**kw):
        kw["transport"] = transport
        return orig_client(**kw)

    runtime = OllamaRuntime()
    assert await runtime.warmup("reasoning") is True

    pkg = PromptPackage(
        system_prompt="S",
        developer_prompt="D",
        user_prompt="Test user query",
        retrieved_context="",
    )
    config = GenerationConfig(temperature=0.1, max_tokens=512)
    req = GenerationRequest(prompt_package=pkg, config=config, request_id="test_req_1")

    with patch.object(httpx, "AsyncClient", mock_client):
        res = await runtime.generate(req)
        assert res.request_id == "test_req_1"
        assert res.tokens_per_second > 0

        json_res = await runtime.generate_json(req, expected_schema={"required": []})
        assert json_res.parsed_json is not None

        stream_chunks: list[str] = []
        async for chunk in runtime.stream(req):
            stream_chunks.append(chunk)
        assert len(stream_chunks) == 2

    assert runtime.health()["status"] == "healthy"
    await runtime.shutdown()


@pytest.mark.asyncio
async def test_ollama_runtime_connection_and_missing_model_errors() -> None:
    """Verify OllamaRuntime raises ConnectionError and ModelNotInstalled cleanly."""
    runtime = OllamaRuntime(ollama_host="http://127.0.0.1:59999")

    pkg = PromptPackage(
        system_prompt="S",
        developer_prompt="D",
        user_prompt="User query",
        retrieved_context="",
    )
    req = GenerationRequest(prompt_package=pkg, request_id="req_err")

    # Connection failure test
    with pytest.raises(ConnectionError):
        await runtime.generate(req)

    # Missing model 404 test
    def mock_404_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": "model not found"})

    transport = httpx.MockTransport(mock_404_handler)
    orig_client = httpx.AsyncClient

    def mock_client(**kw):
        kw["transport"] = transport
        return orig_client(**kw)

    with patch.object(httpx, "AsyncClient", mock_client):
        with pytest.raises(ModelNotInstalled):
            await runtime.generate(req)


@pytest.mark.asyncio
async def test_ollama_runtime_invalid_json_error() -> None:
    """Verify generate_json raises InvalidModelResponse when JSON is invalid."""

    def mock_text_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"model": "qwen2.5-coder:7b", "response": "Plain non-JSON text"},
        )

    transport = httpx.MockTransport(mock_text_handler)
    orig_client = httpx.AsyncClient

    def mock_client(**kw):
        kw["transport"] = transport
        return orig_client(**kw)

    runtime = OllamaRuntime()
    pkg = PromptPackage(
        system_prompt="S",
        developer_prompt="D",
        user_prompt="User query",
        retrieved_context="",
    )
    req = GenerationRequest(prompt_package=pkg, request_id="req_invalid_json")

    with patch.object(httpx, "AsyncClient", mock_client):
        with pytest.raises(InvalidModelResponse):
            await runtime.generate_json(req, expected_schema={"type": "object"})
