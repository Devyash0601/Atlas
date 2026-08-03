"""Unit tests for Sprint 1.1 Production Prompt Engine Subsystem."""

import pytest

from src.infrastructure.llm.conversation_memory import ConversationMemory
from src.infrastructure.llm.exceptions import (
    ContextOverflowError,
    MemoryError,
    PromptValidationError,
    StructuredOutputError,
    TemplateNotFoundError,
    TemplateRenderingError,
)
from src.infrastructure.llm.prompt_engine import PromptEngine
from src.infrastructure.llm.prompt_package import PromptPackage
from src.infrastructure.llm.prompt_registry import PromptRegistry, PromptSchema
from src.infrastructure.llm.prompt_template import PromptTemplate
from src.infrastructure.llm.research_memory import ResearchMemory
from src.infrastructure.llm.retrieval_memory import RetrievalMemory
from src.infrastructure.llm.structured_output import StructuredOutputParser
from src.infrastructure.llm.token_counter import TokenCounter
from src.infrastructure.llm.workflow_memory import WorkflowMemory


def test_prompt_template_rendering() -> None:
    """Verify deterministic prompt template rendering."""
    tmpl = PromptTemplate(
        system_template="System: {role}",
        developer_template="Dev: {mode}",
        user_template="User: {query}",
    )
    res = tmpl.render(role="Scientist", mode="Strict", query="Analyze LST")
    assert res["system"] == "System: Scientist"
    assert res["developer"] == "Dev: Strict"
    assert res["user"] == "User: Analyze LST"

    with pytest.raises(TemplateRenderingError):
        tmpl.render(role="Scientist")  # Missing mode and query


def test_prompt_registry_versioning_and_validation() -> None:
    """Verify PromptRegistry versioning, schema registration, and validation."""
    registry = PromptRegistry()
    tmpl = PromptTemplate(user_template="Hello {name}")
    schema_v1 = PromptSchema(
        id="test_prompt",
        version="1.0",
        description="Test prompt v1",
        owner="Team A",
        input_schema={"name": "str"},
        output_schema={"type": "object"},
    )
    registry.register(tmpl, schema_v1)

    _, s = registry.get("test_prompt", "1.0")
    assert s.version == "1.0"

    registry.validate_variables("test_prompt", "1.0", {"name": "Alice"})

    with pytest.raises(PromptValidationError):
        registry.validate_variables("test_prompt", "1.0", {})  # Missing name

    with pytest.raises(TemplateNotFoundError):
        registry.get("non_existent")


def test_token_counter_and_overflow() -> None:
    """Verify local TokenCounter budget calculations and ContextOverflowError."""
    counter = TokenCounter(chars_per_token=4.0)
    text = "A" * 400
    tokens = counter.count_tokens(text)
    assert tokens == 100

    # Budget validation passing
    counter.validate_budget(text, context_window=1000, reserved_output_tokens=200)

    # Overflow budget rejection
    with pytest.raises(ContextOverflowError):
        counter.validate_budget(text, context_window=200, reserved_output_tokens=150)


def test_structured_output_parser() -> None:
    """Verify production StructuredOutputParser JSON validation and type coercion."""
    raw_text = (
        '```json\n{"name": "Land Surface Temperature", "score": "42.5", "tags": ["lst"]}\n```'
    )
    schema = {
        "required": ["name", "score"],
        "properties": {
            "name": {"type": "string"},
            "score": {"type": "number"},
            "tags": {"type": "array"},
        },
    }
    parsed = StructuredOutputParser.parse_and_validate(raw_text, schema)
    assert parsed["name"] == "Land Surface Temperature"
    assert parsed["score"] == 42.5
    assert parsed["tags"] == ["lst"]

    with pytest.raises(StructuredOutputError):
        StructuredOutputParser.parse_and_validate('{"name": "Test"}', schema)  # Missing score

    with pytest.raises(StructuredOutputError):
        StructuredOutputParser.parse_and_validate("Invalid JSON text", schema)


def test_4_memory_systems_full_lifecycle() -> None:
    """Verify add, remove, search, summarize, clear, serialize, deserialize for 4 memory classes."""
    # 1. ConversationMemory
    cm = ConversationMemory(window_size=2)
    cm.add("user", "Hello")
    cm.add("assistant", "Hi there")
    cm.add("user", "How are you?")
    assert len(cm.get_messages()) == 2  # Window size cap
    assert len(cm.search("How")) == 1
    assert "turns" in cm.summarize()
    cm_serialized = cm.serialize()
    cm_deserialized = ConversationMemory.deserialize(cm_serialized)
    assert len(cm_deserialized.get_messages()) == 2
    cm.clear()
    assert len(cm.get_messages()) == 0

    # 2. WorkflowMemory
    wm = WorkflowMemory()
    wm.add("step_1", {"data": 123}, decision="proceed")
    assert len(wm.search("step_1")) == 1
    assert "steps" in wm.summarize()
    wm_serialized = wm.serialize()
    wm_deserialized = WorkflowMemory.deserialize(wm_serialized)
    assert len(wm_deserialized.search("step_1")) == 1
    wm.remove("step_1")
    with pytest.raises(MemoryError):
        wm.remove("step_1")

    # 3. ResearchMemory
    rm = ResearchMemory()
    rm.set_hypothesis("UHI Effect in Paris")
    rm.add("f1", "LST is 4C higher in city center", "10.1016/j.rse.2024")
    assert len(rm.search("Paris")) == 0
    assert len(rm.search("LST")) == 1
    assert "UHI Effect" in rm.summarize()
    rm_serialized = rm.serialize()
    rm_deserialized = ResearchMemory.deserialize(rm_serialized)
    assert rm_deserialized.hypothesis == "UHI Effect in Paris"
    rm.remove("f1")
    assert len(rm.search("LST")) == 0

    # 4. RetrievalMemory
    rtm = RetrievalMemory()
    rtm.add("c1", "Landsat ST_B10 thermal band calculation", "Smith 2024", 0.92)
    assert len(rtm.search("Landsat")) == 1
    assert rtm.get_citations() == ["Smith 2024"]
    rtm_serialized = rtm.serialize()
    rtm_deserialized = RetrievalMemory.deserialize(rtm_serialized)
    assert rtm_deserialized.get_citations() == ["Smith 2024"]
    rtm.remove("c1")
    assert len(rtm.get_citations()) == 0


def test_context_builder_and_prompt_engine() -> None:
    """Verify ContextBuilder assembling PromptPackage and PromptEngine end-to-end flow."""
    engine = PromptEngine()

    cm = ConversationMemory()
    cm.add("user", "What is the LST anomaly?")

    rm = ResearchMemory()
    rm.set_hypothesis("LST correlates with NDBI")

    rtm = RetrievalMemory()
    rtm.add("c1", "NDBI urban index formula", "Jones 2023", 0.98)

    package: PromptPackage = engine.render_package(
        template_id="hypothesis_generation",
        question="UHI Hyderabad",
        region="Hyderabad",
        conversation_memory=cm,
        research_memory=rm,
        retrieval_memory=rtm,
    )

    assert package.total_prompt_tokens > 0
    assert "Jones 2023" in package.citations
    assert "HYDERABAD" in package.assemble_full_text().upper()
