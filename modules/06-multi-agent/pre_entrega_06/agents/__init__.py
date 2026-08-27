"""Paquete de agentes: Supervisor, especialistas en investigación y análisis, y síntesis."""

from agents.research_agent import research_node
from agents.analyst_agent import analyst_node
from agents.supervisor_agent import supervisor_node
from agents.synthesis_agent import synthesis_node

__all__ = [
    "research_node",
    "analyst_node",
    "supervisor_node",
    "synthesis_node",
]
