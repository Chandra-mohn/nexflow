#!/usr/bin/env python3
"""
Nexflow Language Server Entry Point

Starts the LSP server with registered language modules.
Run with: python -m backend.lsp
"""

import argparse
import logging
import sys

from backend.lsp.driver import server
from backend.lsp.modules.proc_module import ProcModule
from backend.lsp.modules.schema_module import SchemaModule
from backend.lsp.modules.transform_module import TransformModule
from backend.lsp.modules.rules_module import RulesModule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("nexflow-lsp")


def register_modules():
    """Register all available language modules."""

    # L1: ProcDSL - Process Orchestration
    try:
        server.register_module(ProcModule())
        logger.info("Registered L1 ProcDSL module")
    except Exception as e:
        logger.error(f"Failed to register ProcModule: {e}")

    # L2: SchemaDSL - Data Schemas
    try:
        server.register_module(SchemaModule())
        logger.info("Registered L2 SchemaDSL module")
    except Exception as e:
        logger.error(f"Failed to register SchemaModule: {e}")

    # L3: TransformDSL - Transformations
    try:
        server.register_module(TransformModule())
        logger.info("Registered L3 TransformDSL module")
    except Exception as e:
        logger.error(f"Failed to register TransformModule: {e}")

    # L4: RulesDSL - Decision Logic
    try:
        server.register_module(RulesModule())
        logger.info("Registered L4 RulesDSL module")
    except Exception as e:
        logger.error(f"Failed to register RulesModule: {e}")


def main():
    """Main entry point for the Nexflow LSP server."""
    parser = argparse.ArgumentParser(
        description="Nexflow Language Server for VS Code"
    )
    parser.add_argument(
        "--tcp",
        action="store_true",
        help="Run server over TCP instead of stdio"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="TCP host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=2087,
        help="TCP port (default: 2087)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Register language modules
    register_modules()

    logger.info("Starting Nexflow Language Server...")

    if args.tcp:
        logger.info(f"Running in TCP mode on {args.host}:{args.port}")
        server.start_tcp(args.host, args.port)
    else:
        logger.info("Running in stdio mode")
        server.start_io()


if __name__ == "__main__":
    main()
