"""Unit tests for Local AI Runtime (ModelManager, PromptEngine, Memory, Streaming)."""

import pytest

from src.infrastructure.llm.memory import (
    ConversationMemory,
    ResearchMemory,
    RetrievalMemory,
    WorkflowMemory,
)
from src.infrastructure.llm.model_manager import ModelManager
from src.infrastructure.llm.model_monitoring import ModelBenchmark, ModelHealthMonitor
from src.infrastructure.llm.prompt_engine import ContextBuilder, PromptEngine, TokenCounter
from src.infrastructure.llm.streaming_engine import StreamingEngine
from src.infrastructure.llm.structured_output import StructuredOutputParser


def test_model_manager() -> None:
    """Verify ModelManager loading and memory tracking."""
    manager = ModelManager()
    assert manager.is_model_available("reasoning")

    info = manager.load_model("reasoning")
    assert info.is_loaded
    assert info.kind == "reasoning"
    assert manager.get_memory_usage_mb() == 5500

    status = manager.get_status()
    assert "loaded_models" in status

    assert manager.unload_model("reasoning")
    assert manager.get_memory_usage_mb() == 0

    with pytest.raises(ValueError):
        manager.load_model("invalid_model")


def test_prompt_engine_and_context_builder() -> None:
    """Verify PromptEngine and ContextBuilder."""
    engine = PromptEngine()
    rendered = engine.render("hypothesis", question="UHI Paris", region="Paris")
    assert "UHI Paris" in rendered

    ctx = (
        ContextBuilder()
        .add_system_instruction("Be precise")
        .add_retrieved_evidence("Smith 2024", "LST correlation")
        .build()
    )
    assert "SYSTEM:" in ctx
    assert "EVIDENCE [Smith 2024]:" in ctx

    tokens = TokenCounter.count_tokens("Hello world token test")
    assert tokens > 0


def test_structured_output_parser() -> None:
    """Verify StructuredOutputParser parsing and validation."""
    raw_json = '```json\n{"status": "success", "steps": ["a", "b"]}\n```'
    parsed = StructuredOutputParser.parse_json(raw_json)
    assert parsed["status"] == "success"

    with pytest.raises(ValueError):
        StructuredOutputParser.parse_json("not json text")


@pytest.mark.asyncio
async def test_streaming_engine() -> None:
    """Verify StreamingEngine async token streaming."""
    text = "The quick brown fox jumps over the lazy dog"
    tokens: list[str] = []
    async for token in StreamingEngine.stream_tokens(text, chunk_size=2):
        tokens.append(token)
    assert len(tokens) > 0


def test_4_tier_memory() -> None:
    """Verify 4-tier memory classes."""
    conv = ConversationMemory()
    conv.add_message("user", "Hello")
    assert len(conv.get_messages()) == 1
    conv.clear()
    assert len(conv.get_messages()) == 0

    wf = WorkflowMemory()
    wf.store_step_output("step1", {"result": "ok"})
    assert wf.get_step_output("step1") == {"result": "ok"}

    res = ResearchMemory()
    res.set_hypothesis("Hypothesis A")
    res.add_evidence("Ref 1", "Claim 1", 0.9)
    assert res.hypothesis == "Hypothesis A"

    ret = RetrievalMemory()
    ret.cache_chunk("c1", {"meta": 1})
    assert ret.get_cached_chunk("c1") == {"meta": 1}


def test_model_monitoring() -> None:
    """Verify ModelHealthMonitor and ModelBenchmark."""
    manager = ModelManager()
    monitor = ModelHealthMonitor(manager)
    health = monitor.check_health()
    assert health["status"] == "healthy"

    rate = ModelBenchmark.benchmark_inference(tokens_generated=100, elapsed_seconds=5.0)
    assert rate == 20.0
