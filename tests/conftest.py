"""
PyTest configuration and fixtures for GentooUI tests.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, MagicMock

from gentooui.core.config import AppConfig, ConfigManager


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    return AppConfig(dry_run=True)


@pytest.fixture
def config_manager():
    """Create a ConfigManager instance for testing."""
    return ConfigManager()


@pytest.fixture
def mock_system_info():
    """Mock system information."""
    from gentooui.utils.system import SystemInfo
    return SystemInfo(
        architecture="x86_64",
        cpu_count=4,
        memory_total=8 * 1024 * 1024 * 1024,  # 8GB
        disk_info=[],
        network_interfaces=[],
        boot_mode="UEFI",
        platform="Linux-5.15.0-generic"
    )


@pytest.fixture
def temp_mount_point(tmp_path):
    """Create a temporary mount point for testing."""
    mount_dir = tmp_path / "mnt" / "gentoo"
    mount_dir.mkdir(parents=True)
    return mount_dir


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls."""
    mock = Mock()
    mock.returncode = 0
    mock.stdout = ""
    mock.stderr = ""
    return mock
