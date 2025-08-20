import numpy as np
from scipy.io import wavfile
import os
from pathlib import Path
from datetime import datetime
import asyncio

class AudioGenerator:
    def __init__(self):
        self.sample_rate = 44100
        self.base_dir = Path(__file__).resolve().parent
        self.generated_dir = self.base_dir / "assets" / "music" / "generated"
        self.generated_dir.mkdir(parents=True, exist_ok=True)

    async def generate_simplified_version(self, base_song: str, tempo: str = "slow", style: str = "simplified"):
        """
        Generate a simplified, slower version of classic songs for Alzheimer's patients
        Creates gentle, recognizable melodies that are easier to process
        """
        try:
            # Define tempo multipliers
            tempo_map = {
                "slow": 0.6,      # 60% speed for easier processing
                "medium": 0.8     # 80% speed
            }
            tempo_mult = tempo_map.get(tempo, 0.6)

            # Generate based on common old song patterns
            if "waltz" in base_song.lower():
                audio_data = self._generate_waltz_pattern(tempo_mult)
            elif "swing" in base_song.lower():
                audio_data = self._generate_swing_pattern(tempo_mult)
            else:
                audio_data = self._generate_simple_melody(tempo_mult)

            # Save the generated audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simplified_{base_song.replace(' ', '_').lower()}_{timestamp}.wav"
            filepath = self.generated_dir / filename

            # Normalize audio
            audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767 * 0.5)

            # Save to file
            wavfile.write(filepath, self.sample_rate, audio_data)

            return filename

        except Exception as e:
            print(f"Error generating audio: {e}")
            # Return a default file if generation fails
            return await self._create_default_audio()

    def _generate_simple_melody(self, tempo_mult: float):
        """Generate a simple, recognizable melody pattern"""
        duration = 30  # 30 seconds
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Classic pentatonic scale frequencies (C, D, E, G, A)
        notes = [261.63, 293.66, 329.63, 392.00, 440.00]  # Hz

        # Create a simple, repetitive melody
        melody = np.zeros_like(t)
        note_duration = 0.5 / tempo_mult  # Slower notes
        samples_per_note = int(note_duration * self.sample_rate)

        # Simple ascending and descending pattern
        pattern = [0, 1, 2, 3, 4, 3, 2, 1]  # Index into notes

        for i, note_idx in enumerate(pattern * (len(t) // (samples_per_note * len(pattern)))):
            start = i * samples_per_note
            end = min(start + samples_per_note, len(t))
            if start < len(t):
                # Add gentle envelope for smooth transitions
                envelope = np.hanning(end - start)
                melody[start:end] += envelope * np.sin(2 * np.pi * notes[note_idx] * t[start:end])

        # Add soft harmony
        harmony = 0.3 * np.sin(2 * np.pi * 130.81 * t)  # Low C

        return melody + harmony

    def _generate_waltz_pattern(self, tempo_mult: float):
        """Generate a 3/4 waltz pattern common in old songs"""
        duration = 30
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Waltz rhythm: strong-weak-weak
        beat_duration = 1.0 / tempo_mult
        samples_per_beat = int(beat_duration * self.sample_rate)

        # Basic waltz bass pattern
        bass_freqs = [130.81, 164.81, 196.00]  # C, E, G
        audio = np.zeros_like(t)

        for i in range(0, len(t), samples_per_beat * 3):
            for j, freq in enumerate(bass_freqs):
                start = i + j * samples_per_beat
                end = min(start + samples_per_beat, len(t))
                if start < len(t):
                    strength = 1.0 if j == 0 else 0.5  # Strong first beat
                    audio[start:end] += strength * np.sin(2 * np.pi * freq * t[start:end])

        # Add simple melody on top
        melody_notes = [329.63, 392.00, 440.00, 392.00]  # E, G, A, G
        melody = np.zeros_like(t)

        for i, note in enumerate(melody_notes * (len(t) // (samples_per_beat * len(melody_notes)))):
            start = i * samples_per_beat
            end = min(start + samples_per_beat, len(t))
            if start < len(t):
                melody[start:end] += 0.6 * np.sin(2 * np.pi * note * t[start:end])

        return audio + melody

    def _generate_swing_pattern(self, tempo_mult: float):
        """Generate a gentle swing pattern from the big band era"""
        duration = 30
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Swing rhythm (simplified)
        beat_duration = 0.75 / tempo_mult
        samples_per_beat = int(beat_duration * self.sample_rate)

        # Walking bass line
        bass_notes = [130.81, 146.83, 164.81, 174.61]  # C, D, E, F
        audio = np.zeros_like(t)

        for i, note in enumerate(bass_notes * (len(t) // (samples_per_beat * len(bass_notes)))):
            start = i * samples_per_beat
            end = min(start + int(samples_per_beat * 0.8), len(t))
            if start < len(t):
                audio[start:end] += np.sin(2 * np.pi * note * t[start:end])

        # Add gentle brush-like percussion
        noise = np.random.normal(0, 0.05, len(t))
        for i in range(0, len(t), samples_per_beat):
            end = min(i + int(samples_per_beat * 0.1), len(t))
            audio[i:end] += noise[i:end]

        # Simple horn-like melody
        melody_notes = [261.63, 329.63, 392.00, 329.63]  # C, E, G, E
        for i, note in enumerate(melody_notes * (len(t) // (samples_per_beat * 2 * len(melody_notes)))):
            start = i * samples_per_beat * 2
            end = min(start + samples_per_beat * 2, len(t))
            if start < len(t):
                envelope = np.exp(-np.linspace(0, 2, end - start))
                audio[start:end] += 0.5 * envelope * np.sin(2 * np.pi * note * t[start:end])

        return audio

    async def _create_default_audio(self):
        """Create a default gentle audio if generation fails"""
        duration = 30
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Simple, calming sine wave
        frequency = 261.63  # Middle C
        audio = np.sin(2 * np.pi * frequency * t) * 0.3

        # Add gentle fade in and out
        fade_samples = int(self.sample_rate * 2)
        audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
        audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        filename = f"default_calm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        filepath = self.generated_dir / filename

        audio_data = np.int16(audio * 32767 * 0.5)
        wavfile.write(filepath, self.sample_rate, audio_data)

        return filename