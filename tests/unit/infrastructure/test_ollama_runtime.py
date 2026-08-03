"""Unit tests for Sprint 1.2 Production Ollama Runtime Subsystem."""

import asyncio
import time

import pytest

from src.infrastructure.llm.context_window import ContextWindowManager
from src.infrastructure.llm.exceptions import (
    ContextOverflow,
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

    assert len(registry.list_installed()) == 3

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
    assert "qwen2.5-coder:7b-instruct-q5_k_m" in unloaded
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

    res = await runtime.generate(req)
    assert res.request_id == "test_req_1"
    assert res.tokens_per_second > 0

    json_res = await runtime.generate_json(req, expected_schema={"required": []})
    assert json_res.parsed_json is not None

    stream_chunks: list[str] = []
    async for chunk in runtime.stream(req):
        stream_chunks.append(chunk)
    assert len(stream_chunks) > 0

    assert runtime.health()["status"] == "healthy"
    await runtime.shutdown()
