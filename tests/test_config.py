"""Tests for config module."""

import os
import tempfile
from pathlib import Path

import pytest

from config import (
    load_config,
    ConfigProfile,
    Environment,
    validate_config,
    RiskConfigSchema,
    ExchangeConfigSchema,
    ObservabilityConfigSchema,
    ReconciliationConfigSchema,
    PlaybookConfigSchema,
)
from config.env import SecretFreeEnvTemplate, EnvVarSpec


class TestConfigSchemas:
    """Test configuration schemas."""

    def test_risk_config_schema_valid(self):
        """Test valid risk config."""
        config = RiskConfigSchema(
            max_gross_exposure=2.0,
            max_position_size=0.5,
            max_drawdown_pct=10.0,
            var_confidence=0.95,
            cvar_confidence=0.99,
            correlation_exposure_cap=0.5,
            kill_switch_enabled=True,
        )
        assert config.max_gross_exposure == 2.0

    def test_risk_config_schema_invalid_exposure(self):
        """Test invalid risk config - negative exposure."""
        with pytest.raises(Exception):
            RiskConfigSchema(
                max_gross_exposure=-1.0,
                max_position_size=0.5,
                max_drawdown_pct=10.0,
                var_confidence=0.95,
                cvar_confidence=0.99,
                correlation_exposure_cap=0.5,
            )

    def test_risk_config_schema_invalid_position_size(self):
        """Test invalid risk config - position size > 1."""
        with pytest.raises(Exception):
            RiskConfigSchema(
                max_gross_exposure=2.0,
                max_position_size=1.5,
                max_drawdown_pct=10.0,
                var_confidence=0.95,
                cvar_confidence=0.99,
                correlation_exposure_cap=0.5,
            )

    def test_exchange_config_schema(self):
        """Test exchange config schema."""
        config = ExchangeConfigSchema(
            name="binance",
            api_key_env="BINANCE_API_KEY",
            api_secret_env="BINANCE_API_SECRET",
            testnet=True,
        )
        assert config.name == "binance"
        assert config.testnet is True

    def test_observability_config_schema(self):
        """Test observability config schema."""
        config = ObservabilityConfigSchema(
            log_level="INFO",
            metrics_enabled=True,
            metrics_port=9090,
        )
        assert config.log_level == "INFO"
        assert config.metrics_port == 9090

    def test_reconciliation_config_schema(self):
        """Test reconciliation config schema."""
        config = ReconciliationConfigSchema(
            enabled=True,
            position_tolerance=1e-6,
            cash_tolerance=1e-2,
        )
        assert config.enabled is True
        assert config.position_tolerance == 1e-6

    def test_playbook_config_schema(self):
        """Test playbook config schema."""
        config = PlaybookConfigSchema(
            preflight_enabled=True,
            kill_switch_grace_seconds=30,
        )
        assert config.preflight_enabled is True
        assert config.kill_switch_grace_seconds == 30


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_config_valid(self):
        """Test validating a valid config."""
        config_dict = {
            "environment": "development",
            "risk": {
                "max_gross_exposure": 2.0,
                "max_position_size": 0.5,
                "max_drawdown_pct": 10.0,
                "var_confidence": 0.95,
                "cvar_confidence": 0.99,
                "correlation_exposure_cap": 0.5,
                "kill_switch_enabled": True,
            },
            "exchanges": [
                {
                    "name": "binance",
                    "api_key_env": "BINANCE_API_KEY",
                    "api_secret_env": "BINANCE_API_SECRET",
                    "testnet": True,
                }
            ],
            "observability": {},
            "reconciliation": {},
            "playbooks": {},
        }
        validated = validate_config(config_dict)
        assert validated.environment == Environment.DEVELOPMENT
        assert len(validated.exchanges) == 1

    def test_validate_config_duplicate_exchanges(self):
        """Test validation fails with duplicate exchange names."""
        config_dict = {
            "environment": "development",
            "risk": {
                "max_gross_exposure": 2.0,
                "max_position_size": 0.5,
                "max_drawdown_pct": 10.0,
                "var_confidence": 0.95,
                "cvar_confidence": 0.99,
                "correlation_exposure_cap": 0.5,
                "kill_switch_enabled": True,
            },
            "exchanges": [
                {
                    "name": "binance",
                    "api_key_env": "BINANCE_API_KEY",
                    "api_secret_env": "BINANCE_API_SECRET",
                },
                {
                    "name": "binance",
                    "api_key_env": "BINANCE_API_KEY_2",
                    "api_secret_env": "BINANCE_API_SECRET_2",
                },
            ],
        }
        with pytest.raises(Exception):
            validate_config(config_dict)


