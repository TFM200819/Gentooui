"""
System utility functions for GentooUI.
"""

import os
import platform
import subprocess
import psutil
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from ..core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SystemInfo:
    """System information container."""
    architecture: str
    cpu_count: int
    memory_total: int  # in bytes
    disk_info: List[Dict[str, Any]]
    network_interfaces: List[Dict[str, Any]]
    boot_mode: str  # UEFI or BIOS
    platform: str


def check_root_privileges() -> bool:
    """Check if the current process has root privileges."""
    return os.geteuid() == 0


def check_system_compatibility() -> bool:
    """Check if the system is compatible with Gentoo installation."""
    try:
        # Check if we're on Linux
        if platform.system() != "Linux":
            logger.error("System is not Linux-based")
            return False
        
        # Check architecture
        arch = platform.machine()
        supported_archs = ["x86_64", "amd64", "i686", "arm64", "aarch64"]
        if arch not in supported_archs:
            logger.warning(f"Architecture {arch} may not be fully supported")
        
        # Check if we have enough memory (minimum 1GB)
        memory = psutil.virtual_memory()
        if memory.total < 1024 * 1024 * 1024:  # 1GB
            logger.warning("System has less than 1GB RAM, installation may be slow")
        
        # Check if required tools are available
        required_tools = ["fdisk", "mkfs.ext4", "mount", "wget", "tar", "chroot"]
        missing_tools = []
        
        for tool in required_tools:
            if not is_command_available(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            logger.error(f"Missing required tools: {', '.join(missing_tools)}")
            return False
        
        return True
        
    except Exception as e:
        logger.exception(f"Error checking system compatibility: {e}")
        return False


def get_system_info() -> SystemInfo:
    """Get comprehensive system information."""
    logger.info("Gathering system information")
    
    try:
        # Architecture
        architecture = platform.machine()
        
        # CPU count
        cpu_count = psutil.cpu_count(logical=False)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_total = memory.total
        
        # Disk information
        disk_info = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free
                })
            except PermissionError:
                # Skip partitions we can't access
                continue
        
        # Network interfaces
        network_interfaces = []
        for interface, addresses in psutil.net_if_addrs().items():
            interface_info = {"name": interface, "addresses": []}
            for addr in addresses:
                interface_info["addresses"].append({
                    "family": addr.family.name,
                    "address": addr.address,
                    "netmask": addr.netmask
                })
            network_interfaces.append(interface_info)
        
        # Boot mode (UEFI vs BIOS)
        boot_mode = detect_boot_mode()
        
        # Platform
        platform_name = platform.platform()
        
        return SystemInfo(
            architecture=architecture,
            cpu_count=cpu_count,
            memory_total=memory_total,
            disk_info=disk_info,
            network_interfaces=network_interfaces,
            boot_mode=boot_mode,
            platform=platform_name
        )
        
    except Exception as e:
        logger.exception(f"Error gathering system information: {e}")
        raise


def detect_boot_mode() -> str:
    """Detect if the system is booted in UEFI or BIOS mode."""
    try:
        # Check if /sys/firmware/efi exists
        if Path("/sys/firmware/efi").exists():
            return "UEFI"
        else:
            return "BIOS"
    except Exception:
        return "Unknown"


def is_command_available(command: str) -> bool:
    """Check if a command is available in the system PATH."""
    try:
        subprocess.run(
            ["which", command],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


async def run_command(
    command: List[str],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    capture_output: bool = True
) -> Tuple[int, str, str]:
    """
    Run a system command asynchronously.
    
    Args:
        command: Command to run as list of strings
        cwd: Working directory
        env: Environment variables
        timeout: Command timeout in seconds
        capture_output: Whether to capture stdout/stderr
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    logger.debug(f"Running command: {' '.join(command)}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
        
        stdout_str = stdout.decode('utf-8') if stdout else ""
        stderr_str = stderr.decode('utf-8') if stderr else ""
        
        logger.debug(f"Command completed with return code: {process.returncode}")
        
        return process.returncode, stdout_str, stderr_str
        
    except asyncio.TimeoutError:
        logger.error(f"Command timed out: {' '.join(command)}")
        process.kill()
        await process.wait()
        return -1, "", "Command timed out"
    except Exception as e:
        logger.exception(f"Error running command: {e}")
        return -1, "", str(e)


def get_block_devices() -> List[Dict[str, Any]]:
    """Get list of block devices in the system."""
    logger.info("Getting block devices")
    
    try:
        result = subprocess.run(
            ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE"],
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        data = json.loads(result.stdout)
        return data.get("blockdevices", [])
        
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        logger.error(f"Error getting block devices: {e}")
        return []


def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def is_mounted(device_path: str) -> bool:
    """Check if a device is currently mounted."""
    try:
        for partition in psutil.disk_partitions():
            if partition.device == device_path:
                return True
        return False
    except Exception:
        return False


def get_mount_point(device_path: str) -> Optional[str]:
    """Get the mount point of a device."""
    try:
        for partition in psutil.disk_partitions():
            if partition.device == device_path:
                return partition.mountpoint
        return None
    except Exception:
        return None


def create_directory(path: Path, mode: int = 0o755) -> bool:
    """Create directory with specified permissions."""
    try:
        path.mkdir(parents=True, exist_ok=True, mode=mode)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def ensure_mount_point(path: Path) -> bool:
    """Ensure mount point directory exists and is empty."""
    try:
        if path.exists():
            if path.is_dir():
                # Check if it's a mount point
                if is_mounted(str(path)):
                    logger.warning(f"Path {path} is already a mount point")
                    return True
                
                # Check if directory is empty
                if any(path.iterdir()):
                    logger.error(f"Mount point {path} is not empty")
                    return False
            else:
                logger.error(f"Path {path} exists but is not a directory")
                return False
        else:
            # Create the directory
            return create_directory(path)
        
        return True
        
    except Exception as e:
        logger.error(f"Error ensuring mount point {path}: {e}")
        return False


def validate_hostname(hostname: str) -> bool:
    """Validate hostname format."""
    if not hostname:
        return False
    
    if len(hostname) > 253:
        return False
    
    import re
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(pattern, hostname))


def get_timezone_list() -> List[str]:
    """Get list of available timezones."""
    try:
        result = subprocess.run(
            ["timedatectl", "list-timezones"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        # Fallback to common timezones
        return [
            "UTC",
            "US/Eastern",
            "US/Central", 
            "US/Mountain",
            "US/Pacific",
            "Europe/London",
            "Europe/Paris",
            "Europe/Berlin",
            "Asia/Tokyo",
            "Australia/Sydney"
        ]


def get_available_locales() -> List[str]:
    """Get list of available locales."""
    try:
        result = subprocess.run(
            ["locale", "-a"],
            capture_output=True,
            text=True,
            check=True
        )
        locales = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        return sorted(locales)
    except subprocess.CalledProcessError:
        # Fallback to common locales
        return [
            "C",
            "POSIX",
            "en_US.UTF-8",
            "en_GB.UTF-8",
            "de_DE.UTF-8",
            "fr_FR.UTF-8",
            "es_ES.UTF-8",
            "it_IT.UTF-8",
            "ja_JP.UTF-8",
            "zh_CN.UTF-8"
        ]
