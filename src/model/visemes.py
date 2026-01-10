"""
Viseme definitions for lip sync animation.

Visemes are the visual representation of phonemes (speech sounds).
This module defines mouth shapes that correspond to different sounds.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class Viseme(Enum):
    """
    Standard viseme set for speech animation.

    Based on common viseme groupings used in animation software.
    """
    # Silence / rest
    X = "X"  # Neutral rest position

    # Open vowels
    A = "A"  # ah, aw, ay - wide open mouth
    E = "E"  # ee, i - narrow/wide smile
    O = "O"  # oh, oo, w - round pursed lips

    # Closed consonants
    B = "B"  # b, m, p - lips closed
    F = "F"  # f, v - lower lip tucked under upper teeth

    # Partial open
    C = "C"  # d, t, n, k, g, ng, y, h - teeth visible, tongue at roof
    D = "D"  # th - tongue between teeth
    H = "H"  # l, r - relaxed open, tongue visible

    # Extended set
    I = "I"  # ch, j, sh, zh - lips slightly puckered
    U = "U"  # uh, schwa - relaxed small opening


@dataclass
class VisemeShape:
    """
    Parameters defining a mouth shape for a viseme.
    """
    mouth_openness: float  # 0 = closed, 1 = wide open
    mouth_width: float     # 0 = narrow, 1 = wide (smile)
    lip_pucker: float      # 0 = relaxed, 1 = pursed
    jaw_offset: float      # Vertical jaw displacement
    tongue_visible: float  # 0 = hidden, 1 = visible
    teeth_visible: float   # 0 = hidden, 1 = visible

    def lerp_to(self, other: "VisemeShape", t: float) -> "VisemeShape":
        """Interpolate between two viseme shapes."""
        return VisemeShape(
            mouth_openness=self.mouth_openness + (other.mouth_openness - self.mouth_openness) * t,
            mouth_width=self.mouth_width + (other.mouth_width - self.mouth_width) * t,
            lip_pucker=self.lip_pucker + (other.lip_pucker - self.lip_pucker) * t,
            jaw_offset=self.jaw_offset + (other.jaw_offset - self.jaw_offset) * t,
            tongue_visible=self.tongue_visible + (other.tongue_visible - self.tongue_visible) * t,
            teeth_visible=self.teeth_visible + (other.teeth_visible - self.teeth_visible) * t,
        )


# Viseme shape definitions
VISEME_SHAPES: Dict[Viseme, VisemeShape] = {
    Viseme.X: VisemeShape(
        mouth_openness=0.05,
        mouth_width=0.5,
        lip_pucker=0.0,
        jaw_offset=0.0,
        tongue_visible=0.0,
        teeth_visible=0.0,
    ),
    Viseme.A: VisemeShape(
        mouth_openness=0.9,
        mouth_width=0.7,
        lip_pucker=0.0,
        jaw_offset=-0.15,
        tongue_visible=0.3,
        teeth_visible=0.5,
    ),
    Viseme.E: VisemeShape(
        mouth_openness=0.35,
        mouth_width=0.9,
        lip_pucker=0.0,
        jaw_offset=-0.05,
        tongue_visible=0.1,
        teeth_visible=0.8,
    ),
    Viseme.O: VisemeShape(
        mouth_openness=0.5,
        mouth_width=0.3,
        lip_pucker=0.8,
        jaw_offset=-0.1,
        tongue_visible=0.0,
        teeth_visible=0.0,
    ),
    Viseme.B: VisemeShape(
        mouth_openness=0.0,
        mouth_width=0.5,
        lip_pucker=0.3,
        jaw_offset=0.0,
        tongue_visible=0.0,
        teeth_visible=0.0,
    ),
    Viseme.F: VisemeShape(
        mouth_openness=0.15,
        mouth_width=0.5,
        lip_pucker=0.1,
        jaw_offset=0.0,
        tongue_visible=0.0,
        teeth_visible=0.6,
    ),
    Viseme.C: VisemeShape(
        mouth_openness=0.3,
        mouth_width=0.5,
        lip_pucker=0.0,
        jaw_offset=-0.05,
        tongue_visible=0.5,
        teeth_visible=0.9,
    ),
    Viseme.D: VisemeShape(
        mouth_openness=0.25,
        mouth_width=0.5,
        lip_pucker=0.0,
        jaw_offset=-0.03,
        tongue_visible=0.9,
        teeth_visible=0.7,
    ),
    Viseme.H: VisemeShape(
        mouth_openness=0.4,
        mouth_width=0.6,
        lip_pucker=0.0,
        jaw_offset=-0.08,
        tongue_visible=0.4,
        teeth_visible=0.3,
    ),
    Viseme.I: VisemeShape(
        mouth_openness=0.25,
        mouth_width=0.4,
        lip_pucker=0.5,
        jaw_offset=-0.03,
        tongue_visible=0.2,
        teeth_visible=0.5,
    ),
    Viseme.U: VisemeShape(
        mouth_openness=0.2,
        mouth_width=0.45,
        lip_pucker=0.2,
        jaw_offset=-0.02,
        tongue_visible=0.1,
        teeth_visible=0.2,
    ),
}


# Phoneme to viseme mapping (common English phonemes)
PHONEME_TO_VISEME: Dict[str, Viseme] = {
    # Silence
    "sil": Viseme.X,
    "sp": Viseme.X,
    "": Viseme.X,

    # Open vowels (A)
    "AA": Viseme.A,  # odd
    "AE": Viseme.A,  # at
    "AH": Viseme.A,  # hut
    "AO": Viseme.A,  # ought
    "AW": Viseme.A,  # cow
    "AY": Viseme.A,  # hide

    # Smile vowels (E)
    "EH": Viseme.E,  # Ed
    "EY": Viseme.E,  # ate
    "IH": Viseme.E,  # it
    "IY": Viseme.E,  # eat

    # Round vowels (O)
    "OW": Viseme.O,  # oat
    "OY": Viseme.O,  # toy
    "UH": Viseme.O,  # hood
    "UW": Viseme.O,  # two
    "W": Viseme.O,

    # Closed consonants (B)
    "B": Viseme.B,
    "M": Viseme.B,
    "P": Viseme.B,

    # Lip-teeth (F)
    "F": Viseme.F,
    "V": Viseme.F,

    # Teeth visible (C)
    "D": Viseme.C,
    "T": Viseme.C,
    "N": Viseme.C,
    "K": Viseme.C,
    "G": Viseme.C,
    "NG": Viseme.C,
    "Y": Viseme.C,
    "HH": Viseme.C,
    "S": Viseme.C,
    "Z": Viseme.C,

    # Tongue between teeth (D)
    "TH": Viseme.D,
    "DH": Viseme.D,

    # Relaxed open (H)
    "L": Viseme.H,
    "R": Viseme.H,
    "ER": Viseme.H,

    # Puckered (I)
    "CH": Viseme.I,
    "JH": Viseme.I,
    "SH": Viseme.I,
    "ZH": Viseme.I,
}

# Rhubarb lip sync output to viseme mapping
RHUBARB_TO_VISEME: Dict[str, Viseme] = {
    "X": Viseme.X,
    "A": Viseme.B,  # Rhubarb A = closed mouth (m, b, p)
    "B": Viseme.A,  # Rhubarb B = open mouth (vowels)
    "C": Viseme.E,  # Rhubarb C = teeth visible (e, i)
    "D": Viseme.O,  # Rhubarb D = round (o, u)
    "E": Viseme.O,  # Rhubarb E = slightly round
    "F": Viseme.F,  # Rhubarb F = f, v
    "G": Viseme.C,  # Rhubarb G = teeth together
    "H": Viseme.H,  # Rhubarb H = L position
}


@dataclass
class VisemeCue:
    """A single viseme timing cue."""
    start_time: float
    end_time: float
    viseme: Viseme

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


class VisemeController:
    """
    Controls viseme state and transitions for lip sync.
    """

    def __init__(
        self,
        transition_time: float = 0.05,
        idle_viseme: Viseme = Viseme.X,
    ):
        """
        Initialize the viseme controller.

        Args:
            transition_time: Time to transition between visemes
            idle_viseme: Default viseme when not speaking
        """
        self.transition_time = transition_time
        self.idle_viseme = idle_viseme

        self.cues: List[VisemeCue] = []
        self.current_shape = VISEME_SHAPES[idle_viseme]
        self.target_shape = VISEME_SHAPES[idle_viseme]
        self.current_viseme = idle_viseme
        self._transition_progress = 1.0

    def load_cues(self, cues: List[VisemeCue]):
        """Load a sequence of viseme cues."""
        self.cues = sorted(cues, key=lambda c: c.start_time)

    def load_rhubarb_json(self, data: dict):
        """
        Load cues from Rhubarb Lip Sync JSON output.

        Expected format:
        {
            "mouthCues": [
                {"start": 0.00, "end": 0.12, "value": "X"},
                ...
            ]
        }
        """
        cues = []
        for cue in data.get("mouthCues", []):
            viseme_str = cue.get("value", "X")
            viseme = RHUBARB_TO_VISEME.get(viseme_str, Viseme.X)
            cues.append(VisemeCue(
                start_time=cue["start"],
                end_time=cue["end"],
                viseme=viseme,
            ))
        self.load_cues(cues)

    def get_viseme_at_time(self, t: float) -> Viseme:
        """Get the viseme that should be active at time t."""
        for cue in self.cues:
            if cue.start_time <= t < cue.end_time:
                return cue.viseme
        return self.idle_viseme

    def update(self, t: float, dt: float) -> VisemeShape:
        """
        Update viseme state based on current time.

        Args:
            t: Current playback time
            dt: Time since last update

        Returns:
            Current viseme shape (interpolated)
        """
        target_viseme = self.get_viseme_at_time(t)

        if target_viseme != self.current_viseme:
            # Start transition to new viseme
            self.current_viseme = target_viseme
            self.target_shape = VISEME_SHAPES[target_viseme]
            self._transition_progress = 0.0

        if self._transition_progress < 1.0:
            # Continue transition
            self._transition_progress += dt / self.transition_time
            self._transition_progress = min(1.0, self._transition_progress)

            # Smooth interpolation
            t_smooth = self._transition_progress * self._transition_progress * (3 - 2 * self._transition_progress)
            self.current_shape = self.current_shape.lerp_to(self.target_shape, t_smooth)

        return self.current_shape

    def get_mouth_openness(self, t: float) -> float:
        """
        Simple method to get just mouth openness at time t.

        Useful for basic animation without full viseme shapes.
        """
        viseme = self.get_viseme_at_time(t)
        return VISEME_SHAPES[viseme].mouth_openness

    def reset(self):
        """Reset to idle state."""
        self.current_shape = VISEME_SHAPES[self.idle_viseme]
        self.target_shape = VISEME_SHAPES[self.idle_viseme]
        self.current_viseme = self.idle_viseme
        self._transition_progress = 1.0


def simple_text_to_visemes(
    text: str,
    duration: float,
    words_per_minute: float = 150.0,
) -> List[VisemeCue]:
    """
    Generate approximate viseme cues from text without TTS.

    This is a simple fallback when proper phoneme data isn't available.
    It estimates timing based on character count and alternates between
    open and closed mouth shapes.

    Args:
        text: Text to generate cues for
        duration: Total duration in seconds
        words_per_minute: Speaking rate

    Returns:
        List of viseme cues
    """
    cues = []

    # Simple syllable estimation
    vowels = set("aeiouAEIOU")
    words = text.split()

    if not words:
        return [VisemeCue(0, duration, Viseme.X)]

    # Estimate syllables
    syllables = []
    for word in words:
        word_syllables = 0
        prev_was_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                word_syllables += 1
            prev_was_vowel = is_vowel
        syllables.append(max(1, word_syllables))

    total_syllables = sum(syllables)
    time_per_syllable = duration / total_syllables if total_syllables > 0 else duration

    # Generate cues
    current_time = 0.0
    viseme_cycle = [Viseme.A, Viseme.B, Viseme.E, Viseme.B]

    syllable_idx = 0
    for word_syllables in syllables:
        for _ in range(word_syllables):
            viseme = viseme_cycle[syllable_idx % len(viseme_cycle)]
            cues.append(VisemeCue(
                start_time=current_time,
                end_time=current_time + time_per_syllable * 0.8,
                viseme=viseme,
            ))
            # Brief closure between syllables
            cues.append(VisemeCue(
                start_time=current_time + time_per_syllable * 0.8,
                end_time=current_time + time_per_syllable,
                viseme=Viseme.X,
            ))
            current_time += time_per_syllable
            syllable_idx += 1

    return cues