class TestConfigProfiles:
    """Test configuration profiles."""

    def test_development_profile(self):
        """Test development profile."""
        profile = ConfigProfile.development()
        assert profile.environment == Environment.DEVELOPMENT
        assert profile.config.risk.max_gross_exposure == 2.0
        assert profile.config.exchanges[0].testnet is True

    def test_staging_profile(self):
        """Test staging profile."""
        profile = ConfigProfile.staging()
        assert profile.environment == Environment.STAGING
        assert profile.config.risk.max_gross_exposure == 1.5
        assert profile.config.exchanges[0].testnet is True

    def test_production_profile(self):
        """Test production profile."""
        profile = ConfigProfile.production()
        assert profile.environment == Environment.PRODUCTION
        assert profile.config.risk.max_gross_exposure == 1.4
        assert profile.config.exchanges[0].testnet is False

    def test_load_config_from_env(self, monkeypatch):
        """Test loading config from environment variable."""
        monkeypatch.setenv("CRYPTOQUANT_ENV", "staging")
        config = load_config()
        assert config.environment == Environment.STAGING

    def test_load_config_from_file(self):
        """Test loading config from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
environment: production
risk:
  max_gross_exposure: 1.4
  max_position_size: 0.25
  max_drawdown_pct: 3.0
  var_confidence: 0.99
  cvar_confidence: 0.995
  correlation_exposure_cap: 0.3
  kill_switch_enabled: true
exchanges:
  - name: binance
    api_key_env: BINANCE_API_KEY
    api_secret_env: BINANCE_API_SECRET
    testnet: false
observability: {}
reconciliation: {}
playbooks: {}
""")
            f.flush()
            try:
                config = load_config(config_file=f.name)
                assert config.environment == Environment.PRODUCTION
                assert config.risk.max_gross_exposure == 1.4
            finally:
                os.unlink(f.name)


class TestSecretFreeEnvTemplate:
    """Test secret-free environment templates."""

    def test_env_template_creation(self):
        """Test creating env template."""
        template = SecretFreeEnvTemplate()
        template.add_variable(EnvVarSpec(
            name="TEST_VAR",
            description="Test variable",
            required=True,
            sensitive=True,
        ))
        assert "TEST_VAR" in template.get_names()

    def test_env_template_render(self):
        """Test rendering env template."""
        template = SecretFreeEnvTemplate()
        template.add_variable(EnvVarSpec(
            name="REQUIRED_VAR",
            description="Required variable",
            required=True,
            sensitive=True,
        ))
        template.add_variable(EnvVarSpec(
            name="OPTIONAL_VAR",
            description="Optional variable",
            required=False,
            default="default_value",
            sensitive=False,
        ))
        rendered = template.render()
        assert "REQUIRED_VAR=" in rendered
        assert "OPTIONAL_VAR=default_value" in rendered

    def test_env_template_validate_present(self, monkeypatch):
        """Test validating present variables."""
        monkeypatch.setenv("PRESENT_VAR", "value")
        template = SecretFreeEnvTemplate()
        template.add_variable(EnvVarSpec(
            name="PRESENT_VAR",
            description="Present variable",
            required=True,
        ))
        template.add_variable(EnvVarSpec(
            name="MISSING_VAR",
            description="Missing variable",
            required=True,
        ))
        result = template.validate_present()
        assert "PRESENT_VAR" in result["present"]
        assert "MISSING_VAR" in result["missing"]

    def test_predefined_templates(self):
        """Test predefined templates."""
        exchange_template = SecretFreeEnvTemplate.from_config("exchange")
        assert "BINANCE_API_KEY" in exchange_template.get_names()
        assert "BINANCE_API_SECRET" in exchange_template.get_names()

        full_template = SecretFreeEnvTemplate.from_config("full")
        assert "BINANCE_API_KEY" in full_template.get_names()
        assert "LOG_LEVEL" in full_template.get_names()
        assert "ALERT_WEBHOOK_URL" in full_template.get_names()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])