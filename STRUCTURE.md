# GentooUI Project Structure

This document provides an overview of the GentooUI project structure and organization.

## Directory Structure

```
gentooui/
├── src/gentooui/           # Main application source code
│   ├── __init__.py         # Package initialization
│   ├── main.py             # Application entry point
│   ├── core/               # Core application modules
│   │   ├── __init__.py
│   │   ├── app.py          # Main TUI application class
│   │   ├── config.py       # Configuration management
│   │   ├── installer.py    # Installation orchestration
│   │   └── logger.py       # Logging configuration
│   ├── installers/         # Installation step implementations
│   │   ├── __init__.py
│   │   ├── disk.py         # Disk partitioning and formatting
│   │   ├── stage3.py       # Stage3 download and extraction
│   │   ├── portage.py      # Portage configuration
│   │   ├── kernel.py       # Kernel installation and configuration
│   │   ├── bootloader.py   # Bootloader installation
│   │   └── system.py       # System configuration
│   ├── screens/            # TUI screen components
│   │   ├── __init__.py
│   │   ├── welcome.py      # Welcome screen
│   │   ├── disk_setup.py   # Disk setup screen
│   │   ├── stage3.py       # Stage3 screen
│   │   ├── configuration.py # Configuration screen
│   │   ├── kernel.py       # Kernel screen
│   │   ├── bootloader.py   # Bootloader screen
│   │   ├── finalization.py # Finalization screen
│   │   └── progress.py     # Progress monitoring screen
│   └── utils/              # Utility functions and helpers
│       ├── __init__.py
│       └── system.py       # System utility functions
├── tests/                  # Test suite
│   ├── conftest.py         # PyTest configuration and fixtures
│   ├── test_config.py      # Configuration tests
│   ├── test_system.py      # System utility tests
│   └── ...                 # Additional test files
├── configs/                # Configuration files and templates
│   └── examples/           # Example configuration files
│       ├── desktop.yaml    # Desktop installation configuration
│       └── server.yaml     # Server installation configuration
├── docs/                   # Documentation
│   └── index.md            # Main documentation file
├── scripts/                # Utility scripts
│   └── install-dev.sh      # Development environment setup
├── setup.py                # Package setup (legacy)
├── pyproject.toml          # Modern package configuration
├── requirements.txt        # Package dependencies
├── README.md               # Project overview and instructions
├── LICENSE                 # License file
├── .gitignore              # Git ignore patterns
└── STRUCTURE.md            # This file
```

## Module Organization

### Core Modules (`src/gentooui/core/`)

- **`app.py`**: Main Textual application class that manages the TUI interface and coordinates between different screens
- **`config.py`**: Configuration management including data classes, validation schemas, and file I/O
- **`installer.py`**: Installation orchestration that manages the overall installation process
- **`logger.py`**: Logging configuration with Rich integration for colored terminal output

### Installation Modules (`src/gentooui/installers/`)

Each installer module handles a specific phase of the Gentoo installation:

- **`disk.py`**: Disk operations (partitioning, formatting, mounting)
- **`stage3.py`**: Stage3 tarball download, verification, and extraction
- **`portage.py`**: Portage configuration (make.conf, package.use, etc.)
- **`kernel.py`**: Kernel source installation, configuration, and compilation
- **`bootloader.py`**: Bootloader installation and configuration
- **`system.py`**: Basic system configuration (hostname, locale, users, etc.)

### Screen Modules (`src/gentooui/screens/`)

TUI screen components built with Textual framework:

- **`welcome.py`**: Initial screen showing system information and configuration options
- **`disk_setup.py`**: Interactive disk partitioning interface
- **`stage3.py`**: Stage3 selection and download progress
- **`configuration.py`**: System configuration forms and inputs
- **`kernel.py`**: Kernel configuration and compilation progress
- **`bootloader.py`**: Bootloader setup and configuration
- **`finalization.py`**: Final steps and completion screen
- **`progress.py`**: Real-time progress monitoring for long-running operations

### Utility Modules (`src/gentooui/utils/`)

- **`system.py`**: System utility functions (hardware detection, command execution, validation)

## Configuration System

The configuration system uses a hierarchical structure with YAML files:

1. **Default Configuration**: Built into the application with sensible defaults
2. **User Configuration**: YAML files that override defaults
3. **Runtime Configuration**: Command-line arguments that override file-based config

Configuration classes are defined in `core/config.py` with full validation using Marshmallow schemas.

## Installation Flow

1. **Welcome** → System information display and configuration loading
2. **Disk Setup** → Partition and format target disk
3. **Stage3** → Download and extract base Gentoo system
4. **Configuration** → Configure system settings (hostname, locale, users)
5. **Kernel** → Install kernel sources and compile
6. **Bootloader** → Install and configure bootloader
7. **Finalization** → Complete installation and cleanup

## Testing Strategy

- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Testing interaction between components
- **Mock Testing**: Using mocks for system operations to enable safe testing
- **Fixture-based Testing**: PyTest fixtures for common test data and configurations

## Development Workflow

1. **Setup**: Use `scripts/install-dev.sh` for development environment
2. **Coding**: Follow project structure and coding standards
3. **Testing**: Add tests for new functionality
4. **Documentation**: Update documentation for changes
5. **Integration**: Test with example configurations

## Key Design Principles

- **Modularity**: Each component has a single responsibility
- **Testability**: Code is designed to be easily testable with mocks
- **Configuration-driven**: Behavior controlled through YAML configuration
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Logging**: Detailed logging for debugging and audit purposes
- **Safety**: Dry-run mode and validation to prevent accidental data loss
