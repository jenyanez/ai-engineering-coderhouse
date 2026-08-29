"""Herramientas de cómputo cuantitativo, CAGR y estadísticas para el Agente de Análisis."""

import json
import math
from typing import List
from langchain_core.tools import tool


@tool
def calculate_cagr_and_growth(start_value: float, end_value: float, periods: int) -> str:
    """Calcula la Tasa de Crecimiento Anual Compuesta (CAGR) y el crecimiento total porcentual.
    
    Args:
        start_value: Valor inicial numérico (ej. 67.0).
        end_value: Valor final proyectado (ej. 1300.0).
        periods: Número de años o períodos transcurridos (ej. 6).
    """
    if start_value <= 0 or end_value <= 0 or periods <= 0:
        return json.dumps({
            "error": "Todos los valores deben ser mayores que cero para calcular CAGR."
        }, ensure_ascii=False)
        
    cagr = ((end_value / start_value) ** (1.0 / periods)) - 1.0
    total_growth = ((end_value - start_value) / start_value) * 100.0
    
    return json.dumps({
        "start_value": start_value,
        "end_value": end_value,
        "periods_years": periods,
        "cagr_percentage": round(cagr * 100.0, 2),
        "total_growth_percentage": round(total_growth, 2),
        "multiplier": round(end_value / start_value, 2)
    }, ensure_ascii=False)


@tool
def compute_statistical_metrics(values_json: str) -> str:
    """Calcula estadísticas descriptivas (media, mediana, desviación estándar, min, max) sobre una lista de números.
    
    Args:
        values_json: Cadena JSON con lista de números (ej. '[67.0, 1300.0, 48.5]').
    """
    try:
        data = json.loads(values_json)
        if not isinstance(data, list) or len(data) == 0:
            return json.dumps({"error": "Se requiere una lista no vacía de números."}, ensure_ascii=False)
            
        numbers: List[float] = [float(x) for x in data]
        n = len(numbers)
        mean_val = sum(numbers) / n
        
        sorted_nums = sorted(numbers)
        if n % 2 == 1:
            median_val = sorted_nums[n // 2]
        else:
            median_val = (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2.0
            
        variance = sum((x - mean_val) ** 2 for x in numbers) / n
        std_dev = math.sqrt(variance)
        
        return json.dumps({
            "count": n,
            "mean": round(mean_val, 2),
            "median": round(median_val, 2),
            "std_dev": round(std_dev, 2),
            "min": min(numbers),
            "max": max(numbers)
        }, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": f"Error procesando métricas: {str(exc)}"}, ensure_ascii=False)
