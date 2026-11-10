"""Secret-free environment variable templates."""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from pathlib import Path


@dataclass
class EnvVarSpec:
    """Specification for an environment variable."""

    name: str
    description: str
    required: bool = True
    default: Optional[str] = None
    sensitive: bool = True
    example: Optional[str] = None


@dataclass
class SecretFreeEnvTemplate:
    """Secret-free environment template with variable specifications."""

    variables: List[EnvVarSpec] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def add_variable(self, spec: EnvVarSpec) -> "SecretFreeEnvTemplate":
        """Add a variable specification."""
        self.variables.append(spec)
        return self

    def get_required(self) -> List[EnvVarSpec]:
        """Get required variables."""
        return [v for v in self.variables if v.required]

    def get_optional(self) -> List[EnvVarSpec]:
        """Get optional variables."""
        return [v for v in self.variables if not v.required]

    def get_names(self) -> Set[str]:
        """Get all variable names."""
        return {v.name for v in self.variables}

    def render(self, values: Optional[Dict[str, str]] = None) -> str:
        """Render template as .env file content (with placeholders for secrets)."""
        lines = []

        if self.metadata:
            lines.append("# Environment Configuration Template")
            lines.append(f"# Generated: {self.metadata.get('generated_at', 'unknown')}")
            lines.append(f"# Environment: {self.metadata.get('environment', 'unknown')}")
            lines.append("")

        for var in self.variables:
            lines.append(f"# {var.description}")
            if var.example:
                lines.append(f"# Example: {var.example}")
            if var.sensitive:
                lines.append(f"# ⚠️  SECRET - Never commit actual values")
            else:
                lines.append(f"# Non-sensitive")
            if var.required:
                lines.append(f"{var.name}=")
            else:
                default_val = values.get(var.name, var.default) if values else var.default
                lines.append(f"{var.name}={default_val or ''}")
            lines.append("")

        return "\n".join(lines)

    def validate_present(self, env: Optional[Dict[str, str]] = None) -> Dict[str, List[str]]:
        """Validate which required variables are present/missing."""
        env = env or os.environ
        present = []
        missing = []

        for var in self.get_required():
            if var.name in env and env[var.name]:
                present.append(var.name)
            else:
                missing.append(var.name)

        return {"present": present, "missing": missing}

    def write_to_file(self, path: str, values: Optional[Dict[str, str]] = None) -> None:
        """Write rendered template to file."""
        Path(path).write_text(self.render(values))

    @classmethod
    def from_config(cls, config_type: str) -> "SecretFreeEnvTemplate":
        """Create template from predefined configuration type."""
        template = cls()

        if config_type == "exchange":
            template.metadata = {"generated_at": "auto", "environment": "all"}
            template.add_variable(
                EnvVarSpec(
                    name="BINANCE_API_KEY",
                    description="Binance API Key (spot/futures)",
                    required=True,
                    sensitive=True,
                    example="your_api_key_here",
                )
            )
            template.add_variable(
                EnvVarSpec(
                    name="BINANCE_API_SECRET",
                    description="Binance API Secret",
                    required=True,
                    sensitive=True,
                    example="your_api_secret_here",
                )
            )

        elif config_type == "observability":
            template.metadata = {"generated_at": "auto", "environment": "all"}
            template.add_variable(
                EnvVarSpec(
                    name="LOG_LEVEL",
                    description="Structured log level",
                    required=False,
                    default="INFO",
                    sensitive=False,
                    example="DEBUG",
                )
            )
            template.add_variable(
                EnvVarSpec(
                    name="METRICS_PORT",
                    description="Prometheus metrics HTTP port",
                    required=False,
                    default="9090",
                    sensitive=False,
                    example="9090",
                )
            )
            template.add_variable(
                EnvVarSpec(
                    name="HEALTH_CHECK_PORT",
                    description="Health check HTTP port",
                    required=False,
                    default="8080",
                    sensitive=False,
                    example="8080",
                )
            )

        elif config_type == "alerts":
            template.metadata = {"generated_at": "auto", "environment": "staging,production"}
            template.add_variable(
                EnvVarSpec(
                    name="ALERT_WEBHOOK_URL",
                    description="Alert webhook URL (Slack, PagerDuty, etc.)",
                    required=False,
                    sensitive=True,
                    example="https://hooks.slack.com/services/...",
                )
            )
            template.add_variable(
                EnvVarSpec(
                    name="ALERT_SEVERITY_THRESHOLD",
                    description="Minimum severity for alerts",
                    required=False,
                    default="WARNING",
                    sensitive=False,
                    example="ERROR",
                )
            )

        elif config_type == "data":
            template.metadata = {"generated_at": "auto", "environment": "all"}
            template.add_variable(
                EnvVarSpec(
                    name="DATA_CACHE_DIR",
                    description="Directory for cached market data",
                    required=False,
                    default="./data/cache",
                    sensitive=False,
                    example="/var/lib/cryptoquant/cache",
                )
            )
            template.add_variable(
                EnvVarSpec(
                    name="BINANCE_BASE_URL",
                    description="Binance API base URL override",
                    required=False,
                    default="https://api.binance.com",
                    sensitive=False,
                    example="https://testnet.binance.vision",
                )
            )

        elif config_type == "full":
            template.metadata = {"generated_at": "auto", "environment": "all"}
            # Exchange
            template.add_variable(
                EnvVarSpec(
                    name="BINANCE_API_KEY",
                    description="Binance API Key (spot/futures)",
                    required=True,
                    sensitive=True,
                    example="your_api_key_here",
                )
            )
            template.add_variable(
                EnvVarSpec(
                    name="BINANCE_API_SECRET",
                    description="Binance API Secret",
                    required=True,
                    sensitive=True,
                    example="your_api_secret_here",
                )
            )
            # Observability
            template.add_variable(
                EnvVarSpec(
                    name="LOG_LEVEL",
                    description="Structured log level",
                    required=False,
                    default="INFO",
                    sensitive=False,
                    example="DEBUG",
                )
            )
            template.add_variable(
                EnvVarSpec(
                    name="METRICS_PORT",
                    description="Prometheus metrics HTTP port",
                    required=False,
                    default="9090",
                    sensitive=False,
                    example="9090",
                )
            )
            template.add_variable(
                EnvVarSpec(
                    name="HEALTH_CHECK_PORT",
                    description="Health check HTTP port",
                    required=False,
                    default="8080",
                    sensitive=False,
                    example="8080",
                )
            )
            # Alerts
            template.add_variable(
                EnvVarSpec(
                    name="ALERT_WEBHOOK_URL",
                    description="Alert webhook URL (Slack, PagerDuty, etc.)",
                    required=False,
                    sensitive=True,
                    example="https://hooks.slack.com/services/...",
                )
            )
            # Data
            template.add_variable(
                EnvVarSpec(
                    name="DATA_CACHE_DIR",
                    description="Directory for cached market data",
                    required=False,
                    default="./data/cache",
                    sensitive=False,
                    example="/var/lib/cryptoquant/cache",
                )
            )
            template.add_variable(
                EnvVarSpec(
                    name="BINANCE_BASE_URL",
                    description="Binance API base URL override",
                    required=False,
                    default="https://api.binance.com",
                    sensitive=False,
                    example="https://testnet.binance.vision",
                )
            )
            # State
            template.add_variable(
                EnvVarSpec(
                    name="STATE_PERSISTENCE_PATH",
                    description="Path for operational state persistence",
                    required=False,
                    default="/tmp/cryptoquant_state.json",
                    sensitive=False,
                    example="/var/lib/cryptoquant/prod_state.json",
                )
            )

        return template


DEFAULT_TEMPLATE = SecretFreeEnvTemplate.from_config("full")


def load_env_template(path: str) -> SecretFreeEnvTemplate:
    """Load environment template from .env.example file."""
    content = Path(path).read_text()
    template = SecretFreeEnvTemplate()

    current_desc = ""
    current_example = None
    current_required = True
    current_sensitive = True

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("#"):
            # Comment - could be description or example
            comment = line[1:].strip()
            if comment.startswith("Example:"):
                current_example = comment[8:].strip()
            elif comment.startswith("⚠️"):
                current_sensitive = True
            elif "Non-sensitive" in comment:
                current_sensitive = False
            else:
                current_desc = comment
        elif "=" in line:
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip()

            required = not value or value == ""
            template.add_variable(
                EnvVarSpec(
                    name=name,
                    description=current_desc or name,
                    required=required,
                    default=value if not required else None,
                    sensitive=current_sensitive,
                    example=current_example,
                )
            )
            current_desc = ""
            current_example = None
            current_required = True
            current_sensitive = True

    return template


def render_env_template(template: SecretFreeEnvTemplate, values: Optional[Dict[str, str]] = None) -> str:
    """Render environment template with optional values."""
    return template.render(values)