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
            import yaml
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
                import tomli as tomllib
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
        import yaml

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


class ConfigValidationError(ValueError):
    """Raised when a config dict fails schema validation."""


# Schema describing the keys the CLI understands. Each entry maps a config key
# to a validator: ("type", ...) for type checks, ("choice", {...}) for enums,
# ("range", lo, hi) for numeric bounds. Keys not in the schema are reported as
# unknown so mis-typed config keys surface immediately instead of silently
# being ignored by ``_apply_config``.
CONFIG_SCHEMA: dict[str, tuple] = {
    "symbols": ("type", (list, tuple)),
    "start": ("type", str),
    "start_date": ("type", str),
    "end": ("type", str),
    "end_date": ("type", str),
    "freq": ("type", str),
    "frequency": ("type", str),
    "data_source": ("choice", {"binance", "csv", "synthetic"}),
    "dataSource": ("choice", {"binance", "csv", "synthetic"}),
    "data_csv": ("type", str),
    "data_path": ("type", str),
    "price_csv": ("type", str),
    "strategy": ("choice", {"mean_reversion", "pairs", "term_structure"}),
    "asset": ("type", str),
    "pair": ("type", (list, tuple)),
    "pairs": ("type", (list, tuple)),
    "initial_capital": ("range", 0.0, float("inf")),
    "initialCapital": ("range", 0.0, float("inf")),
    "capital": ("range", 0.0, float("inf")),
    "fee_rate": ("range", 0.0, 1.0),
    "feeRate": ("range", 0.0, 1.0),
    "fee": ("range", 0.0, 1.0),
    "slippage": ("range", 0.0, 1.0),
    "output": ("choice", {"text", "json", "html", "pdf"}),
    "format": ("choice", {"text", "json", "html", "pdf"}),
    "report": ("choice", {"full", "risk"}),
    "report_type": ("choice", {"full", "risk"}),
    "output_path": ("type", str),
    "outputPath": ("type", str),
    "output_file": ("type", str),
    "artifact_dir": ("type", str),
    "artifactDir": ("type", str),
    "artifact_directory": ("type", str),
    "rebalance_frequency": ("type", str),
    "rebalance_freq": ("type", str),
    "rebal_freq": ("type", str),
    "rebalance_offset": ("type", str),
    "offset": ("type", str),
    "volume_csv": ("type", str),
    "volume": ("type", str),
    "volume_path": ("type", str),
    "high_csv": ("type", str),
    "high": ("type", str),
    "high_path": ("type", str),
    "low_csv": ("type", str),
    "low": ("type", str),
    "low_path": ("type", str),
    "benchmark_weights_csv": ("type", str),
    "benchmark_weights": ("type", str),
    "benchmark_weights_path": ("type", str),
    "factor_returns_csv": ("type", str),
    "factor_returns": ("type", str),
    "factor_returns_path": ("type", str),
    "execution_simulator": ("type", bool),
    "use_execution_simulator": ("type", bool),
    "order_type": ("choice", {"market", "limit", "vwap", "twap", "iceberg", "lob"}),
    "participation_rate": ("range", 0.0, 1.0),
    "slippage_bps": ("range", 0.0, 10_000.0),
    "regime_mode": ("type", str),
    "regimeMode": ("type", str),
    "regime_lookback": ("range", 1, float("inf")),
    "regimeLookback": ("range", 1, float("inf")),
    "regime_vol_mode": ("type", str),
    "regimeVolMode": ("type", str),
    "benchmark": ("type", bool),
    "rebalance_benchmark": ("type", bool),
    "rebalanceBenchmark": ("type", bool),
    "walk_forward": ("type", bool),
    "walk_forward_report": ("type", bool),
    "walkForwardReport": ("type", bool),
    "train_period": ("range", 1, float("inf")),
    "trainPeriod": ("range", 1, float("inf")),
    "test_period": ("range", 1, float("inf")),
    "testPeriod": ("range", 1, float("inf")),
    "reoptimize": ("type", bool),
    "reOptimize": ("type", bool),
    "reoptimize_portfolio": ("type", bool),
    "optimizer": ("type", str),
    "opt": ("type", str),
    "optimization": ("type", str),
    "optimizer_name": ("type", str),
    "title": ("type", str),
    "near_tenor": ("type", str),
    "far_tenor": ("type", str),
    "lookback": ("range", 1, float("inf")),
    "entry_threshold": ("range", 0.0, float("inf")),
    "exit_threshold": ("range", 0.0, float("inf")),
}


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate a loaded config dict against the CLI schema.

    Args:
        config: Parsed config dict (as returned by :func:`load_config`).

    Returns:
        The validated config dict (unchanged).

    Raises:
        ConfigValidationError: When a key is unknown, has the wrong type,
            violates a numeric range, or is not one of the allowed choices.
    """
    if not isinstance(config, dict):
        raise ConfigValidationError("Config must be a mapping")

    errors: list[str] = []
    for key, value in config.items():
        if key not in CONFIG_SCHEMA:
            errors.append(f"Unknown config key: {key!r}")
            continue
        spec = CONFIG_SCHEMA[key]
        kind = spec[0]
        if kind == "type":
            expected = spec[1]
            if not isinstance(value, expected):
                errors.append(
                    f"Config field '{key}' must be {getattr(expected, '__name__', expected)}, "
                    f"got {type(value).__name__}"
                )
        elif kind == "choice":
            allowed = spec[1]
            if value not in allowed:
                errors.append(
                    f"Config field '{key}' must be one of {sorted(allowed)}, got {value!r}"
                )
        elif kind == "range":
            lo, hi = spec[1], spec[2]
            if isinstance(value, bool):
                errors.append(
                    f"Config field '{key}' must be numeric, got {type(value).__name__}"
                )
                continue
            try:
                v = float(value)
            except (TypeError, ValueError):
                errors.append(f"Config field '{key}' must be numeric")
                continue
            if not (lo <= v <= hi):
                errors.append(
                    f"Config field '{key}' must be in [{lo}, {hi}], got {v}"
                )

    if errors:
        raise ConfigValidationError("Invalid config:\n  - " + "\n  - ".join(errors))
    return config
