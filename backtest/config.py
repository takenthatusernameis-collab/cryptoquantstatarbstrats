"""
Configuration loading for backtest runs.

Supports YAML and TOML configuration files. Falls back gracefully if PyYAML
or tomllib are not available for a given format.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load configuration from a file (YAML or TOML)."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = path.suffix.lower()
    text = path.read_text()

    if suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover - env dependent
            raise ImportError("PyYAML is required to load YAML config files") from exc
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise ValueError("YAML config must be a mapping")
        return data

    if suffix == ".toml":
        try:
            import tomllib  # Python 3.11+
        except Exception:
            try:
                import tomli as tomllib  # type: ignore
            except Exception as exc:  # pragma: no cover - env dependent
                raise ImportError("tomllib/tomli is required to load TOML config files") from exc
        data = tomllib.loads(text)
        if not isinstance(data, dict):
            raise ValueError("TOML config must be a mapping")
        return data

    if suffix == ".json":
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("JSON config must be a mapping")
        return data

    # Try YAML first, then JSON as a fallback.
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    raise ValueError(f"Unsupported config format: {suffix}")
