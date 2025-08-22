"""
Main TUI application class using Textual framework.
"""

import asyncio
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button, Footer, Header, Static, ProgressBar, 
    Log, TabbedContent, TabPane, DataTable, Tree
)
from textual.reactive import reactive
from textual.message import Message

from .config import AppConfig
from .logger import get_logger
from .installer import InstallationManager
from ..screens.welcome import WelcomeScreen
from ..screens.disk_setup import DiskSetupScreen
from ..screens.stage3 import Stage3Screen
from ..screens.configuration import ConfigurationScreen
from ..screens.kernel import KernelScreen
from ..screens.bootloader import BootloaderScreen
from ..screens.finalization import FinalizationScreen
from ..screens.progress import ProgressScreen


logger = get_logger(__name__)


class GentooUIApp(App):
    """
    Main Textual application for GentooUI.
    
    This is the primary interface that coordinates the installation process
    through various screens and manages the overall application state.
    """
    
    CSS_PATH = "styles.css"
    TITLE = "GentooUI - Gentoo Linux Installation"
    SUB_TITLE = "Step-by-step guided installation"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+s", "screenshot", "Screenshot"),
        Binding("f1", "help", "Help"),
        Binding("f10", "toggle_dark", "Toggle Dark Mode"),
    ]
    
    # Reactive variables
    current_step = reactive(0)
    total_steps = reactive(7)
    installation_active = reactive(False)
    dry_run_mode = reactive(False)
    
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.installation_manager = InstallationManager(config)
        self.dry_run_mode = config.dry_run
        
        # Installation steps
        self.steps = [
            ("Welcome", "welcome"),
            ("Disk Setup", "disk_setup"),
            ("Stage3", "stage3"),
            ("Configuration", "configuration"),
            ("Kernel", "kernel"),
            ("Bootloader", "bootloader"),
            ("Finalization", "finalization"),
        ]
        
        logger.info(f"Initialized GentooUIApp with {len(self.steps)} steps")
    
    def compose(self) -> ComposeResult:
        """Create the main application layout."""
        yield Header()
        
        with Container(id="main-container"):
            # Installation progress bar
            with Container(id="progress-container"):
                yield Static("Installation Progress:", classes="progress-label")
                yield ProgressBar(
                    total=self.total_steps,
                    show_eta=True,
                    id="main-progress"
                )
            
            # Main content area
            yield Container(id="content-area")
            
            # Status bar
            with Horizontal(id="status-bar"):
                yield Static(f"Step {self.current_step + 1}/{self.total_steps}", 
                           id="step-counter")
                if self.dry_run_mode:
                    yield Static("DRY RUN MODE", id="dry-run-indicator", 
                               classes="warning")
                yield Static("Ready", id="status-text")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application after mounting."""
        logger.info("App mounted, showing welcome screen")
        self.show_welcome_screen()
        
        # Update progress bar
        progress_bar = self.query_one("#main-progress", ProgressBar)
        progress_bar.progress = self.current_step
    
    def show_welcome_screen(self) -> None:
        """Show the welcome screen."""
        logger.info("Displaying welcome screen")
        content_area = self.query_one("#content-area")
        content_area.remove_children()
        
        welcome_screen = WelcomeScreen(
            config=self.config,
            on_continue=self.on_welcome_continue,
            on_load_config=self.on_load_config
        )
        content_area.mount(welcome_screen)
        self.update_status("Welcome - Review system information and configuration")
    
    def show_disk_setup_screen(self) -> None:
        """Show the disk partitioning screen."""
        logger.info("Displaying disk setup screen")
        content_area = self.query_one("#content-area")
        content_area.remove_children()
        
        disk_screen = DiskSetupScreen(
            config=self.config,
            on_continue=self.on_disk_setup_continue,
            on_back=self.on_back_to_welcome
        )
        content_area.mount(disk_screen)
        self.update_status("Disk Setup - Configure partitions and file systems")
    
    def show_stage3_screen(self) -> None:
        """Show the Stage3 download and extraction screen."""
        logger.info("Displaying Stage3 screen")
        content_area = self.query_one("#content-area")
        content_area.remove_children()
        
        stage3_screen = Stage3Screen(
            config=self.config,
            installation_manager=self.installation_manager,
            on_continue=self.on_stage3_continue,
            on_back=self.on_back_to_disk_setup
        )
        content_area.mount(stage3_screen)
        self.update_status("Stage3 - Download and extract base system")
    
    def show_configuration_screen(self) -> None:
        """Show the system configuration screen."""
        logger.info("Displaying configuration screen")
        content_area = self.query_one("#content-area")
        content_area.remove_children()
        
        config_screen = ConfigurationScreen(
            config=self.config,
            on_continue=self.on_configuration_continue,
            on_back=self.on_back_to_stage3
        )
        content_area.mount(config_screen)
        self.update_status("Configuration - Set up system configuration")
    
    def show_kernel_screen(self) -> None:
        """Show the kernel compilation screen."""
        logger.info("Displaying kernel screen")
        content_area = self.query_one("#content-area")
        content_area.remove_children()
        
        kernel_screen = KernelScreen(
            config=self.config,
            installation_manager=self.installation_manager,
            on_continue=self.on_kernel_continue,
            on_back=self.on_back_to_configuration
        )
        content_area.mount(kernel_screen)
        self.update_status("Kernel - Configure and compile kernel")
    
    def show_bootloader_screen(self) -> None:
        """Show the bootloader installation screen."""
        logger.info("Displaying bootloader screen")
        content_area = self.query_one("#content-area")
        content_area.remove_children()
        
        bootloader_screen = BootloaderScreen(
            config=self.config,
            installation_manager=self.installation_manager,
            on_continue=self.on_bootloader_continue,
            on_back=self.on_back_to_kernel
        )
        content_area.mount(bootloader_screen)
        self.update_status("Bootloader - Install and configure bootloader")
    
    def show_finalization_screen(self) -> None:
        """Show the finalization screen."""
        logger.info("Displaying finalization screen")
        content_area = self.query_one("#content-area")
        content_area.remove_children()
        
        finalization_screen = FinalizationScreen(
            config=self.config,
            installation_manager=self.installation_manager,
            on_finish=self.on_installation_complete
        )
        content_area.mount(finalization_screen)
        self.update_status("Finalization - Complete installation and cleanup")
    
    # Event handlers
    def on_welcome_continue(self) -> None:
        """Handle continue from welcome screen."""
        self.advance_step()
        self.show_disk_setup_screen()
    
    def on_disk_setup_continue(self) -> None:
        """Handle continue from disk setup screen."""
        self.advance_step()
        self.show_stage3_screen()
    
    def on_stage3_continue(self) -> None:
        """Handle continue from Stage3 screen."""
        self.advance_step()
        self.show_configuration_screen()
    
    def on_configuration_continue(self) -> None:
        """Handle continue from configuration screen."""
        self.advance_step()
        self.show_kernel_screen()
    
    def on_kernel_continue(self) -> None:
        """Handle continue from kernel screen."""
        self.advance_step()
        self.show_bootloader_screen()
    
    def on_bootloader_continue(self) -> None:
        """Handle continue from bootloader screen."""
        self.advance_step()
        self.show_finalization_screen()
    
    def on_installation_complete(self) -> None:
        """Handle installation completion."""
        logger.info("Installation completed successfully")
        self.update_status("Installation completed successfully!")
        self.installation_active = False
    
    # Back navigation handlers
    def on_back_to_welcome(self) -> None:
        """Go back to welcome screen."""
        self.previous_step()
        self.show_welcome_screen()
    
    def on_back_to_disk_setup(self) -> None:
        """Go back to disk setup screen."""
        self.previous_step()
        self.show_disk_setup_screen()
    
    def on_back_to_stage3(self) -> None:
        """Go back to Stage3 screen."""
        self.previous_step()
        self.show_stage3_screen()
    
    def on_back_to_configuration(self) -> None:
        """Go back to configuration screen."""
        self.previous_step()
        self.show_configuration_screen()
    
    def on_back_to_kernel(self) -> None:
        """Go back to kernel screen."""
        self.previous_step()
        self.show_kernel_screen()
    
    def on_load_config(self, config_path: str) -> None:
        """Handle loading a new configuration."""
        logger.info(f"Loading configuration from {config_path}")
        # TODO: Implement configuration loading
        self.update_status(f"Loaded configuration from {config_path}")
    
    # Utility methods
    def advance_step(self) -> None:
        """Move to the next installation step."""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            progress_bar = self.query_one("#main-progress", ProgressBar)
            progress_bar.progress = self.current_step
            self.update_step_counter()
    
    def previous_step(self) -> None:
        """Move to the previous installation step."""
        if self.current_step > 0:
            self.current_step -= 1
            progress_bar = self.query_one("#main-progress", ProgressBar)
            progress_bar.progress = self.current_step
            self.update_step_counter()
    
    def update_step_counter(self) -> None:
        """Update the step counter display."""
        step_counter = self.query_one("#step-counter", Static)
        step_counter.update(f"Step {self.current_step + 1}/{self.total_steps}")
    
    def update_status(self, message: str) -> None:
        """Update the status message."""
        try:
            status_text = self.query_one("#status-text", Static)
            status_text.update(message)
        except Exception:
            # Widget might not be mounted yet
            pass
    
    # Action handlers
    def action_quit(self) -> None:
        """Handle quit action."""
        logger.info("User requested quit")
        self.exit()
    
    def action_help(self) -> None:
        """Show help dialog."""
        # TODO: Implement help dialog
        self.update_status("Help not implemented yet")
    
    def action_toggle_dark(self) -> None:
        """Toggle dark/light mode."""
        self.dark = not self.dark
        self.update_status(f"Switched to {'dark' if self.dark else 'light'} mode")
    
    def action_screenshot(self) -> None:
        """Take a screenshot."""
        self.save_screenshot("gentooui_screenshot.svg")
        self.update_status("Screenshot saved as gentooui_screenshot.svg")
