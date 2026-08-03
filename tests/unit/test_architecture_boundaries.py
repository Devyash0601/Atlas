"""Automated AST-based Clean Architecture boundary enforcement test.

Verifies that domain layer modules in src/domain NEVER import forbidden infrastructure,
web framework, database, or external AI/geospatial SDK dependencies.
"""

import ast
from pathlib import Path

FORBIDDEN_DOMAIN_IMPORTS = {
    "fastapi",
    "sqlalchemy",
    "redis",
    "qdrant_client",
    "ollama",
    "ee",
    "requests",
    "httpx",
    "pydantic",
    "src.infrastructure",
    "infrastructure",
}


def test_domain_layer_has_zero_forbidden_imports() -> None:
    """Scan all Python modules in src/domain/ to enforce inward dependency rules."""
    domain_dir = Path("src/domain")
    assert domain_dir.exists(), "src/domain directory must exist"

    violations: list[str] = []

    for file_path in domain_dir.rglob("*.py"):
        code = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(code, filename=str(file_path))
        except SyntaxError as e:
            violations.append(f"Syntax error in {file_path}: {e}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if alias.name in FORBIDDEN_DOMAIN_IMPORTS or mod in FORBIDDEN_DOMAIN_IMPORTS:
                        msg = f"{file_path}:{node.lineno} imports forbidden '{alias.name}'"
                        violations.append(msg)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split(".")[0]
                    if node.module in FORBIDDEN_DOMAIN_IMPORTS or mod in FORBIDDEN_DOMAIN_IMPORTS:
                        msg = f"{file_path}:{node.lineno} imports forbidden from '{node.module}'"
                        violations.append(msg)

    err_msg = "Architecture Boundary Violations found in Domain layer:\n" + "\n".join(violations)
    assert not violations, err_msg
