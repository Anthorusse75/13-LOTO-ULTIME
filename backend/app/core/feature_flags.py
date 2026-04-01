"""Feature flags — toggleable features controlled via environment variables.

Usage:
    from app.core.feature_flags import feature_flags

    if feature_flags.WHEELING_ENABLED:
        ...  # feature is active

All flags default to True (enabled). Set the environment variable to "false"
or "0" to disable a feature without redeploying code.

    export FEATURE_WHEELING_ENABLED=false
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class FeatureFlags(BaseSettings):
    """Feature toggles loaded from environment variables."""

    # Phase C features
    WHEELING_ENABLED: bool = Field(True, alias="FEATURE_WHEELING_ENABLED")
    BUDGET_OPTIMIZER_ENABLED: bool = Field(True, alias="FEATURE_BUDGET_OPTIMIZER_ENABLED")

    # Phase D features
    COMPARATOR_ENABLED: bool = Field(True, alias="FEATURE_COMPARATOR_ENABLED")
    SIMULATION_ENABLED: bool = Field(True, alias="FEATURE_SIMULATION_ENABLED")
    FAVORITES_ENABLED: bool = Field(True, alias="FEATURE_FAVORITES_ENABLED")

    # Phase E features
    EXPORT_PDF_ENABLED: bool = Field(True, alias="FEATURE_EXPORT_PDF_ENABLED")
    LIGHT_THEME_ENABLED: bool = Field(True, alias="FEATURE_LIGHT_THEME_ENABLED")
    ONBOARDING_TOUR_ENABLED: bool = Field(True, alias="FEATURE_ONBOARDING_TOUR_ENABLED")

    # Infra features
    SCHEDULER_NIGHTLY_ENABLED: bool = Field(True, alias="FEATURE_SCHEDULER_NIGHTLY_ENABLED")
    LLM_INSIGHTS_ENABLED: bool = Field(True, alias="FEATURE_LLM_INSIGHTS_ENABLED")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


feature_flags = FeatureFlags()
