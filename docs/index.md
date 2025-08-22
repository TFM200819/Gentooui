# GentooUI Documentation

Welcome to GentooUI, a modern Text User Interface (TUI) for installing Gentoo Linux.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Installation Process](#installation-process)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Installation

### From Source

```bash
git clone https://github.com/yourusername/gentooui.git
cd gentooui
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/gentooui.git
cd gentooui
./scripts/install-dev.sh
```

## Quick Start

1. **Boot from Gentoo LiveCD/LiveUSB**
2. **Install GentooUI**:
   ```bash
   pip install gentooui
   ```
3. **Run the installer**:
   ```bash
   sudo gentooui
   ```

## Configuration

GentooUI can be configured using YAML configuration files. See the `configs/examples/` directory for sample configurations.

### Desktop Installation
```bash
gentooui --config configs/examples/desktop.yaml
```

### Server Installation
```bash
gentooui --config configs/examples/server.yaml
```

## Installation Process

GentooUI follows the standard Gentoo installation process with these steps:

1. **Welcome Screen** - System information and configuration review
2. **Disk Setup** - Partition and format target disk
3. **Stage3** - Download and extract base system
4. **Configuration** - System and network configuration
5. **Kernel** - Install and configure kernel
6. **Bootloader** - Install bootloader (GRUB/systemd-boot)
7. **Finalization** - Complete installation and cleanup

## Features

- 📱 **Modern TUI** - Clean, intuitive interface built with Textual
- 🎯 **Guided Installation** - Step-by-step process with validation
- ⚡ **Automated Tasks** - Intelligent automation with manual override options
- 🔧 **Flexible Configuration** - YAML-based configuration with profiles
- 📊 **Real-time Progress** - Live progress monitoring and logging
- 🔍 **System Detection** - Automatic hardware and system detection
- 💾 **Multiple Profiles** - Desktop, server, and custom installation profiles
- 🛡️ **Safety Features** - Dry-run mode and validation checks

## System Requirements

- **Operating System**: Linux (preferably Gentoo LiveCD)
- **Python**: 3.8 or higher
- **Privileges**: Root access required for installation
- **Memory**: Minimum 1GB RAM (2GB+ recommended)
- **Storage**: Minimum 20GB free space

## Command Line Options

```
Usage: gentooui [OPTIONS]

Options:
  -c, --config PATH       Path to configuration file
  -l, --log-level LEVEL   Set logging level (DEBUG, INFO, WARNING, ERROR)
  --log-file PATH         Path to log file
  --dry-run               Run in dry-run mode (no actual changes)
  --skip-checks           Skip prerequisite checks (dangerous!)
  --help                  Show this message and exit
```

## Troubleshooting

### Common Issues

**Permission Denied**
- Ensure you're running as root: `sudo gentooui`

**Missing Dependencies**
- Install required system tools: `emerge -av fdisk parted mkfs.ext4`

**Network Issues**
- Check internet connectivity before starting installation

### Log Files

GentooUI creates detailed logs at:
- Console output with colored formatting
- File output at `./gentooui.log` (default) or specified path

### Debug Mode

Run with debug logging for detailed information:
```bash
gentooui --log-level DEBUG
```

## Development

### Setting up Development Environment

```bash
git clone https://github.com/yourusername/gentooui.git
cd gentooui
./scripts/install-dev.sh
source .venv/bin/activate
```

### Running Tests

```bash
pytest
pytest --cov=gentooui  # With coverage
```

### Code Formatting

```bash
black src/
flake8 src/
mypy src/
```

### Project Structure

```
gentooui/
├── src/gentooui/           # Main application source
│   ├── core/               # Core application modules
│   ├── installers/         # Installation step implementations
│   ├── screens/            # TUI screens
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── configs/examples/       # Configuration examples
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run the test suite: `pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

- **Documentation**: [Project Documentation]
- **Issues**: [GitHub Issues](https://github.com/yourusername/gentooui/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/gentooui/discussions)

## Disclaimer

⚠️ **Important**: This tool performs system-level operations that can result in data loss. Always:

- Backup your data before running
- Test in a virtual machine first
- Read and understand the configuration before proceeding
- Use dry-run mode to preview changes

The developers are not responsible for any data loss or system damage.
