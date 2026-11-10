"""Configuration schemas with strict validation using Pydantic."""

from enum import Enum
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class Environment(str, Enum):
    """Deployment environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class MetricsFormat(str, Enum):
    """Metrics output format."""

    PROMETHEUS = "prometheus"
    JSON = "json"


class HealthCheckType(str, Enum):
    """Health check types."""

    LIVENESS = "liveness"
    READINESS = "readiness"


class RiskConfigSchema(BaseModel):
    """Risk management configuration."""

    max_gross_exposure: float = Field(
        gt=0, le=10, description="Maximum gross exposure as multiple of capital"
    )
    max_position_size: float = Field(
        gt=0, le=1, description="Maximum position size as fraction of capital"
    )
    max_drawdown_pct: float = Field(
        gt=0, le=100, description="Maximum drawdown percentage before circuit breaker"
    )
    var_confidence: float = Field(gt=0, lt=1, description="VaR confidence level")
    cvar_confidence: float = Field(gt=0, lt=1, description="CVaR confidence level")
    correlation_exposure_cap: float = Field(
        gt=0, le=1, description="Correlation exposure cap"
    )
    kill_switch_enabled: bool = Field(default=True, description="Enable kill switch")


class ExchangeConfigSchema(BaseModel):
    """Exchange connection configuration."""

    name: str = Field(min_length=1, description="Exchange identifier")
    api_key_env: str = Field(
        min_length=1, description="Environment variable name for API key"
    )
    api_secret_env: str = Field(
        min_length=1, description="Environment variable name for API secret"
    )
    testnet: bool = Field(default=False, description="Use testnet/sandbox")
    base_url: Optional[str] = Field(
        default=None, description="Custom base URL override"
    )
    rate_limit: int = Field(gt=0, default=1200, description="Requests per minute")
    timeout_seconds: int = Field(gt=0, default=30, description="Request timeout")


class ObservabilityConfigSchema(BaseModel):
    """Observability configuration."""

    log_level: LogLevel = Field(
        default=LogLevel.INFO, description="Structured log level"
    )
    log_format: str = Field(default="json", description="Log format: json or text")
    log_output: str = Field(default="stdout", description="Log output destination")
    metrics_enabled: bool = Field(default=True, description="Enable metrics emission")
    metrics_format: MetricsFormat = Field(
        default=MetricsFormat.PROMETHEUS, description="Metrics format"
    )
    metrics_port: int = Field(
        gt=0, lt=65536, default=9090, description="Metrics HTTP port"
    )
    metrics_path: str = Field(default="/metrics", description="Metrics endpoint path")
    health_check_enabled: bool = Field(
        default=True, description="Enable health checks"
    )
    health_check_port: int = Field(
        gt=0, lt=65536, default=8080, description="Health check HTTP port"
    )
    health_check_liveness_path: str = Field(
        default="/health/live", description="Liveness endpoint path"
    )
    health_check_readiness_path: str = Field(
        default="/health/ready", description="Readiness endpoint path"
    )
    trace_sampling_rate: float = Field(
        ge=0, le=1, default=0.1, description="Distributed trace sampling rate"
    )


class ReconciliationConfigSchema(BaseModel):
    """Reconciliation configuration."""

    enabled: bool = Field(default=True, description="Enable reconciliation checks")
    position_tolerance: float = Field(
        gt=0, default=1e-6, description="Position reconciliation tolerance"
    )
    cash_tolerance: float = Field(
        gt=0, default=1e-2, description="Cash reconciliation tolerance"
    )
    equity_tolerance: float = Field(
        gt=0, default=1e-4, description="Equity reconciliation tolerance"
    )
    fill_audit_enabled: bool = Field(
        default=True, description="Enable fill audit trail"
    )
    lifecycle_audit_enabled: bool = Field(
        default=True, description="Enable order lifecycle state machine audit"
    )
    reconciliation_interval_seconds: int = Field(
        gt=0, default=60, description="Reconciliation check interval"
    )


class PlaybookConfigSchema(BaseModel):
    """Operational playbook configuration."""

    preflight_enabled: bool = Field(default=True, description="Enable preflight checks")
    preflight_checks: List[str] = Field(
        default_factory=lambda: [
            "network_reachability",
            "credential_presence",
            "risk_config_validation",
            "exchange_capability_probe",
            "data_feed_validation",
        ],
        description="Preflight check names",
    )
    state_persistence_path: str = Field(
        default="/tmp/cryptoquant_state.json", description="State persistence file"
    )
    incident_response_enabled: bool = Field(
        default=True, description="Enable incident response runbook"
    )
    kill_switch_grace_seconds: int = Field(
        gt=0, default=30, description="Grace period for kill switch"
    )
    position_flatten_timeout_seconds: int = Field(
        gt=0, default=300, description="Position flattening timeout"
    )
    alert_webhook_url_env: Optional[str] = Field(
        default=None, description="Env var for alert webhook URL"
    )
    dry_run_validation_enabled: bool = Field(
        default=True, description="Enable dry-run validation script"
    )


class ConfigSchema(BaseModel):
    """Top-level configuration schema."""

    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="Deployment environment"
    )
    risk: RiskConfigSchema = Field(default_factory=RiskConfigSchema)
    exchanges: List[ExchangeConfigSchema] = Field(default_factory=list, min_length=1)
    observability: ObservabilityConfigSchema = Field(default_factory=ObservabilityConfigSchema)
    reconciliation: ReconciliationConfigSchema = Field(default_factory=ReconciliationConfigSchema)
    playbooks: PlaybookConfigSchema = Field(default_factory=PlaybookConfigSchema)

    @field_validator("exchanges")
    @classmethod
    def validate_unique_exchanges(cls, v: List[ExchangeConfigSchema]) -> List[ExchangeConfigSchema]:
        names = [ex.name for ex in v]
        if len(names) != len(set(names)):
            raise ValueError("Exchange names must be unique")
        return v


def validate_config(config_dict: Dict[str, Any]) -> ConfigSchema:
    """Validate configuration dictionary against schema."""
    return ConfigSchema(**config_dict)


def load_yaml_config(path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def load_toml_config(path: str) -> Dict[str, Any]:
    """Load configuration from TOML file."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    with open(path, "rb") as f:
        return tomllib.load(f) or {}


def load_json_config(path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    import json
    with open(path, "r") as f:
        return json.load(f) or {}


def load_config_file(path: str) -> Dict[str, Any]:
    """Load configuration from file based on extension."""
    if path.endswith(".yaml") or path.endswith(".yml"):
        return load_yaml_config(path)
    elif path.endswith(".toml"):
        return load_toml_config(path)
    elif path.endswith(".json"):
        return load_json_config(path)
    else:
        raise ValueError(f"Unsupported config file format: {path}")
