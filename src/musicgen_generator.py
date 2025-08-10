"""
MusicGen Traditional Chinese Music Generator
Generates culturally faithful variations of TCM using melody conditioning and cultural prompts
"""

import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import torchaudio
import librosa
import soundfile as sf
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import json
import mido
from mido import MidiFile
import muspy
from dataclasses import dataclass
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    """Configuration for music generation."""
    model_name: str = "facebook/musicgen-medium"  # Or "facebook/musicgen-large" for better quality
    max_new_tokens: int = 256  # About 20 seconds at 50 Hz
    do_sample: bool = True
    temperature: float = 1.0
    top_k: int = 250
    top_p: float = 0.0
    guidance_scale: float = 3.0
    sample_rate: int = 32000

class TCMPromptGenerator:
    """Generate culturally-specific prompts for Traditional Chinese Music."""

    def __init__(self):
        # Traditional Chinese instruments with their characteristics
        self.instruments = {
            'erhu': {
                'description': 'Chinese two-stringed bowed instrument',
                'characteristics': ['expressive', 'emotional', 'sliding notes', 'vibrato'],
                'timbre': 'warm, singing, melancholic'
            },
            'guqin': {
                'description': 'Ancient Chinese seven-stringed zither',
                'characteristics': ['meditative', 'subtle', 'harmonics', 'sparse'],
                'timbre': 'refined, contemplative, ethereal'
            },
            'guzheng': {
                'description': 'Chinese plucked string instrument',
                'characteristics': ['flowing', 'graceful', 'glissando', 'tremolo'],
                'timbre': 'bright, cascading, lyrical'
            },
            'pipa': {
                'description': 'Chinese four-stringed lute',
                'characteristics': ['percussive', 'dramatic', 'rapid passages', 'storytelling'],
                'timbre': 'crisp, articulate, dynamic'
            },
            'dizi': {
                'description': 'Chinese bamboo flute',
                'characteristics': ['breathy', 'natural', 'ornamental', 'folk-like'],
                'timbre': 'airy, pastoral, expressive'
            },
            'xiao': {
                'description': 'Chinese vertical bamboo flute',
                'characteristics': ['haunting', 'deep', 'contemplative', 'sparse'],
                'timbre': 'deep, mysterious, introspective'
            },
            'yangqin': {
                'description': 'Chinese hammered dulcimer',
                'characteristics': ['percussive', 'melodic', 'rapid', 'decorative'],
                'timbre': 'bright, metallic, rhythmic'
            }
        }

        # Musical scales and modes
        self.scales = {
            'pentatonic': {
                'description': 'Five-note scale fundamental to Chinese music',
                'characteristics': ['modal', 'ancient', 'harmonious', 'spiritual'],
                'notes': 'C D E G A'
            },
            'gong_mode': {
                'description': 'Chinese mode equivalent to major',
                'characteristics': ['bright', 'celebratory', 'royal', 'formal'],
                'mood': 'majestic'
            },
            'shang_mode': {
                'description': 'Chinese mode with minor characteristics',
                'characteristics': ['melancholic', 'introspective', 'autumn', 'reflective'],
                'mood': 'contemplative'
            },
            'jue_mode': {
                'description': 'Chinese mode with unique intervals',
                'characteristics': ['mysterious', 'ancient', 'ritual', 'otherworldly'],
                'mood': 'mystical'
            }
        }

        # Historical periods and their musical characteristics
        self.historical_periods = {
            '1930s': {
                'context': 'Republic of China era, cultural modernization',
                'style': 'blend of traditional and early modern influences',
                'characteristics': ['nostalgic', 'romantic', 'cultural revival', 'gentle modernization']
            },
            '1940s': {
                'context': 'War period, emotional depth',
                'style': 'expressive, often melancholic, strong emotional content',
                'characteristics': ['dramatic', 'emotional', 'patriotic', 'resilient']
            },
            '1950s': {
                'context': 'Post-war reconstruction, hope and rebuilding',
                'style': 'optimistic traditional music, cultural preservation',
                'characteristics': ['hopeful', 'reconstructive', 'community-focused', 'traditional revival']
            },
            '1960s': {
                'context': 'Economic development, modernization',
                'style': 'traditional forms with modern sensibilities',
                'characteristics': ['progressive', 'bridge-building', 'cultural adaptation', 'forward-looking']
            },
            'traditional': {
                'context': 'Ancient Chinese musical traditions',
                'style': 'pure traditional forms, ancient practices',
                'characteristics': ['timeless', 'spiritual', 'ceremonial', 'ancestral']
            }
        }

        # Mood descriptors in Chinese musical context
        self.moods = {
            'nostalgic': ['wistful', 'longing', 'memories of home', 'bittersweet', 'reminiscent'],
            'peaceful': ['serene', 'tranquil', 'meditative', 'harmonious', 'balanced'],
            'melancholic': ['sorrowful', 'autumn leaves', 'rainy day', 'introspective', 'profound'],
            'joyful': ['celebratory', 'spring festival', 'wedding', 'harvest', 'community gathering']
        }

        # Tempo and rhythm patterns
        self.tempo_styles = {
            'slow': ['meditation pace', 'contemplative', 'breathing rhythm', 'ceremonial'],
            'moderate': ['walking pace', 'storytelling', 'conversational', 'flowing'],
            'fast': ['dance-like', 'celebratory', 'virtuosic', 'energetic']
        }

    def generate_base_prompt(self, track_metadata: Dict) -> str:
        """Generate a base prompt from track metadata."""

        # Extract key information
        instruments = track_metadata.get('instruments', [])
        era = track_metadata.get('era', 'traditional')
        mood = track_metadata.get('mood', 'nostalgic')
        tempo = track_metadata.get('tempo', 'moderate')

        # Build prompt components
        components = []

        # Historical context
        if era in self.historical_periods:
            period_info = self.historical_periods[era]
            components.append(f"{period_info['style']}")

        # Primary instruments
        if instruments:
            inst_descriptions = []
            for inst in instruments[:2]:  # Limit to main instruments
                if inst in self.instruments:
                    inst_info = self.instruments[inst]
                    inst_descriptions.append(f"{inst} with {inst_info['timbre']} timbre")
            if inst_descriptions:
                components.append(f"featuring {', '.join(inst_descriptions)}")

        # Musical characteristics
        components.append("pentatonic scale")

        # Mood and tempo
        if mood in self.moods:
            mood_desc = random.choice(self.moods[mood])
            components.append(f"{mood_desc} mood")

        if tempo in self.tempo_styles:
            tempo_desc = random.choice(self.tempo_styles[tempo])
            components.append(f"{tempo_desc} tempo")

        # Combine into coherent prompt
        base_prompt = f"Traditional Chinese music, {', '.join(components)}"

        return base_prompt

    def generate_variation_prompts(self, base_prompt: str, num_variations: int = 3) -> List[str]:
        """Generate multiple variation prompts from a base prompt."""

        variations = []

        # Style variations
        style_modifiers = [
            "with gentle ornamentation",
            "with expressive phrasing",
            "with subtle rhythmic variation",
            "with melodic embellishment",
            "with traditional breathing",
            "with cultural authenticity"
        ]

        # Emotional variations
        emotional_modifiers = [
            "deeply emotional",
            "spiritually moving",
            "culturally resonant",
            "authentically expressive",
            "traditionally grounded",
            "melodically rich"
        ]

        # Technical variations
        technical_modifiers = [
            "with traditional techniques",
            "with cultural ornaments",
            "with authentic phrasing",
            "with period-appropriate style",
            "with regional characteristics",
            "with generational memory"
        ]

        modifier_sets = [style_modifiers, emotional_modifiers, technical_modifiers]

        for i in range(num_variations):
            # Select modifiers from different categories
            modifiers = []
            for mod_set in modifier_sets:
                if random.random() > 0.5:  # 50% chance to include modifier from each set
                    modifiers.append(random.choice(mod_set))

            if modifiers:
                variation = f"{base_prompt}, {', '.join(modifiers)}"
            else:
                variation = base_prompt

            variations.append(variation)

        return variations

    def create_era_specific_prompt(self, era: str, instruments: List[str] = None) -> str:
        """Create a prompt specifically targeting a historical era."""

        if era not in self.historical_periods:
            era = 'traditional'

        period_info = self.historical_periods[era]

        components = [
            f"Chinese music from the {era}",
            period_info['style'],
            f"reflecting {period_info['context']}"
        ]

        # Add era-specific characteristics
        characteristics = period_info['characteristics']
        selected_chars = random.sample(characteristics, min(2, len(characteristics)))
        components.extend(selected_chars)

        # Add instruments if specified
        if instruments:
            inst_list = [inst for inst in instruments if inst in self.instruments]
            if inst_list:
                components.append(f"performed on {', '.join(inst_list[:2])}")

        return ', '.join(components)

