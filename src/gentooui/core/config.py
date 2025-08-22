"""
Configuration management for GentooUI.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from marshmallow import Schema, fields, post_load, ValidationError

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class DiskConfig:
    """Configuration for disk partitioning."""
    target_disk: str = "/dev/sda"
    partition_scheme: str = "gpt"  # gpt, mbr
    boot_partition_size: str = "1G"
    swap_size: str = "4G"
    root_filesystem: str = "ext4"  # ext4, xfs, btrfs
    encryption_enabled: bool = False
    encryption_cipher: str = "aes-xts-plain64"


@dataclass
class Stage3Config:
    """Configuration for Stage3 installation."""
    mirror_url: str = "https://distfiles.gentoo.org"
    architecture: str = "amd64"
    variant: str = "hardened"  # hardened, systemd, musl, etc.
    auto_select: bool = True
    verify_signature: bool = True


@dataclass
class PortageConfig:
    """Configuration for Portage package manager."""
    make_opts: str = "-j$(nproc)"
    use_flags: List[str] = field(default_factory=lambda: [
        "bindist", "-gtk", "-qt5", "systemd"
    ])
    accept_keywords: List[str] = field(default_factory=lambda: ["~amd64"])
    mirrors: List[str] = field(default_factory=lambda: [
        "https://distfiles.gentoo.org"
    ])
    emerge_opts: str = "--ask --verbose"


@dataclass
class KernelConfig:
    """Configuration for kernel compilation."""
    kernel_source: str = "gentoo-sources"  # gentoo-sources, vanilla-sources
    config_method: str = "genkernel"  # genkernel, manual, distribution
    initramfs: bool = True
    modules_autoload: bool = True
    firmware_install: bool = True
    compile_jobs: int = 0  # 0 = auto-detect


@dataclass
class BootloaderConfig:
    """Configuration for bootloader installation."""
    bootloader: str = "grub"  # grub, systemd-boot, lilo
    target: str = "x86_64-efi"  # x86_64-efi, i386-pc
    install_location: str = "/boot/efi"
    timeout: int = 5
    additional_params: List[str] = field(default_factory=list)


@dataclass
class SystemConfig:
    """Configuration for system settings."""
    hostname: str = "gentoo"
    timezone: str = "UTC"
    locale: str = "en_US.UTF-8"
    keymap: str = "us"
    root_password: Optional[str] = None
    create_user: bool = True
    username: str = "user"
    user_password: Optional[str] = None
    enable_ssh: bool = False
    install_desktop: bool = False
    desktop_environment: str = "xfce"  # xfce, kde, gnome


@dataclass
class NetworkConfig:
    """Configuration for network settings."""
    interface: str = "auto"
    dhcp: bool = True
    static_ip: Optional[str] = None
    netmask: Optional[str] = None
    gateway: Optional[str] = None
    dns_servers: List[str] = field(default_factory=lambda: ["8.8.8.8", "8.8.4.4"])
    hostname_resolution: bool = True


@dataclass
class AppConfig:
    """Main application configuration."""
    # Application settings
    dry_run: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    
    # Installation configuration
    disk: DiskConfig = field(default_factory=DiskConfig)
    stage3: Stage3Config = field(default_factory=Stage3Config)
    portage: PortageConfig = field(default_factory=PortageConfig)
    kernel: KernelConfig = field(default_factory=KernelConfig)
    bootloader: BootloaderConfig = field(default_factory=BootloaderConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    
    # Paths
    mount_point: str = "/mnt/gentoo"
    work_dir: str = "/tmp/gentooui"


# Marshmallow schemas for validation
class DiskConfigSchema(Schema):
    target_disk = fields.Str()
    partition_scheme = fields.Str(validate=lambda x: x in ["gpt", "mbr"])
    boot_partition_size = fields.Str()
    swap_size = fields.Str()
    root_filesystem = fields.Str(validate=lambda x: x in ["ext4", "xfs", "btrfs"])
    encryption_enabled = fields.Bool()
    encryption_cipher = fields.Str()
    
    @post_load
    def make_config(self, data, **kwargs):
        return DiskConfig(**data)


class Stage3ConfigSchema(Schema):
    mirror_url = fields.Url()
    architecture = fields.Str()
    variant = fields.Str()
    auto_select = fields.Bool()
    verify_signature = fields.Bool()
    
    @post_load
    def make_config(self, data, **kwargs):
        return Stage3Config(**data)


class PortageConfigSchema(Schema):
    make_opts = fields.Str()
    use_flags = fields.List(fields.Str())
    accept_keywords = fields.List(fields.Str())
    mirrors = fields.List(fields.Url())
    emerge_opts = fields.Str()
    
    @post_load
    def make_config(self, data, **kwargs):
        return PortageConfig(**data)


class AppConfigSchema(Schema):
    dry_run = fields.Bool()
    verbose = fields.Bool()
    log_level = fields.Str(validate=lambda x: x in ["DEBUG", "INFO", "WARNING", "ERROR"])
    
    disk = fields.Nested(DiskConfigSchema)
    stage3 = fields.Nested(Stage3ConfigSchema)
    portage = fields.Nested(PortageConfigSchema)
    # ... other nested schemas
    
    mount_point = fields.Str()
    work_dir = fields.Str()
    
    @post_load
    def make_config(self, data, **kwargs):
        return AppConfig(**data)


class ConfigManager:
    """
    Manages application configuration loading, validation, and saving.
    """
    
    def __init__(self):
        self.schema = AppConfigSchema()
        logger.info("ConfigManager initialized")
    
    def get_default_config(self) -> AppConfig:
        """Get the default application configuration."""
        logger.info("Creating default configuration")
        return AppConfig()
    
    def load_config(self, config_path: Path) -> AppConfig:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Validated AppConfig instance
            
        Raises:
            ValidationError: If configuration is invalid
            FileNotFoundError: If configuration file doesn't exist
        """
        logger.info(f"Loading configuration from {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if config_data is None:
                logger.warning("Configuration file is empty, using defaults")
                return self.get_default_config()
            
            # Validate and create config
            config = self.schema.load(config_data)
            logger.info("Configuration loaded and validated successfully")
            return config
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            raise ValidationError(f"Invalid YAML format: {e}")
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise
    
    def save_config(self, config: AppConfig, config_path: Path) -> None:
        """
        Save configuration to a YAML file.
        
        Args:
            config: Configuration to save
            config_path: Path where to save the configuration
        """
        logger.info(f"Saving configuration to {config_path}")
        
        try:
            config_data = self.schema.dump(config)
            
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config_data, f, default_flow_style=False, indent=2)
            
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def validate_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration data.
        
        Args:
            config_data: Raw configuration data
            
        Returns:
            Validated configuration data
            
        Raises:
            ValidationError: If configuration is invalid
        """
        try:
            return self.schema.load(config_data)
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def merge_configs(self, base_config: AppConfig, override_data: Dict[str, Any]) -> AppConfig:
        """
        Merge configuration overrides with base configuration.
        
        Args:
            base_config: Base configuration
            override_data: Data to override
            
        Returns:
            Merged configuration
        """
        logger.info("Merging configuration overrides")
        
        # Convert base config to dict
        base_data = self.schema.dump(base_config)
        
        # Deep merge override data
        def deep_merge(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        merged_data = deep_merge(base_data, override_data)
        
        # Validate and return
        return self.schema.load(merged_data)
