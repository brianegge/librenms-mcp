#!/usr/bin/env python3
"""
LibreNMS MCP Server

Provides a Model Context Protocol (MCP) server exposing tools that interact with the LibreNMS API.
"""

import logging
import os
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware

from librenms_mcp.librenms_client import get_librenms_config_from_env
from librenms_mcp.librenms_middlewares import ReadOnlyTagMiddleware
from librenms_mcp.librenms_tools import register_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get package version
try:
    __version__ = version("librenms-mcp")
except PackageNotFoundError:
    __version__ = "0.0.1"

# Initialize FastMCP server
mcp = FastMCP(
    name="LibreNMS MCP Server",
    version=__version__,
    instructions=(
        "This MCP server exposes tools for interacting with the LibreNMS API, supporting both read and write operations if not in read-only mode."
    ),
    dependencies=["httpx", "python-dotenv", "pydantic"],
)

try:
    LNMS_CONFIG = get_librenms_config_from_env()
except Exception as e:
    logger.error(f"Invalid LibreNMS configuration: {e}")
    raise

# Register all tools
register_tools(mcp, LNMS_CONFIG)

# Enforce read-only behavior via middleware
if getattr(LNMS_CONFIG, "read_only_mode", False):
    logger.info("Read-only mode is enabled - applying middleware")
    mcp.add_middleware(ReadOnlyTagMiddleware())

# Optional rate limiting
if getattr(LNMS_CONFIG, "rate_limit_enabled", False):
    logger.info("Rate limiting is enabled - applying middleware")
    mcp.add_middleware(
        SlidingWindowRateLimitingMiddleware(
            max_requests=LNMS_CONFIG.rate_limit_max_requests,
            window_minutes=LNMS_CONFIG.rate_limit_window_minutes,
        )
    )


def main():
    # Basic validation
    if not all([LNMS_CONFIG.librenms_url, LNMS_CONFIG.token]):
        logger.error(
            "Missing required LibreNMS configuration (LIBRENMS_URL or LIBRENMS_TOKEN). Check your .env file."
        )
        raise SystemExit(1)

    logger.info(f"Starting LibreNMS MCP Server at {LNMS_CONFIG.librenms_url} ...")
    mcp.run()


if __name__ == "__main__":
    main()
