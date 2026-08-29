"""Módulo de Guardrails y validación de seguridad de prompts en tiempo real."""

import logging
import re
from typing import Tuple

logger = logging.getLogger("Guardrails")

# Patrones precompilados de detección de Prompt Injection y Jailbreaks
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives)", re.IGNORECASE),
    re.compile(r"(system\s+override|mode\s+developer|jailbreak|bypass\s+security)", re.IGNORECASE),
    re.compile(r"(olvida|ignora)\s+(todas\s+las\s+)?(instrucciones|directivas)", re.IGNORECASE),
    re.compile(r"(modo\s+desarrollador|inyección\s+de\s+prompt|saltar\s+reglas)", re.IGNORECASE),
    re.compile(r"(reveal|muestra)\s+(system\s+prompt|tu\s+prompt\s+del\s+sistema)", re.IGNORECASE),
]


class SecurityGuardrails:
    """Validador heurístico local de bajo costo (0 tokens) para consultas de entrada."""

    @staticmethod
    def validate_query(query: str) -> Tuple[bool, str]:
        """Evalúa si una consulta es segura antes de enviarla a los agentes."""
        if not query or len(query.strip()) < 3:
            return False, "La consulta es demasiado corta o vacía."

        if len(query) > 3000:
            return False, "La consulta excede la longitud máxima permitida (3000 caracteres)."

        # Detección de patrones de ataque / jailbreak
        for pattern in _INJECTION_PATTERNS:
            if pattern.search(query):
                logger.warning(f"Guardrail activado por posible inyección: '{query[:60]}...'")
                return False, "Consulta bloqueada por Guardrails de Seguridad (Posible Prompt Injection detectado)."

        return True, "Consulta validada con éxito."
