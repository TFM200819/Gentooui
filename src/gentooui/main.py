#!/usr/bin/env python3
"""
Main entry point for GentooUI application.
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .core.app import GentooUIApp
from .core.config import ConfigManager, AppConfig
from .core.logger import setup_logging, get_logger
from .utils.system import check_root_privileges, check_system_compatibility


console = Console()
logger = get_logger(__name__)


def check_prerequisites() -> bool:
    """Check if the system meets the prerequisites for running GentooUI."""
    console.print(Panel.fit("🔍 Checking Prerequisites", style="bold blue"))
    
    # Check root privileges
    if not check_root_privileges():
        console.print("❌ Root privileges required. Please run with sudo.", style="bold red")
        return False
    
    # Check system compatibility
    if not check_system_compatibility():
        console.print("❌ System not compatible with Gentoo installation.", style="bold red")
        return False
    
    console.print("✅ Prerequisites check passed!", style="bold green")
    return True


def print_banner():
    """Print the application banner."""
    banner = Text()
    banner.append("╔══════════════════════════════════════╗\n", style="bold cyan")
    banner.append("║          ", style="bold cyan")
    banner.append("🐧 GentooUI v0.1.0", style="bold white")
    banner.append("          ║\n", style="bold cyan")
    banner.append("║   ", style="bold cyan")
    banner.append("Text User Interface for Gentoo Linux", style="italic white")
    banner.append("   ║\n", style="bold cyan")
    banner.append("╚══════════════════════════════════════╝", style="bold cyan")
    
    console.print(banner)
    console.print()


@click.command()
@click.option(
    "--config", 
    "-c", 
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file"
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Set logging level"
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help="Path to log file (default: ./gentooui.log)"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Run in dry-run mode (no actual system changes)"
)
@click.option(
    "--skip-checks",
    is_flag=True,
    help="Skip prerequisite checks (dangerous!)"
)
@click.version_option(version="0.1.0", prog_name="GentooUI")
def main(
    config: Optional[Path] = None,
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    dry_run: bool = False,
    skip_checks: bool = False
):
    """
    GentooUI - A Text User Interface for Gentoo Linux Installation.
    
    This tool provides a guided, step-by-step interface for installing
    Gentoo Linux on your system.
    """
    try:
        # Set up logging
        if log_file is None:
            log_file = Path("./gentooui.log")
        
        setup_logging(log_level, log_file)
        logger.info("Starting GentooUI application")
        
        # Print banner
        print_banner()
        
        # Check prerequisites unless skipped
        if not skip_checks and not check_prerequisites():
            sys.exit(1)
        
        # Load configuration
        config_manager = ConfigManager()
        
        if config:
            logger.info(f"Loading configuration from {config}")
            app_config = config_manager.load_config(config)
        else:
            logger.info("Using default configuration")
            app_config = config_manager.get_default_config()
        
        # Set dry-run mode
        app_config.dry_run = dry_run
        
        if dry_run:
            console.print("⚠️  Running in DRY-RUN mode - no actual changes will be made", 
                         style="bold yellow")
        
        # Run the TUI application
        logger.info("Starting TUI application")
        app = GentooUIApp(config=app_config)
        asyncio.run(app.run_async())
        
    except KeyboardInterrupt:
        console.print("\n👋 Installation cancelled by user", style="bold yellow")
        logger.info("Application cancelled by user")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n💥 Fatal error: {e}", style="bold red")
        logger.exception("Fatal error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
