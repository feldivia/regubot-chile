"""Cliente wrapper para la API de Anthropic Claude."""

import logging

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

_client: anthropic.AsyncAnthropic | None = None


def get_claude_client() -> anthropic.AsyncAnthropic:
    """Singleton del cliente async de Anthropic."""
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def generar_con_claude(
    mensajes: list[dict],
    system: str,
    tools: list[dict] | None = None,
    max_tokens: int = 4096,
    stream: bool = True,
):
    """Genera una respuesta con Claude, opcionalmente con streaming y tool use."""
    client = get_claude_client()

    params = {
        "model": settings.claude_model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": mensajes,
    }
    if tools:
        params["tools"] = tools

    if stream:
        async with client.messages.stream(**params) as stream_response:
            async for event in stream_response:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield {"tipo": "texto", "contenido": event.delta.text}
                elif event.type == "content_block_start":
                    if event.content_block.type == "tool_use":
                        yield {
                            "tipo": "tool_call",
                            "contenido": {
                                "id": event.content_block.id,
                                "name": event.content_block.name,
                            },
                        }
                elif event.type == "message_stop":
                    yield {"tipo": "fin", "contenido": ""}
    else:
        response = await client.messages.create(**params)
        for block in response.content:
            if block.type == "text":
                yield {"tipo": "texto", "contenido": block.text}
            elif block.type == "tool_use":
                yield {
                    "tipo": "tool_call",
                    "contenido": {
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    },
                }
