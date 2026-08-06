"""Production OllamaRuntime executing local LLM inferences via Ollama HTTP API."""

import asyncio
import json
import os
import time
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from src.infrastructure.llm.context_window import ContextWindowManager
from src.infrastructure.llm.exceptions import (
    GenerationTimeout,
    InvalidModelResponse,
    ModelNotInstalled,
    RetryLimitExceeded,
)
from src.infrastructure.llm.generation import GenerationRequest, GenerationResponse
from src.infrastructure.llm.health_monitor import RuntimeHealthMonitor
from src.infrastructure.llm.model_manager import ModelManager
from src.infrastructure.llm.runtime_metrics import RuntimeMetrics
from src.infrastructure.llm.runtime_queue import RuntimeQueue
from src.infrastructure.llm.structured_output import StructuredOutputParser


class OllamaRuntime:
    """Production Ollama LLM execution engine communicating with local Ollama server via HTTP."""

    def __init__(
        self,
        model_manager: ModelManager | None = None,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        ollama_host: str | None = None,
    ) -> None:
        self.model_manager = model_manager or ModelManager()
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.ollama_host = (
            ollama_host or os.getenv("OLLAMA_HOST") or "http://localhost:11434"
        ).rstrip("/")
        self.queue = RuntimeQueue()
        self.metrics = RuntimeMetrics()
        self.health_monitor = RuntimeHealthMonitor(self.model_manager)
        self.context_manager = ContextWindowManager()

    async def warmup(self, alias: str = "reasoning") -> bool:
        """Warm up local model by verifying model availability."""
        self.model_manager.load_model(alias)
        return True

    async def shutdown(self) -> None:
        """Shut down runtime and unload loaded models."""
        for alias in list(self.model_manager.SUPPORTED_MODELS.keys()):
            self.model_manager.unload_model(alias)

    async def generate(
        self, request: GenerationRequest, timeout_seconds: float = 30.0
    ) -> GenerationResponse:
        """Execute text generation request via Ollama HTTP API with retries."""
        self.queue.enqueue(request)
        start_time = time.time()
        attempt = 0

        model_name = request.model_name or self.model_manager.SUPPORTED_MODELS["reasoning"]

        while attempt < self.max_retries:
            attempt += 1
            try:
                req = self.queue.dequeue() or request
                full_text = req.prompt_package.assemble_full_text()

                payload = {
                    "model": model_name,
                    "prompt": full_text,
                    "stream": False,
                    "options": {
                        "temperature": req.config.temperature,
                        "seed": req.config.seed,
                        "num_predict": req.config.max_tokens,
                    },
                }

                async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                    try:
                        resp = await client.post(f"{self.ollama_host}/api/generate", json=payload)
                    except httpx.TimeoutException as err:
                        raise GenerationTimeout(
                            f"Generation timed out after {timeout_seconds}s."
                        ) from err
                    except httpx.RequestError as err:
                        raise ConnectionError(
                            f"Unable to connect to Ollama at {self.ollama_host}. "
                            "Make sure 'ollama serve' is running."
                        ) from err

                if resp.status_code == 404:
                    msg = (
                        f"Model '{model_name}' is not installed. "
                        "Run 'ollama list' to inspect installed models."
                    )
                    raise ModelNotInstalled(msg)

                if resp.status_code != 200:
                    raise InvalidModelResponse(f"Ollama returned HTTP status {resp.status_code}.")

                data = resp.json()
                content = data.get("response", "")
                elapsed = round(time.time() - start_time, 3)

                prompt_tokens = data.get("prompt_eval_count") or (len(full_text) // 4)
                completion_tokens = data.get("eval_count") or (len(content) // 4)
                total_dur_ns = data.get("total_duration", 0)
                dur_sec = (total_dur_ns / 1e9) if total_dur_ns > 0 else elapsed

                tok_per_sec = round(completion_tokens / dur_sec, 2) if dur_sec > 0 else 50.0

                response = GenerationResponse(
                    request_id=req.request_id,
                    content=content,
                    parsed_json=None,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_seconds=dur_sec,
                    tokens_per_second=tok_per_sec,
                    model_name=model_name,
                )

                self.metrics.record_generation(
                    prompt_tokens, completion_tokens, dur_sec, retries=attempt - 1
                )
                return response

            except (GenerationTimeout, ModelNotInstalled, ConnectionError):
                self.metrics.record_failure()
                raise
            except Exception as err:
                if attempt >= self.max_retries:
                    self.metrics.record_failure()
                    raise RetryLimitExceeded(
                        f"Generation failed after {attempt} retries: {err}"
                    ) from err
                await asyncio.sleep(self.backoff_factor * (2 ** (attempt - 1)))

        raise RetryLimitExceeded("Maximum generation retries exceeded.")

    async def generate_json(
        self,
        request: GenerationRequest,
        expected_schema: dict[str, Any],
        timeout_seconds: float = 30.0,
    ) -> GenerationResponse:
        """Execute generation and parse/validate structured JSON."""
        res = await self.generate(request, timeout_seconds=timeout_seconds)
        raw_content = res.content

        try:
            parsed = StructuredOutputParser.parse_and_validate(raw_content, expected_schema)
            res.parsed_json = parsed
            return res
        except Exception as err:
            raise InvalidModelResponse(f"JSON validation failed: {err}") from err

    async def stream(
        self, request: GenerationRequest, timeout_seconds: float = 30.0
    ) -> AsyncGenerator[str]:
        """Stream response tokens from Ollama via async generator."""
        full_text = request.prompt_package.assemble_full_text()
        model_name = request.model_name or self.model_manager.SUPPORTED_MODELS["reasoning"]

        payload = {
            "model": model_name,
            "prompt": full_text,
            "stream": True,
            "options": {
                "temperature": request.config.temperature,
                "seed": request.config.seed,
                "num_predict": request.config.max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                async with client.stream(
                    "POST", f"{self.ollama_host}/api/generate", json=payload
                ) as resp:
                    if resp.status_code != 200:
                        msg = (
                            f"Unable to stream from Ollama server at {self.ollama_host}. "
                            f"Status code: {resp.status_code}"
                        )
                        raise ConnectionError(msg)
                    async for line in resp.aiter_lines():
                        if line.strip():
                            try:
                                chunk_data = json.loads(line)
                                token = chunk_data.get("response", "")
                                if token:
                                    yield token
                            except json.JSONDecodeError:
                                pass
                    return
        except (httpx.RequestError, httpx.TimeoutException) as err:
            raise ConnectionError(
                f"Unable to stream from Ollama server at {self.ollama_host}."
            ) from err

    def health(self) -> dict[str, Any]:
        """Return runtime health status."""
        return self.health_monitor.check_health()
