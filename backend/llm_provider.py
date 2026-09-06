import os

import httpx

from telemetry import get_tracer


tracer = get_tracer("llm_provider")


class LLMProviderError(Exception):
    pass


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b",
)


async def _generate_with_ollama(
    prompt: str,
    schema: dict | None = None,
) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    if schema is not None:
        payload["format"] = schema
        payload["options"] = {
            "temperature": 0
        }

    with tracer.start_as_current_span(
        "llm.ollama.request"
    ) as span:
        span.set_attribute(
            "llm.provider",
            "ollama",
        )
        span.set_attribute(
            "llm.model",
            OLLAMA_MODEL,
        )
        span.set_attribute(
            "llm.structured_output",
            schema is not None,
        )
        span.set_attribute(
            "llm.prompt_characters",
            len(prompt),
        )

        try:
            async with httpx.AsyncClient(
                timeout=300
            ) as client:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json=payload,
                )

                response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                "Ollama request timed out."
            ) from exc
        except httpx.RequestError as exc:
            raise LLMProviderError(
                "Could not connect to Ollama."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                f"Ollama returned HTTP "
                f"{exc.response.status_code}."
            ) from exc

        result = response.json()

        if "response" not in result:
            raise LLMProviderError(
                "Ollama returned an unexpected response."
            )

        generated_text = result["response"]

        span.set_attribute(
            "llm.response_characters",
            len(generated_text),
        )

        return generated_text


async def generate_with_llm(
    prompt: str,
    schema: dict | None = None,
) -> str:
    provider = os.getenv(
        "LLM_PROVIDER",
        "ollama",
    ).lower()

    with tracer.start_as_current_span(
        "llm.generate"
    ) as span:
        span.set_attribute(
            "llm.provider",
            provider,
        )
        span.set_attribute(
            "llm.structured_output",
            schema is not None,
        )

        if provider == "ollama":
            return await _generate_with_ollama(
                prompt=prompt,
                schema=schema,
            )

        if provider == "azure":
            raise LLMProviderError(
                "Azure LLM provider is not configured yet."
            )

        raise LLMProviderError(
            f"Unsupported LLM_PROVIDER: {provider}"
        )
