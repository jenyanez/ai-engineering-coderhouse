"""
Pre-entrega 5: Agente de Razonamiento Cíclico con Memoria Persistente
Archivo: tools.py — Fase 1: Contrato de Herramientas

Define las herramientas que el agente puede invocar autónomamente.
Cada herramienta simula una operación de negocio (consulta a base de datos
de pedidos, catálogo de productos y tracking de envíos).

Los docstrings son CRÍTICOS: el LLM decide qué herramienta usar
basándose exclusivamente en estas descripciones.
"""

from langchain_core.tools import tool


# --- Base de datos simulada ---

CLIENTES_PEDIDOS: dict[int, dict] = {
    101: {"pedidos": 5, "total": 23000, "ultimo_pedido_id": 1001, "ultimo_producto_id": 301},
    102: {"pedidos": 3, "total": 14500, "ultimo_pedido_id": 1003, "ultimo_producto_id": 305},
    103: {"pedidos": 1, "total": 4200, "ultimo_pedido_id": 1004, "ultimo_producto_id": 310},
}

PRODUCTOS: dict[int, dict] = {
    301: {"nombre": "Teclado Mecánico RGB", "precio": 3500.00, "stock": 25},
    305: {"nombre": 'Monitor UltraWide 34"', "precio": 5200.00, "stock": 8},
    310: {"nombre": "Auriculares Inalámbricos Pro", "precio": 4200.00, "stock": 15},
    320: {"nombre": "Mouse Ergonómico Vertical", "precio": 2800.00, "stock": 42},
}

ENVIOS: dict[int, dict] = {
    1001: {"estado": "Entregado", "fecha_estimada": "2026-08-10"},
    1003: {"estado": "En camino", "fecha_estimada": "2026-08-18"},
    1004: {"estado": "Procesando", "fecha_estimada": "2026-08-22"},
}


# --- Herramientas con @tool ---

@tool
def buscar_pedidos(cliente_id: int) -> str:
    """
    Busca la información de pedidos de un cliente en la base de datos
    del sistema de gestión comercial.

    Usa esta herramienta cuando el usuario pregunte sobre:
    - Cuántos pedidos tiene o ha realizado un cliente específico.
    - El monto total acumulado de compras de un cliente.
    - El último pedido o producto adquirido por un cliente.

    Args:
        cliente_id: Identificador numérico único del cliente (ej: 101, 102, 103).

    Returns:
        Información del cliente con cantidad de pedidos, total facturado,
        ID del último pedido e ID del último producto comprado.
        Si el cliente no existe, retorna un mensaje de error descriptivo.
    """
    datos = CLIENTES_PEDIDOS.get(cliente_id)
    if datos is None:
        return (
            f"Error: No se encontró el cliente con ID {cliente_id}. "
            f"Clientes disponibles: {list(CLIENTES_PEDIDOS.keys())}. "
            f"Verifica el ID e intenta nuevamente."
        )
    return (
        f"Cliente {cliente_id}: {datos['pedidos']} pedidos, "
        f"total facturado ${datos['total']:,}, "
        f"último pedido ID #{datos['ultimo_pedido_id']}, "
        f"último producto ID #{datos['ultimo_producto_id']}."
    )


@tool
def consultar_producto(producto_id: int) -> str:
    """
    Consulta los detalles de un producto específico en el catálogo
    de la tienda (nombre, precio y stock disponible).

    Usa esta herramienta cuando el usuario pregunte sobre:
    - El nombre, precio o disponibilidad de un producto.
    - Detalles de un producto a partir de su ID.
    - Si un producto está en stock.

    Args:
        producto_id: Identificador numérico único del producto (ej: 301, 305, 310).

    Returns:
        Nombre del producto, precio unitario y cantidad en stock.
        Si el producto no existe, retorna un mensaje de error con los IDs válidos.
    """
    datos = PRODUCTOS.get(producto_id)
    if datos is None:
        return (
            f"Error: No se encontró el producto con ID {producto_id}. "
            f"Productos disponibles: {list(PRODUCTOS.keys())}. "
            f"Verifica el ID e intenta nuevamente."
        )
    return (
        f"Producto #{producto_id}: '{datos['nombre']}', "
        f"precio ${datos['precio']:,.2f}, "
        f"stock disponible: {datos['stock']} unidades."
    )


@tool
def verificar_estado_envio(pedido_id: int) -> str:
    """
    Verifica el estado logístico de un envío asociado a un pedido
    específico (estado actual y fecha estimada de entrega).

    Usa esta herramienta cuando el usuario pregunte sobre:
    - El estado de un envío o despacho.
    - Si un pedido ya fue entregado o está en tránsito.
    - La fecha estimada de entrega de un pedido.

    Args:
        pedido_id: Identificador numérico del pedido (ej: 1001, 1003, 1004).

    Returns:
        Estado del envío y fecha estimada de entrega.
        Si el pedido no existe, retorna un mensaje de error con los IDs válidos.
    """
    datos = ENVIOS.get(pedido_id)
    if datos is None:
        return (
            f"Error: No se encontró envío para el pedido #{pedido_id}. "
            f"Pedidos con envío registrado: {list(ENVIOS.keys())}. "
            f"Verifica el ID e intenta nuevamente."
        )
    return (
        f"Envío del pedido #{pedido_id}: estado '{datos['estado']}', "
        f"fecha estimada de entrega: {datos['fecha_estimada']}."
    )


# Lista exportable de herramientas para bind_tools y ToolNode
tools_list = [buscar_pedidos, consultar_producto, verificar_estado_envio]
