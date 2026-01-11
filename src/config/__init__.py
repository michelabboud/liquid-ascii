"""Configuration system for Liquid ASCII

Supports YAML/JSON config files with preset management.
"""

from .loader import ConfigLoader, find_config_file, load_config
from .presets import PresetManager, list_presets, load_preset, save_preset
from .schema import AppConfig, CharacterConfig, ChatConfig, EffectsConfig, RenderConfig

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
