"""Herramienta de cálculo financiero cuantitativo y proyecciones para el Analista."""

from typing import Any, Dict
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class CAGRCalculationInput(BaseModel):
    """Contrato de entrada para el cálculo de tasa de crecimiento anual compuesta."""

    val_start: float = Field(..., gt=0.0, description="Valor inicial en periodo base")
    val_end: float = Field(..., gt=0.0, description="Valor final proyectado")
    years: int = Field(..., gt=0, description="Número de años transcurridos")


@tool(args_schema=CAGRCalculationInput)
def calculate_cagr(val_start: float, val_end: float, years: int) -> Dict[str, Any]:
    """Calcula la tasa de crecimiento anual compuesta (CAGR) y el factor de expansión."""
    try:
        cagr = ((val_end / val_start) ** (1.0 / years) - 1.0) * 100.0
        expansion = val_end / val_start
        return {
            "valid_analysis": True,
            "cagr_percentage": round(cagr, 2),
            "expansion_factor": round(expansion, 2),
            "years_span": years,
            "interpretation": (
                f"Crecimiento proyectado a un CAGR del {cagr:.2f}%, "
                f"multiplicando el valor inicial por {expansion:.2f}x en {years} años."
            ),
        }
    except Exception as err:
        return {
            "valid_analysis": False,
            "error": f"Error en cálculo cuantitativo: {str(err)}",
        }
