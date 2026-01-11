"""Configuration system for Liquid ASCII

Supports YAML/JSON config files with preset management.
"""

from .loader import ConfigLoader, load_config, find_config_file
from .presets import PresetManager, save_preset, load_preset, list_presets
from .schema import AppConfig, RenderConfig, EffectsConfig, CharacterConfig, ChatConfig

__all__ = [
    # Loader
    "ConfigLoader",
    "load_config",
    "find_config_file",
    # Presets
    "PresetManager",
    "save_preset",
    "load_preset",
    "list_presets",
    # Schema
    "AppConfig",
    "RenderConfig",
    "EffectsConfig",
    "CharacterConfig",
    "ChatConfig",
]
