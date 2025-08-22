"""
Core installation manager that orchestrates the Gentoo installation process.
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig
from .logger import get_logger
from ..installers.disk import DiskManager
from ..installers.stage3 import Stage3Manager
from ..installers.portage import PortageManager
from ..installers.kernel import KernelManager
from ..installers.bootloader import BootloaderManager
from ..installers.system import SystemManager


logger = get_logger(__name__)


class InstallationStep(Enum):
    """Enumeration of installation steps."""
    DISK_SETUP = "disk_setup"
    STAGE3_DOWNLOAD = "stage3_download"
    STAGE3_EXTRACT = "stage3_extract"
    PORTAGE_SETUP = "portage_setup"
    SYSTEM_CONFIG = "system_config"
    KERNEL_INSTALL = "kernel_install"
    KERNEL_CONFIG = "kernel_config"
    KERNEL_COMPILE = "kernel_compile"
    BOOTLOADER_INSTALL = "bootloader_install"
    FINALIZATION = "finalization"


@dataclass
class StepProgress:
    """Progress information for an installation step."""
    step: InstallationStep
    name: str
    progress: float  # 0.0 to 1.0
    status: str
    details: Optional[str] = None
    error: Optional[str] = None


class InstallationManager:
    """
    Manages the overall Gentoo installation process.
    
    This class coordinates all installation steps and provides progress
    reporting and error handling capabilities.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.progress_callback: Optional[Callable[[StepProgress], None]] = None
        self.current_step: Optional[InstallationStep] = None
        
        # Initialize step managers
        self.disk_manager = DiskManager(config)
        self.stage3_manager = Stage3Manager(config)
        self.portage_manager = PortageManager(config)
        self.kernel_manager = KernelManager(config)
        self.bootloader_manager = BootloaderManager(config)
        self.system_manager = SystemManager(config)
        
        # Installation steps definition
        self.steps = [
            (InstallationStep.DISK_SETUP, "Setting up disk partitions", self.run_disk_setup),
            (InstallationStep.STAGE3_DOWNLOAD, "Downloading Stage3", self.run_stage3_download),
            (InstallationStep.STAGE3_EXTRACT, "Extracting Stage3", self.run_stage3_extract),
            (InstallationStep.PORTAGE_SETUP, "Configuring Portage", self.run_portage_setup),
            (InstallationStep.SYSTEM_CONFIG, "System configuration", self.run_system_config),
            (InstallationStep.KERNEL_INSTALL, "Installing kernel sources", self.run_kernel_install),
            (InstallationStep.KERNEL_CONFIG, "Configuring kernel", self.run_kernel_config),
            (InstallationStep.KERNEL_COMPILE, "Compiling kernel", self.run_kernel_compile),
            (InstallationStep.BOOTLOADER_INSTALL, "Installing bootloader", self.run_bootloader_install),
            (InstallationStep.FINALIZATION, "Finalizing installation", self.run_finalization),
        ]
        
        logger.info(f"InstallationManager initialized with {len(self.steps)} steps")
    
    def set_progress_callback(self, callback: Callable[[StepProgress], None]) -> None:
        """Set callback function for progress updates."""
        self.progress_callback = callback
        logger.debug("Progress callback set")
    
    def _report_progress(
        self,
        step: InstallationStep,
        name: str,
        progress: float,
        status: str,
        details: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Report progress to the callback if set."""
        if self.progress_callback:
            step_progress = StepProgress(
                step=step,
                name=name,
                progress=progress,
                status=status,
                details=details,
                error=error
            )
            self.progress_callback(step_progress)
    
    async def run_full_installation(self) -> bool:
        """
        Run the complete Gentoo installation process.
        
        Returns:
            True if installation completed successfully, False otherwise
        """
        logger.info("Starting full Gentoo installation")
        
        try:
            total_steps = len(self.steps)
            
            for i, (step, name, func) in enumerate(self.steps):
                self.current_step = step
                logger.info(f"Starting step {i+1}/{total_steps}: {name}")
                
                self._report_progress(
                    step=step,
                    name=name,
                    progress=0.0,
                    status="Starting..."
                )
                
                try:
                    success = await func()
                    if not success:
                        error_msg = f"Step failed: {name}"
                        logger.error(error_msg)
                        self._report_progress(
                            step=step,
                            name=name,
                            progress=0.0,
                            status="Failed",
                            error=error_msg
                        )
                        return False
                    
                    self._report_progress(
                        step=step,
                        name=name,
                        progress=1.0,
                        status="Completed"
                    )
                    
                except Exception as e:
                    error_msg = f"Exception in step {name}: {e}"
                    logger.exception(error_msg)
                    self._report_progress(
                        step=step,
                        name=name,
                        progress=0.0,
                        status="Error",
                        error=error_msg
                    )
                    return False
            
            logger.info("Full installation completed successfully")
            return True
            
        except Exception as e:
            logger.exception(f"Critical error during installation: {e}")
            return False
    
    # Individual step implementations
    async def run_disk_setup(self) -> bool:
        """Set up disk partitions and filesystems."""
        logger.info("Running disk setup")
        
        try:
            # Create partition table
            self._report_progress(
                InstallationStep.DISK_SETUP,
                "Setting up disk partitions",
                0.1,
                "Creating partition table..."
            )
            
            if not await self.disk_manager.create_partition_table():
                return False
            
            # Create partitions
            self._report_progress(
                InstallationStep.DISK_SETUP,
                "Setting up disk partitions",
                0.3,
                "Creating partitions..."
            )
            
            if not await self.disk_manager.create_partitions():
                return False
            
            # Format filesystems
            self._report_progress(
                InstallationStep.DISK_SETUP,
                "Setting up disk partitions",
                0.6,
                "Formatting filesystems..."
            )
            
            if not await self.disk_manager.format_filesystems():
                return False
            
            # Mount filesystems
            self._report_progress(
                InstallationStep.DISK_SETUP,
                "Setting up disk partitions",
                0.9,
                "Mounting filesystems..."
            )
            
            if not await self.disk_manager.mount_filesystems():
                return False
            
            logger.info("Disk setup completed successfully")
            return True
            
        except Exception as e:
            logger.exception(f"Error during disk setup: {e}")
            return False
    
    async def run_stage3_download(self) -> bool:
        """Download Stage3 tarball."""
        logger.info("Downloading Stage3")
        
        try:
            return await self.stage3_manager.download_stage3(
                progress_callback=lambda p, s: self._report_progress(
                    InstallationStep.STAGE3_DOWNLOAD,
                    "Downloading Stage3",
                    p,
                    s
                )
            )
        except Exception as e:
            logger.exception(f"Error downloading Stage3: {e}")
            return False
    
    async def run_stage3_extract(self) -> bool:
        """Extract Stage3 tarball."""
        logger.info("Extracting Stage3")
        
        try:
            return await self.stage3_manager.extract_stage3(
                progress_callback=lambda p, s: self._report_progress(
                    InstallationStep.STAGE3_EXTRACT,
                    "Extracting Stage3",
                    p,
                    s
                )
            )
        except Exception as e:
            logger.exception(f"Error extracting Stage3: {e}")
            return False
    
    async def run_portage_setup(self) -> bool:
        """Configure Portage package manager."""
        logger.info("Configuring Portage")
        
        try:
            return await self.portage_manager.setup_portage(
                progress_callback=lambda p, s: self._report_progress(
                    InstallationStep.PORTAGE_SETUP,
                    "Configuring Portage",
                    p,
                    s
                )
            )
        except Exception as e:
            logger.exception(f"Error configuring Portage: {e}")
            return False
    
    async def run_system_config(self) -> bool:
        """Configure basic system settings."""
        logger.info("Configuring system")
        
        try:
            return await self.system_manager.configure_system(
                progress_callback=lambda p, s: self._report_progress(
                    InstallationStep.SYSTEM_CONFIG,
                    "System configuration",
                    p,
                    s
                )
            )
        except Exception as e:
            logger.exception(f"Error configuring system: {e}")
            return False
    
    async def run_kernel_install(self) -> bool:
        """Install kernel sources."""
        logger.info("Installing kernel sources")
        
        try:
            return await self.kernel_manager.install_sources(
                progress_callback=lambda p, s: self._report_progress(
                    InstallationStep.KERNEL_INSTALL,
                    "Installing kernel sources",
                    p,
                    s
                )
            )
        except Exception as e:
            logger.exception(f"Error installing kernel sources: {e}")
            return False
    
    async def run_kernel_config(self) -> bool:
        """Configure kernel."""
        logger.info("Configuring kernel")
        
        try:
            return await self.kernel_manager.configure_kernel(
                progress_callback=lambda p, s: self._report_progress(
                    InstallationStep.KERNEL_CONFIG,
                    "Configuring kernel",
                    p,
                    s
                )
            )
        except Exception as e:
            logger.exception(f"Error configuring kernel: {e}")
            return False
    
    async def run_kernel_compile(self) -> bool:
        """Compile kernel."""
        logger.info("Compiling kernel")
        
        try:
            return await self.kernel_manager.compile_kernel(
                progress_callback=lambda p, s: self._report_progress(
                    InstallationStep.KERNEL_COMPILE,
                    "Compiling kernel",
                    p,
                    s
                )
            )
        except Exception as e:
            logger.exception(f"Error compiling kernel: {e}")
            return False
    
    async def run_bootloader_install(self) -> bool:
        """Install and configure bootloader."""
        logger.info("Installing bootloader")
        
        try:
            return await self.bootloader_manager.install_bootloader(
                progress_callback=lambda p, s: self._report_progress(
                    InstallationStep.BOOTLOADER_INSTALL,
                    "Installing bootloader",
                    p,
                    s
                )
            )
        except Exception as e:
            logger.exception(f"Error installing bootloader: {e}")
            return False
    
    async def run_finalization(self) -> bool:
        """Finalize installation."""
        logger.info("Finalizing installation")
        
        try:
            return await self.system_manager.finalize_installation(
                progress_callback=lambda p, s: self._report_progress(
                    InstallationStep.FINALIZATION,
                    "Finalizing installation",
                    p,
                    s
                )
            )
        except Exception as e:
            logger.exception(f"Error during finalization: {e}")
            return False
    
    # Utility methods
    def get_current_step(self) -> Optional[InstallationStep]:
        """Get the currently running step."""
        return self.current_step
    
    def get_all_steps(self) -> List[tuple]:
        """Get list of all installation steps."""
        return [(step, name) for step, name, _ in self.steps]
    
    def validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met."""
        logger.info("Validating installation prerequisites")
        
        # Check if running as root
        if not self.config.dry_run:
            import os
            if os.geteuid() != 0:
                logger.error("Installation must run as root")
                return False
        
        # Check target disk exists
        target_disk = Path(self.config.disk.target_disk)
        if not self.config.dry_run and not target_disk.exists():
            logger.error(f"Target disk does not exist: {target_disk}")
            return False
        
        # Check mount point is available
        mount_point = Path(self.config.mount_point)
        if mount_point.exists() and any(mount_point.iterdir()):
            logger.warning(f"Mount point is not empty: {mount_point}")
        
        logger.info("Prerequisites validation completed")
        return True
