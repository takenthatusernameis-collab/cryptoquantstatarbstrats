"""Configuration profiles for dev/staging/prod environments."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from .schemas import (
    ConfigSchema,
    Environment,
    validate_config,
    load_config_file,
    ExchangeConfigSchema,
    RiskConfigSchema,
    ObservabilityConfigSchema,
    ReconciliationConfigSchema,
    PlaybookConfigSchema,
)


class ConfigProfile:
    """Configuration profile for a specific environment."""

    def __init__(self, environment: Environment, config: ConfigSchema):
        self.environment = environment
        self.config = config

    @classmethod
    def development(cls) -> "ConfigProfile":
        """Create development profile with safe defaults."""
        return cls(
            Environment.DEVELOPMENT,
            ConfigSchema(
                environment=Environment.DEVELOPMENT,
                risk=RiskConfigSchema(
                    max_gross_exposure=2.0,
                    max_position_size=0.5,
                    max_drawdown_pct=10.0,
                    var_confidence=0.95,
                    cvar_confidence=0.99,
                    correlation_exposure_cap=0.5,
                    kill_switch_enabled=True,
                ),
                exchanges=[
                    ExchangeConfigSchema(
                        name="binance",
                        api_key_env="BINANCE_API_KEY",
                        api_secret_env="BINANCE_API_SECRET",
                        testnet=True,
                        rate_limit=1200,
                        timeout_seconds=30,
                    )
                ],
                observability=ObservabilityConfigSchema(
                    log_level="DEBUG",
                    log_format="json",
                    log_output="stdout",
                    metrics_enabled=True,
                    metrics_format="prometheus",
                    metrics_port=9090,
                    metrics_path="/metrics",
                    health_check_enabled=True,
                    health_check_port=8080,
                    health_check_liveness_path="/health/live",
                    health_check_readiness_path="/health/ready",
                    trace_sampling_rate=1.0,
                ),
                reconciliation=ReconciliationConfigSchema(
                    enabled=True,
                    position_tolerance=1e-6,
                    cash_tolerance=1e-2,
                    equity_tolerance=1e-4,
                    fill_audit_enabled=True,
                    lifecycle_audit_enabled=True,
                    reconciliation_interval_seconds=10,
                ),
                playbooks=PlaybookConfigSchema(
                    preflight_enabled=True,
                    preflight_checks=[
                        "network_reachability",
                        "credential_presence",
                        "risk_config_validation",
                        "exchange_capability_probe",
                        "data_feed_validation",
                    ],
                    state_persistence_path="/tmp/cryptoquant_dev_state.json",
                    incident_response_enabled=True,
                    kill_switch_grace_seconds=10,
                    position_flatten_timeout_seconds=60,
                    alert_webhook_url_env=None,
                    dry_run_validation_enabled=True,
                ),
            ),
        )

    @classmethod
    def staging(cls) -> "ConfigProfile":
        """Create staging profile with production-like settings."""
        return cls(
            Environment.STAGING,
            ConfigSchema(
                environment=Environment.STAGING,
                risk=RiskConfigSchema(
                    max_gross_exposure=1.5,
                    max_position_size=0.3,
                    max_drawdown_pct=5.0,
                    var_confidence=0.95,
                    cvar_confidence=0.99,
                    correlation_exposure_cap=0.4,
                    kill_switch_enabled=True,
                ),
                exchanges=[
                    ExchangeConfigSchema(
                        name="binance",
                        api_key_env="BINANCE_API_KEY",
                        api_secret_env="BINANCE_API_SECRET",
                        testnet=True,
                        rate_limit=1200,
                        timeout_seconds=30,
                    )
                ],
                observability=ObservabilityConfigSchema(
                    log_level="INFO",
                    log_format="json",
                    log_output="stdout",
                    metrics_enabled=True,
                    metrics_format="prometheus",
                    metrics_port=9090,
                    metrics_path="/metrics",
                    health_check_enabled=True,
                    health_check_port=8080,
                    health_check_liveness_path="/health/live",
                    health_check_readiness_path="/health/ready",
                    trace_sampling_rate=0.5,
                ),
                reconciliation=ReconciliationConfigSchema(
                    enabled=True,
                    position_tolerance=1e-8,
                    cash_tolerance=1e-4,
                    equity_tolerance=1e-6,
                    fill_audit_enabled=True,
                    lifecycle_audit_enabled=True,
                    reconciliation_interval_seconds=30,
                ),
                playbooks=PlaybookConfigSchema(
                    preflight_enabled=True,
                    preflight_checks=[
                        "network_reachability",
                        "credential_presence",
                        "risk_config_validation",
                        "exchange_capability_probe",
                        "data_feed_validation",
                    ],
                    state_persistence_path="/var/lib/cryptoquant/staging_state.json",
                    incident_response_enabled=True,
                    kill_switch_grace_seconds=20,
                    position_flatten_timeout_seconds=120,
                    alert_webhook_url_env="ALERT_WEBHOOK_URL",
                    dry_run_validation_enabled=True,
                ),
            ),
        )

    @classmethod
    def production(cls) -> "ConfigProfile":
        """Create production profile with strict settings."""
        return cls(
            Environment.PRODUCTION,
            ConfigSchema(
                environment=Environment.PRODUCTION,
                risk=RiskConfigSchema(
                    max_gross_exposure=1.4,
                    max_position_size=0.25,
                    max_drawdown_pct=3.0,
                    var_confidence=0.99,
                    cvar_confidence=0.995,
                    correlation_exposure_cap=0.3,
                    kill_switch_enabled=True,
                ),
                exchanges=[
                    ExchangeConfigSchema(
                        name="binance",
                        api_key_env="BINANCE_API_KEY",
                        api_secret_env="BINANCE_API_SECRET",
                        testnet=False,
                        rate_limit=1200,
                        timeout_seconds=10,
                    )
                ],
                observability=ObservabilityConfigSchema(
                    log_level="WARNING",
                    log_format="json",
                    log_output="stdout",
                    metrics_enabled=True,
                    metrics_format="prometheus",
                    metrics_port=9090,
                    metrics_path="/metrics",
                    health_check_enabled=True,
                    health_check_port=8080,
                    health_check_liveness_path="/health/live",
                    health_check_readiness_path="/health/ready",
                    trace_sampling_rate=0.1,
                ),
                reconciliation=ReconciliationConfigSchema(
                    enabled=True,
                    position_tolerance=1e-10,
                    cash_tolerance=1e-6,
                    equity_tolerance=1e-8,
                    fill_audit_enabled=True,
                    lifecycle_audit_enabled=True,
                    reconciliation_interval_seconds=60,
                ),
                playbooks=PlaybookConfigSchema(
                    preflight_enabled=True,
                    preflight_checks=[
                        "network_reachability",
                        "credential_presence",
                        "risk_config_validation",
                        "exchange_capability_probe",
                        "data_feed_validation",
                    ],
                    state_persistence_path="/var/lib/cryptoquant/prod_state.json",
                    incident_response_enabled=True,
                    kill_switch_grace_seconds=30,
                    position_flatten_timeout_seconds=300,
                    alert_webhook_url_env="ALERT_WEBHOOK_URL",
                    dry_run_validation_enabled=True,
                ),
            ),
        )

    @classmethod
    def from_file(cls, path: str, environment: Optional[Environment] = None) -> "ConfigProfile":
        """Load profile from configuration file."""
        config_dict = load_config_file(path)
        if environment:
            config_dict["environment"] = environment.value
        validated = validate_config(config_dict)
        return cls(validated.environment, validated)

    @classmethod
    def from_env(cls, env_var: str = "CRYPTOQUANT_ENV") -> "ConfigProfile":
        """Load profile from environment variable."""
        env_value = os.getenv(env_var, "development").lower()
        try:
            environment = Environment(env_value)
        except ValueError:
            environment = Environment.DEVELOPMENT

        if environment == Environment.DEVELOPMENT:
            return cls.development()
        elif environment == Environment.STAGING:
            return cls.staging()
        else:
            return cls.production()


def load_config(profile: Optional[str] = None, config_file: Optional[str] = None) -> ConfigSchema:
    """Load configuration from profile or file."""
    if config_file:
        return validate_config(load_config_file(config_file)).config

    if profile:
        if profile == "development":
            return ConfigProfile.development().config
        elif profile == "staging":
            return ConfigProfile.staging().config
        elif profile == "production":
            return ConfigProfile.production().config
        else:
            raise ValueError(f"Unknown profile: {profile}")

    return ConfigProfile.from_env().config


def get_profile(environment: Environment) -> ConfigProfile:
    """Get profile by environment."""
    if environment == Environment.DEVELOPMENT:
        return ConfigProfile.development()
    elif environment == Environment.STAGING:
        return ConfigProfile.staging()
    else:
        return ConfigProfile.production()


def detect_environment() -> Environment:
    """Detect environment from environment variables."""
    env = os.getenv("CRYPTOQUANT_ENV", "development").lower()
    try:
        return Environment(env)
    except ValueError:
        return Environment.DEVELOPMENT