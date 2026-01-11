"""Configuration schema definitions

Defines the structure of configuration files using dataclasses.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any


@dataclass
class EffectsConfig:
    """Visual effects configuration."""

    particles: bool = False
    max_particles: int = 50
    trails: bool = False
    trail_length: int = 5
    glitch: bool = False
    glitch_intensity: float = 0.1
    scanlines: bool = False
    scanline_intensity: float = 0.5
    matrix_rain: bool = False
    matrix_density: float = 0.3
    depth_of_field: bool = False
    dof_focus: float = 3.5
    dof_strength: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EffectsConfig":
        """Create from dictionary."""
        # Filter out unknown keys
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class RenderConfig:
    """Rendering configuration."""

    quality: str = "high"
    fps: float = 15.0
    color_scheme: str = "default"
    rainbow_mode: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RenderConfig":
        """Create from dictionary."""
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class CharacterConfig:
    """Character configuration."""

    character: str = "default"
    expression: Optional[str] = None
    voice: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterConfig":
        """Create from dictionary."""
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class ChatConfig:
    """Chat mode configuration."""

    llm_backend: str = "ollama"
    llm_model: Optional[str] = None
    enable_voice: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatConfig":
        """Create from dictionary."""
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class AppConfig:
    """Main application configuration."""

    render: RenderConfig = field(default_factory=RenderConfig)
    character: CharacterConfig = field(default_factory=CharacterConfig)
    effects: EffectsConfig = field(default_factory=EffectsConfig)
    chat: ChatConfig = field(default_factory=ChatConfig)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "render": self.render.to_dict(),
            "character": self.character.to_dict(),
            "effects": self.effects.to_dict(),
            "chat": self.chat.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """Create from dictionary."""
        render = RenderConfig.from_dict(data.get("render", {}))
        character = CharacterConfig.from_dict(data.get("character", {}))
        effects = EffectsConfig.from_dict(data.get("effects", {}))
        chat = ChatConfig.from_dict(data.get("chat", {}))

        return cls(
            render=render,
            character=character,
            effects=effects,
            chat=chat,
        )

    def merge(self, other: "AppConfig") -> "AppConfig":
        """
        Merge with another config, preferring values from other.

        Args:
            other: Config to merge from

        Returns:
            New merged config
        """
        merged_dict = self.to_dict()

        # Deep merge each section
        for section in ["render", "character", "effects", "chat"]:
            if section in other.to_dict():
                other_section = other.to_dict()[section]
                merged_dict[section].update(
                    {k: v for k, v in other_section.items() if v is not None}
                )

        return AppConfig.from_dict(merged_dict)
