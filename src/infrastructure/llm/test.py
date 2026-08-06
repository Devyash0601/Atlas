import asyncio

from src.infrastructure.llm.generation import GenerationRequest
from src.infrastructure.llm.ollama_runtime import OllamaRuntime
from src.infrastructure.llm.prompt_engine import PromptEngine


async def main() -> None:
    engine = PromptEngine()
    runtime = OllamaRuntime()

    package = engine.render_package(
        template_id="hypothesis",
        question="How has urban expansion affected land surface temperature in Hyderabad?",
        region="Hyderabad",
    )

    request = GenerationRequest(
        request_id="test001",
        model_name="qwen2.5-coder:7b",
        prompt_package=package,
    )

    result = await runtime.generate(request)

    print(result.content)


if __name__ == "__main__":
    asyncio.run(main())
