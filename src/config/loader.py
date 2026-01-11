"""Configuration file loader

Supports YAML and JSON formats with multi-location resolution.
"""

import json
import os
from pathlib import Path

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from .schema import AppConfig


class ConfigLoader:
    """
    Configuration file loader.

    Supports YAML and JSON formats, with automatic format detection.
    """

    CONFIG_FILENAMES = [
        ".liquid-ascii.yaml",
        ".liquid-ascii.yml",
        ".liquid-ascii.json",
        "liquid-ascii.yaml",
        "liquid-ascii.yml",
        "liquid-ascii.json",
    ]

    @staticmethod
    def find_config_file(
        explicit_path: str | None = None,
    ) -> Path | None:
        """
        Find configuration file.

        Search order:
        1. Explicit path (if provided)
        2. Current working directory
        3. User home directory
        4. System config directory (/etc on Linux)

        Args:
            explicit_path: Explicit config file path

        Returns:
            Path to config file, or None if not found
        """
        # 1. Explicit path
        if explicit_path:
            path = Path(explicit_path)
            if path.exists():
                return path
            return None

        # 2. Current working directory
        cwd = Path.cwd()
        for filename in ConfigLoader.CONFIG_FILENAMES:
            config_path = cwd / filename
            if config_path.exists():
                return config_path

        # 3. User home directory
        home = Path.home()
        for filename in ConfigLoader.CONFIG_FILENAMES:
            config_path = home / filename
            if config_path.exists():
                return config_path

        # 4. System config directory
        if os.name != "nt":  # Not Windows
            system_config = Path("/etc/liquid-ascii")
            for filename in ConfigLoader.CONFIG_FILENAMES:
                config_path = system_config / filename
                if config_path.exists():
                    return config_path

        return None

    @staticmethod
    def load(path: Path) -> AppConfig:
        """
        Load configuration from file.

        Args:
            path: Path to config file

        Returns:
            Loaded configuration

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported or invalid
        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        # Detect format from extension
        suffix = path.suffix.lower()

        if suffix in [".yaml", ".yml"]:
            if not HAS_YAML:
                raise ValueError("YAML support requires PyYAML: pip install pyyaml")
            return ConfigLoader._load_yaml(path)
        elif suffix == ".json":
            return ConfigLoader._load_json(path)
        else:
            raise ValueError(f"Unsupported config format: {suffix}")

    @staticmethod
    def _load_yaml(path: Path) -> AppConfig:
        """Load YAML configuration."""
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError("Config file must contain a YAML object")

        return AppConfig.from_dict(data)

    @staticmethod
    def _load_json(path: Path) -> AppConfig:
        """Load JSON configuration."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Config file must contain a JSON object")

        return AppConfig.from_dict(data)

    @staticmethod
    def save(config: AppConfig, path: Path):
        """
        Save configuration to file.

        Args:
            config: Configuration to save
            path: Path to save to

        Raises:
            ValueError: If file format is unsupported
        """
        suffix = path.suffix.lower()

        if suffix in [".yaml", ".yml"]:
            if not HAS_YAML:
                raise ValueError("YAML support requires PyYAML: pip install pyyaml")
            ConfigLoader._save_yaml(config, path)
        elif suffix == ".json":
            ConfigLoader._save_json(config, path)
        else:
            raise ValueError(f"Unsupported config format: {suffix}")

    @staticmethod
    def _save_yaml(config: AppConfig, path: Path):
        """Save YAML configuration."""
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)

    @staticmethod
    def _save_json(config: AppConfig, path: Path):
        """Save JSON configuration."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2)


def find_config_file(explicit_path: str | None = None) -> Path | None:
    """
    Find configuration file.

    Convenience wrapper around ConfigLoader.find_config_file().

    Args:
        explicit_path: Explicit config file path

    Returns:
        Path to config file, or None if not found
    """
    return ConfigLoader.find_config_file(explicit_path)


def load_config(path: Path | None = None) -> AppConfig | None:
    """
    Load configuration from file.

    Args:
        path: Path to config file (optional, will search if not provided)

    Returns:
        Loaded configuration, or None if no config found
    """
    if path is None:
        path = find_config_file()
        if path is None:
            return None

    return ConfigLoader.load(path)