class TCMMusicGenerator:
    """Generate Traditional Chinese Music variations using MusicGen."""

    def __init__(self, config: GenerationConfig = None):
        self.config = config or GenerationConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.prompt_generator = TCMPromptGenerator()

        # Load MusicGen model
        logger.info(f"Loading MusicGen model: {self.config.model_name}")
        self.processor = AutoProcessor.from_pretrained(self.config.model_name)
        self.model = MusicgenForConditionalGeneration.from_pretrained(self.config.model_name)
        self.model.to(self.device)

        logger.info(f"Model loaded on {self.device}")

    def extract_melody_from_midi(self, midi_path: str) -> Optional[torch.Tensor]:
        """Extract melody from MIDI file for conditioning."""
        try:
            # Load MIDI file
            midi_file = MidiFile(midi_path)

            # Convert to muspy Score for easier processing
            score = muspy.from_mido(midi_file)

            # Extract main melody (highest pitch track)
            if not score.tracks:
                return None

            # Find track with most melodic content
            main_track = max(score.tracks, key=lambda t: len(t.notes))

            # Convert to audio representation for MusicGen
            # Sample the melody at MusicGen's expected rate
            melody_audio = self._midi_track_to_audio(main_track)

            return melody_audio

        except Exception as e:
            logger.warning(f"Failed to extract melody from {midi_path}: {e}")
            return None

    def _midi_track_to_audio(self, track) -> torch.Tensor:
        """Convert MIDI track to audio tensor for melody conditioning."""
        # This is a simplified version - in practice, you might want to use
        # a proper MIDI-to-audio synthesis library

        # Create a simple sinusoidal representation
        duration = 10.0  # seconds
        sample_rate = self.config.sample_rate
        samples = int(duration * sample_rate)

        audio = torch.zeros(samples)

        if not track.notes:
            return audio.unsqueeze(0)

        # Convert MIDI notes to audio
        for note in track.notes[:50]:  # Limit number of notes
            start_sample = int((note.time / 1000) * sample_rate)
            end_sample = int(((note.time + note.duration) / 1000) * sample_rate)

            if start_sample >= samples:
                break

            end_sample = min(end_sample, samples)

            # Generate sinusoidal tone for the note
            freq = 440 * (2 ** ((note.pitch - 69) / 12))  # A4 = 440 Hz
            t = torch.linspace(0, (end_sample - start_sample) / sample_rate,
                             end_sample - start_sample)
            tone = 0.3 * torch.sin(2 * torch.pi * freq * t)

            # Add to audio with simple envelope
            envelope = torch.exp(-3 * t)  # Simple decay envelope
            audio[start_sample:end_sample] += tone * envelope

        return audio.unsqueeze(0)  # Add batch dimension

    def generate_variations(self,
                          track_metadata: Dict,
                          num_variations: int = 3,
                          use_melody_conditioning: bool = True) -> List[Dict]:
        """
        Generate variations of a traditional Chinese music track.

        Args:
            track_metadata: Metadata of the source track
            num_variations: Number of variations to generate
            use_melody_conditioning: Whether to use melody conditioning

        Returns:
            List of generated variation metadata
        """

        results = []

        # Generate base prompt
        base_prompt = self.prompt_generator.generate_base_prompt(track_metadata)
        logger.info(f"Base prompt: {base_prompt}")

        # Generate variation prompts
        variation_prompts = self.prompt_generator.generate_variation_prompts(
            base_prompt, num_variations
        )

        # Load melody conditioning if available
        melody_conditioning = None
        if use_melody_conditioning and track_metadata.get('midi_path'):
            melody_conditioning = self.extract_melody_from_midi(track_metadata['midi_path'])
            if melody_conditioning is not None:
                logger.info("Using melody conditioning from MIDI")

        # Generate each variation
        for i, prompt in enumerate(variation_prompts):
            try:
                logger.info(f"Generating variation {i+1}/{num_variations}: {prompt}")

                # Prepare inputs
                inputs = self.processor(
                    text=[prompt],
                    padding=True,
                    return_tensors="pt",
                ).to(self.device)

                # Add melody conditioning if available
                if melody_conditioning is not None:
                    # Ensure melody is the right length and format
                    melody_input = melody_conditioning.to(self.device)

                    # Generate with melody conditioning
                    with torch.no_grad():
                        audio_values = self.model.generate(
                            **inputs,
                            audio_values=melody_input,
                            max_new_tokens=self.config.max_new_tokens,
                            do_sample=self.config.do_sample,
                            temperature=self.config.temperature,
                            top_k=self.config.top_k,
                            top_p=self.config.top_p,
                            guidance_scale=self.config.guidance_scale,
                        )
                else:
                    # Generate without melody conditioning
                    with torch.no_grad():
                        audio_values = self.model.generate(
                            **inputs,
                            max_new_tokens=self.config.max_new_tokens,
                            do_sample=self.config.do_sample,
                            temperature=self.config.temperature,
                            top_k=self.config.top_k,
                            top_p=self.config.top_p,
                            guidance_scale=self.config.guidance_scale,
                        )

                # Convert to numpy for saving
                audio_array = audio_values[0, 0].cpu().numpy()

                # Create result metadata
                variation_metadata = {
                    'variation_id': f"{track_metadata['track_id']}_var_{i+1}",
                    'original_track_id': track_metadata['track_id'],
                    'prompt': prompt,
                    'generation_method': 'melody_conditioned' if melody_conditioning is not None else 'prompt_only',
                    'audio_array': audio_array,
                    'sample_rate': self.config.sample_rate,
                    'duration': len(audio_array) / self.config.sample_rate,
                    'cultural_authenticity_target': track_metadata.get('cultural_authenticity_score', 0.0)
                }

                results.append(variation_metadata)

                logger.info(f"Generated variation {i+1} successfully ({variation_metadata['duration']:.2f}s)")

            except Exception as e:
                logger.error(f"Failed to generate variation {i+1}: {e}")
                continue

        return results

    def save_variation(self, variation_metadata: Dict, output_dir: str) -> str:
        """Save generated variation to file."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create filename
        filename = f"{variation_metadata['variation_id']}.wav"
        filepath = output_path / filename

        # Save audio
        sf.write(
            filepath,
            variation_metadata['audio_array'],
            variation_metadata['sample_rate']
        )

        # Save metadata
        metadata_path = filepath.with_suffix('.json')
        metadata_to_save = {k: v for k, v in variation_metadata.items()
                           if k != 'audio_array'}  # Exclude audio data

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_to_save, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved variation to {filepath}")
        return str(filepath)

    def generate_era_specific_music(self, era: str, instruments: List[str] = None) -> Dict:
        """Generate music specifically for a historical era."""

        prompt = self.prompt_generator.create_era_specific_prompt(era, instruments)
        logger.info(f"Generating era-specific music: {prompt}")

        try:
            # Prepare inputs
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt",
            ).to(self.device)

            # Generate
            with torch.no_grad():
                audio_values = self.model.generate(
                    **inputs,
                    max_new_tokens=self.config.max_new_tokens,
                    do_sample=self.config.do_sample,
                    temperature=self.config.temperature,
                    top_k=self.config.top_k,
                    top_p=self.config.top_p,
                    guidance_scale=self.config.guidance_scale,
                )

            # Convert to numpy
            audio_array = audio_values[0, 0].cpu().numpy()

            return {
                'era': era,
                'instruments': instruments or [],
                'prompt': prompt,
                'audio_array': audio_array,
                'sample_rate': self.config.sample_rate,
                'duration': len(audio_array) / self.config.sample_rate
            }

        except Exception as e:
            logger.error(f"Failed to generate era-specific music: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Example track metadata
    example_track = {
        'track_id': 'ctis_001',
        'title': 'Spring River in the Flower Moon Night',
        'instruments': ['guzheng', 'erhu'],
        'era': '1950s',
        'mood': 'nostalgic',
        'tempo': 'slow',
        'midi_path': '/path/to/midi/file.mid',
        'cultural_authenticity_score': 0.85
    }

    # Initialize generator
    config = GenerationConfig(
        model_name="facebook/musicgen-medium",  # Use medium for faster generation
        max_new_tokens=256,  # ~20 seconds
        temperature=1.0
    )

    generator = TCMMusicGenerator(config)

    # Generate variations
    variations = generator.generate_variations(
        example_track,
        num_variations=3,
        use_melody_conditioning=True
    )

    # Save variations
    output_dir = "generated_tcm_variations"
    for variation in variations:
        filepath = generator.save_variation(variation, output_dir)
        print(f"Saved: {filepath}")

    # Generate era-specific music
    era_music = generator.generate_era_specific_music(
        era='1940s',
        instruments=['erhu', 'guqin']
    )

    if era_music:
        print(f"Generated {era_music['era']} music: {era_music['duration']:.2f}s")