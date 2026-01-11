"""Tests for viseme system and lip sync."""

import pytest

from src.model.visemes import (
    PHONEME_TO_VISEME,
    RHUBARB_TO_VISEME,
    VISEME_SHAPES,
    Viseme,
    VisemeCue,
    VisemeController,
    VisemeShape,
    simple_text_to_visemes,
)


class TestVisemeEnum:
    """Tests for Viseme enum."""

    def test_all_visemes_defined(self):
        """All expected visemes are defined."""
        expected = ["X", "A", "E", "O", "B", "F", "C", "D", "H", "I", "U"]
        for v in expected:
            assert hasattr(Viseme, v)

    def test_viseme_values(self):
        """Viseme values match their names."""
        assert Viseme.X.value == "X"
        assert Viseme.A.value == "A"
        assert Viseme.E.value == "E"


class TestVisemeShape:
    """Tests for VisemeShape dataclass."""

    def test_viseme_shape_creation(self):
        """VisemeShape can be created."""
        shape = VisemeShape(
            mouth_openness=0.5,
            mouth_width=0.7,
            lip_pucker=0.3,
            jaw_offset=-0.1,
            tongue_visible=0.2,
            teeth_visible=0.6,
        )
        assert shape.mouth_openness == 0.5
        assert shape.mouth_width == 0.7
        assert shape.lip_pucker == 0.3

    def test_lerp_to_at_zero(self):
        """Lerp at t=0 returns start shape."""
        start = VisemeShape(0.2, 0.3, 0.1, 0.0, 0.0, 0.0)
        end = VisemeShape(0.8, 0.9, 0.7, -0.1, 0.5, 0.8)

        result = start.lerp_to(end, 0.0)
        assert result.mouth_openness == 0.2
        assert result.mouth_width == 0.3
        assert result.lip_pucker == 0.1

    def test_lerp_to_at_one(self):
        """Lerp at t=1 returns end shape."""
        start = VisemeShape(0.2, 0.3, 0.1, 0.0, 0.0, 0.0)
        end = VisemeShape(0.8, 0.9, 0.7, -0.1, 0.5, 0.8)

        result = start.lerp_to(end, 1.0)
        assert result.mouth_openness == pytest.approx(0.8)
        assert result.mouth_width == pytest.approx(0.9)
        assert result.lip_pucker == pytest.approx(0.7)

    def test_lerp_to_at_half(self):
        """Lerp at t=0.5 returns midpoint."""
        start = VisemeShape(0.2, 0.4, 0.0, 0.0, 0.0, 0.0)
        end = VisemeShape(0.8, 0.8, 1.0, -0.2, 1.0, 1.0)

        result = start.lerp_to(end, 0.5)
        assert result.mouth_openness == pytest.approx(0.5)
        assert result.mouth_width == pytest.approx(0.6)
        assert result.lip_pucker == pytest.approx(0.5)
        assert result.jaw_offset == pytest.approx(-0.1)


class TestVisemeShapePresets:
    """Tests for VISEME_SHAPES dictionary."""

    def test_all_visemes_have_shapes(self):
        """All visemes have shape definitions."""
        for viseme in Viseme:
            assert viseme in VISEME_SHAPES

    def test_neutral_shape(self):
        """Neutral (X) shape is nearly closed."""
        shape = VISEME_SHAPES[Viseme.X]
        assert shape.mouth_openness < 0.1
        assert shape.lip_pucker == 0.0

    def test_a_shape_is_open(self):
        """A viseme is wide open."""
        shape = VISEME_SHAPES[Viseme.A]
        assert shape.mouth_openness > 0.7
        assert shape.mouth_width > 0.5

    def test_o_shape_is_puckered(self):
        """O viseme has pursed lips."""
        shape = VISEME_SHAPES[Viseme.O]
        assert shape.lip_pucker > 0.5

    def test_b_shape_is_closed(self):
        """B viseme is lips closed."""
        shape = VISEME_SHAPES[Viseme.B]
        assert shape.mouth_openness == 0.0

    def test_e_shape_has_wide_smile(self):
        """E viseme has wide smile."""
        shape = VISEME_SHAPES[Viseme.E]
        assert shape.mouth_width > 0.7

    def test_d_shape_shows_tongue(self):
        """D viseme (th) shows tongue."""
        shape = VISEME_SHAPES[Viseme.D]
        assert shape.tongue_visible > 0.5

    def test_all_shapes_valid_ranges(self):
        """All shape parameters in valid ranges."""
        for viseme, shape in VISEME_SHAPES.items():
            assert 0.0 <= shape.mouth_openness <= 1.0, f"{viseme}: mouth_openness"
            assert 0.0 <= shape.mouth_width <= 1.0, f"{viseme}: mouth_width"
            assert 0.0 <= shape.lip_pucker <= 1.0, f"{viseme}: lip_pucker"
            assert -1.0 <= shape.jaw_offset <= 1.0, f"{viseme}: jaw_offset"
            assert 0.0 <= shape.tongue_visible <= 1.0, f"{viseme}: tongue_visible"
            assert 0.0 <= shape.teeth_visible <= 1.0, f"{viseme}: teeth_visible"


