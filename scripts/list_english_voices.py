#!/usr/bin/env python3
"""List all available English TTS voices."""

import asyncio
import sys
sys.path.insert(0, ".")

try:
    import edge_tts
except ImportError:
    print("edge-tts not installed. Run: ./dev.sh install")
    sys.exit(1)


async def main():
    """List all English voices from edge-tts."""
    print("\n🎤 ENGLISH TTS VOICES\n")
    print("=" * 80)

    voices = await edge_tts.list_voices()

    # Group by locale
    locales = {
        'en-US': 'English (United States)',
        'en-GB': 'English (United Kingdom)',
        'en-AU': 'English (Australia)',
        'en-CA': 'English (Canada)',
        'en-IN': 'English (India)',
        'en-IE': 'English (Ireland)',
        'en-NZ': 'English (New Zealand)',
        'en-ZA': 'English (South Africa)',
        'en-SG': 'English (Singapore)',
        'en-HK': 'English (Hong Kong)',
        'en-PH': 'English (Philippines)',
    }

    for locale, description in locales.items():
        # Filter voices for this locale
        locale_voices = [v for v in voices if v['Locale'] == locale]

        if not locale_voices:
            continue

        print(f"\n{description} ({locale})")
        print("-" * 80)

        for voice in sorted(locale_voices, key=lambda x: (x['Gender'], x['ShortName'])):
            gender = voice['Gender']
            short_name = voice['ShortName']
            friendly_name = voice.get('FriendlyName', short_name)

            # Extract just the voice name (last part)
            voice_name = short_name.split('-')[-1]

            gender_icon = "♂" if gender == "Male" else "♀"

            print(f"  {gender_icon} {short_name:35} - {friendly_name}")

    print("\n" + "=" * 80)
    print("\n💡 USAGE EXAMPLES:\n")
    print("  # Use default voice (Aria - US Female)")
    print("  ./dev.sh run --speak \"Hello world\"")
    print()
    print("  # Use specific voice")
    print("  ./dev.sh run --speak \"Hello\" --voice en-GB-RyanNeural")
    print()
    print("  # Try different voices")
    print("  ./dev.sh run --speak \"G'day mate\" --voice en-AU-NatashaNeural")
    print("  ./dev.sh run --speak \"Hello there\" --voice en-GB-SoniaNeural")
    print()

    # Show recommended voices
    print("=" * 80)
    print("\n⭐ RECOMMENDED ENGLISH VOICES:\n")

    recommended = [
        ("en-US-AriaNeural", "US Female", "Natural, clear (default)"),
        ("en-US-GuyNeural", "US Male", "Professional, news anchor"),
        ("en-US-JennyNeural", "US Female", "Warm, friendly"),
        ("en-GB-RyanNeural", "UK Male", "British, clear"),
        ("en-GB-SoniaNeural", "UK Female", "British, professional"),
        ("en-AU-NatashaNeural", "AU Female", "Australian accent"),
        ("en-IN-NeerjaNeural", "IN Female", "Indian accent"),
    ]

    for voice, desc, notes in recommended:
        print(f"  • {voice:30} - {desc:15} - {notes}")

    print("\n" + "=" * 80)
    print(f"\n✓ Found {len([v for v in voices if v['Locale'].startswith('en-')])} English voices total\n")


if __name__ == "__main__":
    asyncio.run(main())
