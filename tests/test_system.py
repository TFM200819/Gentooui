"""
Tests for system utility functions.
"""

import pytest
from unittest.mock import patch, Mock
from pathlib import Path

from gentooui.utils.system import (
    check_root_privileges, check_system_compatibility,
    get_system_info, detect_boot_mode, is_command_available,
    format_bytes, validate_hostname
)


class TestSystemUtils:
    """Test system utility functions."""
    
    @patch('os.geteuid')
    def test_check_root_privileges(self, mock_geteuid):
        """Test root privilege checking."""
        # Test root user
        mock_geteuid.return_value = 0
        assert check_root_privileges() is True
        
        # Test non-root user
        mock_geteuid.return_value = 1000
        assert check_root_privileges() is False
    
    @patch('platform.system')
    @patch('gentooui.utils.system.is_command_available')
    @patch('psutil.virtual_memory')
    def test_check_system_compatibility(self, mock_memory, mock_command, mock_system):
        """Test system compatibility checking."""
        # Mock Linux system with enough memory and all tools available
        mock_system.return_value = "Linux"
        mock_memory.return_value.total = 2 * 1024 * 1024 * 1024  # 2GB
        mock_command.return_value = True
        
        assert check_system_compatibility() is True
        
        # Test non-Linux system
        mock_system.return_value = "Windows"
        assert check_system_compatibility() is False
    
    @patch('pathlib.Path.exists')
    def test_detect_boot_mode(self, mock_exists):
        """Test boot mode detection."""
        # Test UEFI
        mock_exists.return_value = True
        assert detect_boot_mode() == "UEFI"
        
        # Test BIOS
        mock_exists.return_value = False
        assert detect_boot_mode() == "BIOS"
    
    @patch('subprocess.run')
    def test_is_command_available(self, mock_run):
        """Test command availability checking."""
        # Test available command
        mock_run.return_value = Mock()
        assert is_command_available("ls") is True
        
        # Test unavailable command
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, "which")
        assert is_command_available("nonexistent") is False
    
    def test_format_bytes(self):
        """Test byte formatting."""
        assert format_bytes(512) == "512.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_validate_hostname(self):
        """Test hostname validation."""
        # Valid hostnames
        assert validate_hostname("example") is True
        assert validate_hostname("example.com") is True
        assert validate_hostname("test-host") is True
        assert validate_hostname("server123") is True
        
        # Invalid hostnames
        assert validate_hostname("") is False
        assert validate_hostname("example.") is False
        assert validate_hostname("-example") is False
        assert validate_hostname("example-") is False
        assert validate_hostname("a" * 300) is False  # Too long