class TestPhonemeMappings:
    """Tests for phoneme to viseme mappings."""

    def test_phoneme_mapping_exists(self):
        """PHONEME_TO_VISEME mapping exists."""
        assert len(PHONEME_TO_VISEME) > 0

    def test_common_phonemes_mapped(self):
        """Common English phonemes are mapped."""
        common = ["AA", "AE", "EH", "IH", "UW", "B", "M", "P", "F", "V", "TH"]
        for phoneme in common:
            assert phoneme in PHONEME_TO_VISEME

    def test_silence_phonemes(self):
        """Silence phonemes map to X."""
        assert PHONEME_TO_VISEME["sil"] == Viseme.X
        assert PHONEME_TO_VISEME["sp"] == Viseme.X
        assert PHONEME_TO_VISEME[""] == Viseme.X

    def test_vowel_mappings(self):
        """Vowels map to appropriate visemes."""
        # A vowels (open)
        assert PHONEME_TO_VISEME["AA"] == Viseme.A
        assert PHONEME_TO_VISEME["AE"] == Viseme.A

        # E vowels (smile)
        assert PHONEME_TO_VISEME["EH"] == Viseme.E
        assert PHONEME_TO_VISEME["IY"] == Viseme.E

        # O vowels (round)
        assert PHONEME_TO_VISEME["OW"] == Viseme.O
        assert PHONEME_TO_VISEME["UW"] == Viseme.O

    def test_consonant_mappings(self):
        """Consonants map to appropriate visemes."""
        # Lip closure
        assert PHONEME_TO_VISEME["B"] == Viseme.B
        assert PHONEME_TO_VISEME["M"] == Viseme.B
        assert PHONEME_TO_VISEME["P"] == Viseme.B

        # Lip-teeth
        assert PHONEME_TO_VISEME["F"] == Viseme.F
        assert PHONEME_TO_VISEME["V"] == Viseme.F

        # Tongue between teeth
        assert PHONEME_TO_VISEME["TH"] == Viseme.D
        assert PHONEME_TO_VISEME["DH"] == Viseme.D

    def test_rhubarb_mapping_exists(self):
        """Rhubarb mapping exists."""
        assert len(RHUBARB_TO_VISEME) > 0

    def test_rhubarb_mapping_complete(self):
        """All Rhubarb outputs are mapped."""
        rhubarb_outputs = ["X", "A", "B", "C", "D", "E", "F", "G", "H"]
        for output in rhubarb_outputs:
            assert output in RHUBARB_TO_VISEME


class TestVisemeCue:
    """Tests for VisemeCue dataclass."""

    def test_viseme_cue_creation(self):
        """VisemeCue can be created."""
        cue = VisemeCue(start_time=0.5, end_time=1.0, viseme=Viseme.A)
        assert cue.start_time == 0.5
        assert cue.end_time == 1.0
        assert cue.viseme == Viseme.A

    def test_cue_duration_property(self):
        """Duration property calculates correctly."""
        cue = VisemeCue(start_time=0.5, end_time=1.5, viseme=Viseme.A)
        assert cue.duration == 1.0

    def test_cue_zero_duration(self):
        """Zero duration cue."""
        cue = VisemeCue(start_time=1.0, end_time=1.0, viseme=Viseme.X)
        assert cue.duration == 0.0


