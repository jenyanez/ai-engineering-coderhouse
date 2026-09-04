"""Auditoría estática de sintaxis AST para garantizar cero llamadas bloqueantes."""

import ast
import os
import pytest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app"))


def get_all_python_files(directory: str):
    py_files = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files


def test_no_synchronous_requests_library():
    """Valida que ningún archivo del proyecto use 'requests' síncrono."""
    py_files = get_all_python_files(APP_DIR)
    for fpath in py_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=fpath)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "requests", f"Violación sync: 'requests' importado en {fpath}"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "requests", f"Violación sync: 'requests' importado en {fpath}"


def test_no_time_sleep_in_async_routines():
    """Valida que ninguna función async def contenga time.sleep bloqueante."""
    py_files = get_all_python_files(APP_DIR)
    for fpath in py_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=fpath)
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call):
                        func = subnode.func
                        if isinstance(func, ast.Attribute) and func.attr == "sleep":
                            if isinstance(func.value, ast.Name) and func.value.id == "time":
                                pytest.fail(f"Bloqueo de Event Loop: time.sleep en async def en {fpath}")
