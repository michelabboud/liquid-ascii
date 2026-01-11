"""Preset management system

Save and load configuration presets.
"""

import json
from pathlib import Path

from .schema import AppConfig


class PresetManager:
    """
    Manager for configuration presets.

    Presets are stored in ~/.config/liquid-ascii/presets/
    """

    def __init__(self, presets_dir: Path | None = None):
        """
        Initialize preset manager.

        Args:
            presets_dir: Custom presets directory (defaults to ~/.config/liquid-ascii/presets)
        """
        if presets_dir is None:
            config_home = Path.home() / ".config" / "liquid-ascii"
            self.presets_dir = config_home / "presets"
        else:
            self.presets_dir = Path(presets_dir)

        # Create directory if it doesn't exist
        self.presets_dir.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, config: AppConfig, description: str | None = None):
        """
        Save a configuration preset.

        Args:
            name: Preset name (alphanumeric + dash/underscore only)
            config: Configuration to save
            description: Optional preset description

        Raises:
            ValueError: If preset name is invalid
        """
        # Validate preset name
        if not name or not name.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                f"Invalid preset name: {name}. Use alphanumeric characters, dashes, and underscores only."
            )

        preset_path = self.presets_dir / f"{name}.json"

        preset_data = {
            "name": name,
            "description": description or f"Custom preset: {name}",
            "config": config.to_dict(),
        }

        with open(preset_path, "w", encoding="utf-8") as f:
            json.dump(preset_data, f, indent=2)

    def load(self, name: str) -> AppConfig:
        """
        Load a configuration preset.

        Args:
            name: Preset name

        Returns:
            Loaded configuration

        Raises:
            FileNotFoundError: If preset doesn't exist
        """
        preset_path = self.presets_dir / f"{name}.json"

        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {name}")

        with open(preset_path, encoding="utf-8") as f:
            preset_data = json.load(f)

        return AppConfig.from_dict(preset_data["config"])

    def list(self) -> list[dict[str, str]]:
        """
        List available presets.

        Returns:
            List of preset info dicts with 'name' and 'description' keys
        """
        presets = []

        for preset_file in self.presets_dir.glob("*.json"):
            try:
                with open(preset_file, encoding="utf-8") as f:
                    preset_data = json.load(f)

                presets.append(
                    {
                        "name": preset_data.get("name", preset_file.stem),
                        "description": preset_data.get("description", "No description"),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                # Skip invalid preset files
                continue

        return sorted(presets, key=lambda p: p["name"])

    def delete(self, name: str):
        """
        Delete a preset.

        Args:
            name: Preset name

        Raises:
            FileNotFoundError: If preset doesn't exist
        """
        preset_path = self.presets_dir / f"{name}.json"

        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {name}")

        preset_path.unlink()

    def exists(self, name: str) -> bool:
        """
        Check if preset exists.

        Args:
            name: Preset name

        Returns:
            True if preset exists
        """
        preset_path = self.presets_dir / f"{name}.json"
        return preset_path.exists()


# Convenience functions using default preset manager

_default_manager: PresetManager | None = None


def _get_default_manager() -> PresetManager:
    """Get or create default preset manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = PresetManager()
    return _default_manager


def save_preset(name: str, config: AppConfig, description: str | None = None):
    """
    Save a configuration preset.

    Args:
        name: Preset name
        config: Configuration to save
        description: Optional preset description
    """
    manager = _get_default_manager()
    manager.save(name, config, description)


def load_preset(name: str) -> AppConfig:
    """
    Load a configuration preset.

    Args:
        name: Preset name

    Returns:
        Loaded configuration
    """
    manager = _get_default_manager()
    return manager.load(name)


def list_presets() -> list[dict[str, str]]:
    """
    List available presets.

    Returns:
        List of preset info dicts
    """
    manager = _get_default_manager()
    return manager.list()


def delete_preset(name: str):
    """
    Delete a preset.

    Args:
        name: Preset name
    """
    manager = _get_default_manager()
    manager.delete(name)


def preset_exists(name: str) -> bool:
    """
    Check if preset exists.

    Args:
        name: Preset name

    Returns:
        True if preset exists
    """
    manager = _get_default_manager()
    return manager.exists(name)