class TestVisemeController:
    """Tests for VisemeController."""

    def test_controller_initialization(self):
        """Controller initializes with default state."""
        controller = VisemeController()
        assert controller.transition_time == 0.05
        assert controller.idle_viseme == Viseme.X
        assert controller.current_viseme == Viseme.X
        assert controller._transition_progress == 1.0
        assert len(controller.cues) == 0

    def test_controller_custom_initialization(self):
        """Controller can be initialized with custom values."""
        controller = VisemeController(transition_time=0.1, idle_viseme=Viseme.A)
        assert controller.transition_time == 0.1
        assert controller.idle_viseme == Viseme.A
        assert controller.current_viseme == Viseme.A

    def test_load_cues(self):
        """Can load viseme cues."""
        controller = VisemeController()
        cues = [
            VisemeCue(0.0, 0.5, Viseme.A),
            VisemeCue(0.5, 1.0, Viseme.E),
        ]
        controller.load_cues(cues)
        assert len(controller.cues) == 2

    def test_load_cues_sorts_by_time(self):
        """Loading cues sorts them by start time."""
        controller = VisemeController()
        cues = [
            VisemeCue(1.0, 1.5, Viseme.E),
            VisemeCue(0.0, 0.5, Viseme.A),
            VisemeCue(0.5, 1.0, Viseme.O),
        ]
        controller.load_cues(cues)
        assert controller.cues[0].start_time == 0.0
        assert controller.cues[1].start_time == 0.5
        assert controller.cues[2].start_time == 1.0

    def test_get_viseme_at_time(self):
        """Can get viseme at specific time."""
        controller = VisemeController()
        cues = [
            VisemeCue(0.0, 0.5, Viseme.A),
            VisemeCue(0.5, 1.0, Viseme.E),
            VisemeCue(1.0, 1.5, Viseme.O),
        ]
        controller.load_cues(cues)

        assert controller.get_viseme_at_time(0.2) == Viseme.A
        assert controller.get_viseme_at_time(0.7) == Viseme.E
        assert controller.get_viseme_at_time(1.2) == Viseme.O

    def test_get_viseme_before_first_cue(self):
        """Before first cue returns idle viseme."""
        controller = VisemeController(idle_viseme=Viseme.X)
        cues = [VisemeCue(1.0, 2.0, Viseme.A)]
        controller.load_cues(cues)

        assert controller.get_viseme_at_time(0.5) == Viseme.X

    def test_get_viseme_after_last_cue(self):
        """After last cue returns idle viseme."""
        controller = VisemeController(idle_viseme=Viseme.X)
        cues = [VisemeCue(0.0, 1.0, Viseme.A)]
        controller.load_cues(cues)

        assert controller.get_viseme_at_time(2.0) == Viseme.X

    def test_update_with_no_cues(self):
        """Update with no cues maintains idle state."""
        controller = VisemeController()
        shape = controller.update(t=0.5, dt=0.016)

        assert shape == VISEME_SHAPES[Viseme.X]

    def test_update_triggers_transition(self):
        """Update triggers transition when viseme changes."""
        controller = VisemeController(transition_time=0.1)
        cues = [VisemeCue(0.0, 1.0, Viseme.A)]
        controller.load_cues(cues)

        # Before any update, should be at idle
        assert controller.current_viseme == Viseme.X
        assert controller._transition_progress == 1.0

        # First update at t=0.5 should trigger transition to A
        controller.update(t=0.5, dt=0.016)
        assert controller.current_viseme == Viseme.A
        assert controller._transition_progress < 1.0

    def test_update_completes_transition(self):
        """Update completes transition after transition time."""
        controller = VisemeController(transition_time=0.1)
        cues = [VisemeCue(0.0, 1.0, Viseme.A)]
        controller.load_cues(cues)

        # Trigger transition
        controller.update(t=0.5, dt=0.05)
        assert controller._transition_progress < 1.0

        # Complete transition
        controller.update(t=0.5, dt=0.1)
        assert controller._transition_progress == 1.0

    def test_update_interpolates_shape(self):
        """Update interpolates between shapes during transition."""
        controller = VisemeController(transition_time=0.1)
        cues = [VisemeCue(0.0, 1.0, Viseme.A)]
        controller.load_cues(cues)

        # Start at idle (X), transition to A
        idle_openness = VISEME_SHAPES[Viseme.X].mouth_openness
        a_openness = VISEME_SHAPES[Viseme.A].mouth_openness

        # Partway through transition
        controller.update(t=0.5, dt=0.05)
        shape = controller.current_shape

        # Should be between idle and A
        assert idle_openness < shape.mouth_openness < a_openness

    def test_get_mouth_openness(self):
        """Can get mouth openness at specific time."""
        controller = VisemeController()
        cues = [
            VisemeCue(0.0, 1.0, Viseme.A),
            VisemeCue(1.0, 2.0, Viseme.X),
        ]
        controller.load_cues(cues)

        openness_a = controller.get_mouth_openness(0.5)
        openness_x = controller.get_mouth_openness(1.5)

        assert openness_a == VISEME_SHAPES[Viseme.A].mouth_openness
        assert openness_x == VISEME_SHAPES[Viseme.X].mouth_openness

    def test_reset(self):
        """Reset returns to idle state."""
        controller = VisemeController(idle_viseme=Viseme.X)
        cues = [VisemeCue(0.0, 1.0, Viseme.A)]
        controller.load_cues(cues)

        # Advance to A
        controller.update(t=0.5, dt=0.1)
        assert controller.current_viseme == Viseme.A

        # Reset
        controller.reset()
        assert controller.current_viseme == Viseme.X
        assert controller._transition_progress == 1.0
        assert controller.current_shape == VISEME_SHAPES[Viseme.X]

    def test_load_rhubarb_json(self):
        """Can load Rhubarb JSON format."""
        controller = VisemeController()
        data = {
            "mouthCues": [
                {"start": 0.0, "end": 0.5, "value": "X"},
                {"start": 0.5, "end": 1.0, "value": "B"},
                {"start": 1.0, "end": 1.5, "value": "C"},
            ]
        }
        controller.load_rhubarb_json(data)

        assert len(controller.cues) == 3
        assert controller.cues[0].viseme == RHUBARB_TO_VISEME["X"]
        assert controller.cues[1].viseme == RHUBARB_TO_VISEME["B"]
        assert controller.cues[2].viseme == RHUBARB_TO_VISEME["C"]

    def test_load_rhubarb_json_empty(self):
        """Loading empty Rhubarb data works."""
        controller = VisemeController()
        data = {"mouthCues": []}
        controller.load_rhubarb_json(data)
        assert len(controller.cues) == 0

    def test_load_rhubarb_json_unknown_value(self):
        """Unknown Rhubarb values default to X."""
        controller = VisemeController()
        data = {"mouthCues": [{"start": 0.0, "end": 1.0, "value": "UNKNOWN"}]}
        controller.load_rhubarb_json(data)
        assert controller.cues[0].viseme == Viseme.X


