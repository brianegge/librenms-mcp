from pydantic import BaseModel
from pydantic import Field


class LibreNMSConfig(BaseModel):
    librenms_url: str = Field(
        ..., description="LibreNMS base URL, e.g. https://domain.tld:8443"
    )
    token: str = Field(..., description="LibreNMS API token")
    verify_ssl: bool = Field(True, description="Verify SSL (true/false)")
    timeout: int = Field(30, description="Timeout in seconds")
    read_only_mode: bool = Field(False, description="Read-only mode (true/false)")
    rate_limit_enabled: bool = Field(
        False, description="Enable rate limiting (true/false)"
    )
    rate_limit_max_requests: int = Field(60, description="Maximum requests per minute")
    rate_limit_window_minutes: int = Field(
        1, description="Rate limit window in minutes"
    )
