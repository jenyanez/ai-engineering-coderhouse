import asyncio
from typing import AsyncGenerator, List

import openai
from openai import AsyncOpenAI

from clients.base import BaseLLMClient
from schemas import ChatMessage, ModelResponse


class OpenAIClient(BaseLLMClient):
    """
    Implementación del cliente para la API de OpenAI.
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", config=None):
        super().__init__(api_key, model_name, config)
        # Inicializa el cliente oficial asíncrono
        self.client = AsyncOpenAI(api_key=self.api_key)

    def _format_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """Convierte nuestros esquemas Pydantic al formato de OpenAI."""
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=self._format_messages(messages),
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
            )
            
            choice = response.choices[0]
            return ModelResponse(
                content=choice.message.content,
                provider="openai",
                model_used=self.model_name,
                finish_reason=choice.finish_reason,
            )

        except openai.RateLimitError as e:
            # Resiliencia: Controlando el Rate Limit
            return ModelResponse(
                content=f"[Error de OpenAI] Rate limit excedido: {str(e)}",
                provider="openai",
                model_used=self.model_name,
                finish_reason="rate_limit_error"
            )
        except openai.APIConnectionError as e:
            # Resiliencia: Fallos de red
            return ModelResponse(
                content=f"[Error de red] Problema conectando a OpenAI: {str(e)}",
                provider="openai",
                model_used=self.model_name,
                finish_reason="connection_error"
            )
        except Exception as e:
            return ModelResponse(
                content=f"[Error inesperado] {str(e)}",
                provider="openai",
                model_used=self.model_name,
                finish_reason="unknown_error"
            )

    async def stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        try:
            stream_response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=self._format_messages(messages),
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                stream=True,  # Activamos el streaming
            )

            async for chunk in stream_response:
                # Extraemos de forma segura el delta
                content_chunk = chunk.choices[0].delta.content
                if content_chunk:
                    yield content_chunk

        except openai.RateLimitError as e:
            yield f"\n[Stream interrumpido: Rate limit de OpenAI -> {str(e)}]"
        except Exception as e:
            yield f"\n[Stream interrumpido: Error inesperado -> {str(e)}]"