class TestSimpleTextToVisemes:
    """Tests for simple_text_to_visemes function."""

    def test_empty_text(self):
        """Empty text returns single X cue."""
        cues = simple_text_to_visemes("", duration=1.0)
        assert len(cues) == 1
        assert cues[0].viseme == Viseme.X
        assert cues[0].duration == 1.0

    def test_single_word(self):
        """Single word generates cues."""
        cues = simple_text_to_visemes("hello", duration=1.0)
        assert len(cues) > 0
        # Should have at least one viseme for each syllable
        assert any(cue.viseme != Viseme.X for cue in cues)

    def test_multiple_words(self):
        """Multiple words generate multiple cues."""
        cues = simple_text_to_visemes("hello world", duration=2.0)
        assert len(cues) > 2

    def test_cues_cover_duration(self):
        """Generated cues cover the full duration."""
        duration = 2.0
        cues = simple_text_to_visemes("test text", duration=duration)

        # Last cue should end at or near duration
        if cues:
            assert cues[-1].end_time <= duration + 0.1

    def test_vowel_detection(self):
        """Vowels are detected for syllable counting."""
        # "a" has 1 syllable
        cues_a = simple_text_to_visemes("a", duration=1.0)
        # "aa" has 2 syllables
        cues_aa = simple_text_to_visemes("aa", duration=1.0)

        # More vowels should generate more cues (generally)
        assert len(cues_aa) >= len(cues_a)

    def test_consonant_only_word(self):
        """Words with no vowels get at least 1 syllable."""
        cues = simple_text_to_visemes("xyz", duration=1.0)
        # Should still generate cues even with no vowels
        assert len(cues) > 0

    def test_cues_in_order(self):
        """Generated cues are in chronological order."""
        cues = simple_text_to_visemes("hello world", duration=2.0)

        for i in range(len(cues) - 1):
            assert cues[i].start_time <= cues[i + 1].start_time

    def test_no_overlapping_cues(self):
        """Generated cues don't overlap."""
        cues = simple_text_to_visemes("test", duration=1.0)

        for i in range(len(cues) - 1):
            assert cues[i].end_time <= cues[i + 1].start_time + 0.001

    def test_custom_wpm(self):
        """Can customize words per minute."""
        # Different WPM shouldn't crash, though timing may differ
        cues_slow = simple_text_to_visemes("hello", duration=2.0, words_per_minute=60)
        cues_fast = simple_text_to_visemes("hello", duration=2.0, words_per_minute=300)

        # Both should generate cues
        assert len(cues_slow) > 0
        assert len(cues_fast) > 0
