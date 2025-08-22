"""
Tests for configuration management.
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from gentooui.core.config import (
    AppConfig, DiskConfig, Stage3Config,
    ConfigManager
)


class TestConfig:
    """Test configuration classes and management."""
    
    def test_default_config_creation(self):
        """Test default configuration creation."""
        config = AppConfig()
        
        assert config.dry_run is False
        assert config.verbose is False
        assert config.log_level == "INFO"
        assert config.mount_point == "/mnt/gentoo"
        assert config.work_dir == "/tmp/gentooui"
        
        # Test nested config objects
        assert isinstance(config.disk, DiskConfig)
        assert isinstance(config.stage3, Stage3Config)
        assert config.disk.target_disk == "/dev/sda"
        assert config.stage3.architecture == "amd64"
    
    def test_config_manager_default(self, config_manager):
        """Test ConfigManager default configuration."""
        config = config_manager.get_default_config()
        
        assert isinstance(config, AppConfig)
        assert config.dry_run is False
    
    def test_config_save_load(self, config_manager, tmp_path):
        """Test configuration saving and loading."""
        # Create a test configuration
        config = AppConfig(
            dry_run=True,
            verbose=True,
            log_level="DEBUG"
        )
        config.disk.target_disk = "/dev/sdb"
        config.system.hostname = "test-host"
        
        # Save configuration
        config_file = tmp_path / "test_config.yaml"
        config_manager.save_config(config, config_file)
        
        assert config_file.exists()
        
        # Load configuration
        loaded_config = config_manager.load_config(config_file)
        
        assert loaded_config.dry_run is True
        assert loaded_config.verbose is True
        assert loaded_config.log_level == "DEBUG"
        assert loaded_config.disk.target_disk == "/dev/sdb"
        assert loaded_config.system.hostname == "test-host"
    
    def test_config_validation(self, config_manager):
        """Test configuration validation."""
        # Valid configuration
        valid_data = {
            "dry_run": True,
            "log_level": "INFO",
            "disk": {
                "target_disk": "/dev/sda",
                "partition_scheme": "gpt"
            }
        }
        
        config = config_manager.validate_config(valid_data)
        assert config.dry_run is True
        
        # Invalid configuration
        invalid_data = {
            "log_level": "INVALID_LEVEL"
        }
        
        with pytest.raises(Exception):  # Should raise ValidationError
            config_manager.validate_config(invalid_data)
    
    def test_config_merge(self, config_manager):
        """Test configuration merging."""
        base_config = AppConfig(dry_run=False, verbose=False)
        base_config.disk.target_disk = "/dev/sda"
        
        override_data = {
            "dry_run": True,
            "disk": {
                "target_disk": "/dev/sdb"
            }
        }
        
        merged_config = config_manager.merge_configs(base_config, override_data)
        
        assert merged_config.dry_run is True  # Overridden
        assert merged_config.verbose is False  # From base
        assert merged_config.disk.target_disk == "/dev/sdb"  # Overridden
    
    def test_empty_config_file(self, config_manager, tmp_path):
        """Test loading empty configuration file."""
        config_file = tmp_path / "empty_config.yaml"
        config_file.write_text("")
        
        config = config_manager.load_config(config_file)
        assert isinstance(config, AppConfig)
        assert config.dry_run is False  # Should use defaults
