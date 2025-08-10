"""
MusicGen Prompt Templates for Traditional Chinese Music
Culturally-specific prompts designed for authentic TCM generation
"""

from typing import Dict, List, Optional
import random
from dataclasses import dataclass
from enum import Enum

class Era(Enum):
    """Historical eras for Chinese music contextualization."""
    TRADITIONAL = "traditional"
    ERA_1930S = "1930s"
    ERA_1940S = "1940s"
    ERA_1950S = "1950s"
    ERA_1960S = "1960s"

class Mood(Enum):
    """Emotional contexts in Chinese musical tradition."""
    NOSTALGIC = "nostalgic"
    PEACEFUL = "peaceful"
    MELANCHOLIC = "melancholic"
    JOYFUL = "joyful"

class Tempo(Enum):
    """Tempo classifications with cultural context."""
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"

@dataclass
class PromptTemplate:
    """Template for generating culturally-specific prompts."""
    base_description: str
    instrument_modifiers: List[str]
    cultural_elements: List[str]
    emotional_descriptors: List[str]
    technical_elements: List[str]
    era_context: Optional[str] = None

class TCMPromptTemplates:
    """Comprehensive prompt templates for Traditional Chinese Music generation."""

    def __init__(self):
        self.instrument_characteristics = {
            'erhu': {
                'timbre': ['warm', 'expressive', 'singing', 'emotional', 'soulful'],
                'techniques': ['sliding notes', 'vibrato', 'glissando', 'bending'],
                'cultural_role': ['storytelling', 'emotional expression', 'folk tradition'],
                'sound_description': 'bowed string instrument with distinctive crying tone'
            },
            'guqin': {
                'timbre': ['refined', 'contemplative', 'ethereal', 'meditative', 'ancient'],
                'techniques': ['harmonics', 'sparse notes', 'subtle ornaments', 'breath-like phrasing'],
                'cultural_role': ['scholarly music', 'spiritual practice', 'court music'],
                'sound_description': 'seven-stringed zither with profound resonance'
            },
            'guzheng': {
                'timbre': ['bright', 'cascading', 'lyrical', 'flowing', 'crystalline'],
                'techniques': ['glissando', 'tremolo', 'rapid arpeggios', 'finger techniques'],
                'cultural_role': ['entertainment', 'court music', 'popular tradition'],
                'sound_description': 'plucked zither with shimmering metallic tones'
            },
            'pipa': {
                'timbre': ['crisp', 'articulate', 'dramatic', 'percussive', 'dynamic'],
                'techniques': ['rapid passages', 'tremolo', 'storytelling passages', 'martial rhythms'],
                'cultural_role': ['narrative music', 'opera accompaniment', 'virtuosic display'],
                'sound_description': 'four-stringed lute with sharp attack and decay'
            },
            'dizi': {
                'timbre': ['breathy', 'natural', 'pastoral', 'flowing', 'expressive'],
                'techniques': ['ornamental passages', 'breath control', 'trill techniques', 'folk melodies'],
                'cultural_role': ['folk music', 'nature evocation', 'rural tradition'],
                'sound_description': 'bamboo flute with membrane creating buzzing timbre'
            },
            'xiao': {
                'timbre': ['deep', 'mysterious', 'introspective', 'haunting', 'meditative'],
                'techniques': ['long tones', 'breath techniques', 'subtle articulation', 'sparse phrasing'],
                'cultural_role': ['contemplative music', 'spiritual practice', 'solitary reflection'],
                'sound_description': 'vertical bamboo flute with profound, woody tone'
            }
        }

        self.era_templates = {
            Era.TRADITIONAL: PromptTemplate(
                base_description="Ancient Chinese music, timeless traditional style",
                instrument_modifiers=["ceremonial", "classical", "court style", "ritual"],
                cultural_elements=["ancestral wisdom", "spiritual depth", "imperial court", "Confucian ideals"],
                emotional_descriptors=["profound", "timeless", "sacred", "contemplative"],
                technical_elements=["pentatonic scale", "traditional ornaments", "ancient techniques", "formal structure"],
                era_context="reflecting millennia of Chinese musical tradition"
            ),
            Era.ERA_1930S: PromptTemplate(
                base_description="Chinese music from the 1930s, Republican era cultural renaissance",
                instrument_modifiers=["refined", "modern classical", "cultural revival", "nostalgic"],
                cultural_elements=["intellectual awakening", "cultural modernization", "East-West fusion", "urban sophistication"],
                emotional_descriptors=["romantic", "hopeful", "culturally proud", "gently modern"],
                technical_elements=["traditional harmony", "subtle Western influence", "emotional expression", "refined technique"],
                era_context="capturing the spirit of China's cultural renaissance and modernization"
            ),
            Era.ERA_1940S: PromptTemplate(
                base_description="Chinese music from the 1940s, wartime emotion and resilience",
                instrument_modifiers=["emotionally intense", "dramatic", "patriotic", "deeply felt"],
                cultural_elements=["national struggle", "emotional depth", "solidarity", "cultural preservation"],
                emotional_descriptors=["dramatic", "melancholic", "resilient", "emotionally powerful"],
                technical_elements=["expressive techniques", "emotional intensity", "traditional roots", "heartfelt phrasing"],
                era_context="reflecting the emotional intensity and cultural preservation during wartime"
            ),
            Era.ERA_1950S: PromptTemplate(
                base_description="Chinese music from the 1950s, post-war reconstruction and hope",
                instrument_modifiers=["optimistic", "rebuilding spirit", "community-focused", "forward-looking"],
                cultural_elements=["reconstruction", "new beginnings", "collective spirit", "cultural revival"],
                emotional_descriptors=["hopeful", "rebuilding", "optimistic", "community-minded"],
                technical_elements=["accessible melodies", "traditional forms", "uplifting harmonies", "clear structure"],
                era_context="embodying the hope and reconstruction spirit of post-war China"
            ),
            Era.ERA_1960S: PromptTemplate(
                base_description="Chinese music from the 1960s, economic development and cultural adaptation",
                instrument_modifiers=["progressive", "bridge-building", "adaptable", "modernizing"],
                cultural_elements=["economic growth", "cultural adaptation", "modern China", "traditional fusion"],
                emotional_descriptors=["progressive", "adaptive", "forward-thinking", "culturally grounded"],
                technical_elements=["evolved traditional style", "modern sensibilities", "accessible forms", "cultural synthesis"],
                era_context="representing cultural adaptation and modernization while maintaining traditional roots"
            )
        }

        self.mood_descriptors = {
            Mood.NOSTALGIC: {
                'primary': ['wistful', 'longing', 'reminiscent', 'bittersweet', 'sentimental'],
                'cultural': ['memories of home', 'ancestral connection', 'distant homeland', 'childhood memories'],
                'musical': ['gentle phrasing', 'emotional expression', 'tender articulation', 'heartfelt delivery'],
                'imagery': ['autumn leaves', 'distant mountains', 'flowing rivers', 'moonlit nights']
            },
            Mood.PEACEFUL: {
                'primary': ['serene', 'tranquil', 'harmonious', 'balanced', 'calm'],
                'cultural': ['inner harmony', 'Taoist balance', 'garden serenity', 'meditation'],
                'musical': ['flowing rhythms', 'gentle dynamics', 'smooth phrasing', 'relaxed tempo'],
                'imagery': ['still water', 'morning mist', 'bamboo grove', 'peaceful garden']
            },
            Mood.MELANCHOLIC: {
                'primary': ['sorrowful', 'melancholy', 'introspective', 'profound sadness', 'contemplative'],
                'cultural': ['autumn sadness', 'separation sorrow', 'life impermanence', 'deep reflection'],
                'musical': ['descending melodies', 'minor inflections', 'expressive ornaments', 'emotional depth'],
                'imagery': ['falling petals', 'empty courtyard', 'solitary figure', 'grey skies']
            },
            Mood.JOYFUL: {
                'primary': ['celebratory', 'festive', 'bright', 'energetic', 'uplifting'],
                'cultural': ['Spring Festival', 'harvest celebration', 'wedding joy', 'community gathering'],
                'musical': ['bright melodies', 'rhythmic vitality', 'ornamental flourishes', 'energetic tempo'],
                'imagery': ['blooming flowers', 'dancing figures', 'bright lanterns', 'festive gathering']
            }
        }

        self.tempo_characteristics = {
            Tempo.SLOW: {
                'descriptors': ['meditative pace', 'contemplative', 'breathing rhythm', 'ceremonial'],
                'cultural_context': ['ritual music', 'contemplation', 'spiritual practice', 'deep reflection'],
                'technical': ['sustained notes', 'careful articulation', 'spacious phrasing', 'resonant']
            },
            Tempo.MODERATE: {
                'descriptors': ['walking pace', 'conversational', 'narrative', 'flowing'],
                'cultural_context': ['storytelling', 'folk tradition', 'daily life', 'natural rhythm'],
                'technical': ['balanced phrasing', 'natural flow', 'comfortable pace', 'expressive']
            },
            Tempo.FAST: {
                'descriptors': ['energetic', 'virtuosic', 'celebratory', 'dynamic'],
                'cultural_context': ['festival music', 'celebration', 'martial arts', 'theatrical'],
                'technical': ['rapid passages', 'technical display', 'rhythmic precision', 'articulate']
            }
        }

    def generate_base_prompt(self,
                           instruments: List[str],
                           era: Era = Era.TRADITIONAL,
                           mood: Mood = Mood.NOSTALGIC,
                           tempo: Tempo = Tempo.MODERATE) -> str:
        """Generate a base prompt for the given parameters."""

        # Get era template
        era_template = self.era_templates[era]

        # Build instrument description
        instrument_desc = self._build_instrument_description(instruments)

        # Get mood descriptors
        mood_info = self.mood_descriptors[mood]

        # Get tempo characteristics
        tempo_info = self.tempo_characteristics[tempo]

        # Construct prompt
        components = [
            era_template.base_description,
            instrument_desc,
            f"with {random.choice(mood_info['primary'])} {mood.value} mood",
            f"at {random.choice(tempo_info['descriptors'])} {tempo.value} tempo",
            f"featuring {random.choice(era_template.technical_elements)}",
            era_template.era_context
        ]

        return ", ".join(components)

    def _build_instrument_description(self, instruments: List[str]) -> str:
        """Build detailed instrument description."""

        if not instruments:
            return "traditional Chinese ensemble"

        descriptions = []
        for instrument in instruments[:2]:  # Limit to 2 main instruments
            if instrument in self.instrument_characteristics:
                char = self.instrument_characteristics[instrument]
                timbre = random.choice(char['timbre'])
                technique = random.choice(char['techniques'])
                descriptions.append(f"{instrument} with {timbre} timbre and {technique}")

        if descriptions:
            return f"featuring {', '.join(descriptions)}"
        else:
            return f"performed on {', '.join(instruments)}"

    def generate_variation_prompts(self,
                                 base_prompt: str,
                                 variation_types: List[str] = None,
                                 num_variations: int = 3) -> List[str]:
        """Generate multiple variation prompts from a base prompt."""

        if variation_types is None:
            variation_types = ['emotional', 'technical', 'cultural', 'temporal']

        variations = []

        for i in range(num_variations):
            variation_type = random.choice(variation_types)

            if variation_type == 'emotional':
                modifier = self._get_emotional_variation()
            elif variation_type == 'technical':
                modifier = self._get_technical_variation()
            elif variation_type == 'cultural':
                modifier = self._get_cultural_variation()
            elif variation_type == 'temporal':
                modifier = self._get_temporal_variation()
            else:
                modifier = "with subtle variation"

            variation = f"{base_prompt}, {modifier}"
            variations.append(variation)

        return variations

    def _get_emotional_variation(self) -> str:
        """Get emotional variation modifier."""
        modifiers = [
            "with deeper emotional expression",
            "emphasizing nostalgic elements",
            "with more introspective character",
            "highlighting emotional peaks",
            "with gentle emotional intensity",
            "expressing profound feeling"
        ]
        return random.choice(modifiers)

    def _get_technical_variation(self) -> str:
        """Get technical variation modifier."""
        modifiers = [
            "with traditional ornamental techniques",
            "featuring authentic Chinese articulation",
            "using classical phrasing methods",
            "with period-appropriate ornamentation",
            "emphasizing traditional techniques",
            "with characteristic Chinese musical gestures"
        ]
        return random.choice(modifiers)

    def _get_cultural_variation(self) -> str:
        """Get cultural variation modifier."""
        modifiers = [
            "deeply rooted in Chinese tradition",
            "reflecting authentic cultural spirit",
            "embodying Chinese aesthetic principles",
            "with traditional cultural resonance",
            "capturing authentic Chinese character",
            "expressing cultural authenticity"
        ]
        return random.choice(modifiers)

    def _get_temporal_variation(self) -> str:
        """Get temporal/rhythmic variation modifier."""
        modifiers = [
            "with subtle rhythmic variation",
            "featuring natural tempo fluctuation",
            "with breathing-like phrasing",
            "using traditional timing",
            "with organic rhythmic flow",
            "emphasizing natural musical timing"
        ]
        return random.choice(modifiers)

    def generate_era_specific_prompt(self,
                                   era: Era,
                                   instruments: List[str] = None,
                                   cultural_specificity: str = "high") -> str:
        """Generate a prompt specifically targeting a historical era."""

        era_template = self.era_templates[era]

        if instruments is None:
            instruments = ['erhu', 'guqin']  # Default traditional combination

        # Build era-specific components
        components = [
            era_template.base_description,
            self._build_instrument_description(instruments),
            f"reflecting {random.choice(era_template.cultural_elements)}",
            f"with {random.choice(era_template.emotional_descriptors)} character"
        ]

        if cultural_specificity == "high":
            components.extend([
                f"featuring {random.choice(era_template.technical_elements)}",
                era_template.era_context,
                "maintaining cultural authenticity"
            ])

        return ", ".join(components)

    def generate_alzheimer_therapeutic_prompt(self,
                                            patient_era: Era,
                                            familiarity_level: str = "high",
                                            emotional_target: Mood = Mood.NOSTALGIC) -> str:
        """Generate therapeutically-oriented prompt for Alzheimer's patients."""

        # Focus on familiar, culturally resonant elements
        therapeutic_elements = [
            "gentle and familiar",
            "emotionally comforting",
            "culturally resonant",
            "memory-evoking"
        ]

        era_template = self.era_templates[patient_era]
        mood_info = self.mood_descriptors[emotional_target]

        # Build therapeutic prompt
        components = [
            f"Therapeutic Chinese music from the {patient_era.value}",
            "designed for memory care and emotional comfort",
            f"featuring {random.choice(therapeutic_elements)} melodies",
            f"with {random.choice(mood_info['primary'])} {emotional_target.value} mood",
            f"evoking {random.choice(mood_info['cultural'])}",
            "at gentle, comfortable pace",
            "culturally authentic and deeply familiar"
        ]

        if familiarity_level == "high":
            components.extend([
                "using well-known melodic patterns",
                "with traditional harmonic progressions",
                "emphasizing cultural recognition"
            ])

        return ", ".join(components)

    def get_prompt_examples(self) -> Dict[str, List[str]]:
        """Get example prompts for different scenarios."""

        examples = {
            "basic_traditional": [
                self.generate_base_prompt(['erhu'], Era.TRADITIONAL, Mood.PEACEFUL, Tempo.SLOW),
                self.generate_base_prompt(['guzheng', 'pipa'], Era.TRADITIONAL, Mood.JOYFUL, Tempo.MODERATE),
                self.generate_base_prompt(['guqin'], Era.TRADITIONAL, Mood.MELANCHOLIC, Tempo.SLOW)
            ],

            "historical_eras": [
                self.generate_era_specific_prompt(Era.ERA_1930S, ['erhu', 'yangqin']),
                self.generate_era_specific_prompt(Era.ERA_1940S, ['guqin']),
                self.generate_era_specific_prompt(Era.ERA_1950S, ['guzheng', 'dizi']),
                self.generate_era_specific_prompt(Era.ERA_1960S, ['pipa', 'erhu'])
            ],

            "therapeutic": [
                self.generate_alzheimer_therapeutic_prompt(Era.ERA_1940S, "high", Mood.NOSTALGIC),
                self.generate_alzheimer_therapeutic_prompt(Era.ERA_1950S, "high", Mood.PEACEFUL),
                self.generate_alzheimer_therapeutic_prompt(Era.ERA_1930S, "medium", Mood.JOYFUL)
            ],

            "variations": []
        }

        # Generate variations from base prompt
        base = examples["basic_traditional"][0]
        examples["variations"] = self.generate_variation_prompts(base, num_variations=4)

        return examples

# Example usage and demonstration
if __name__ == "__main__":

    # Initialize template generator
    templates = TCMPromptTemplates()

    # Generate examples for different scenarios
    print("=== Traditional Chinese Music Prompt Templates ===\n")

    # Basic traditional prompts
    print("1. Basic Traditional Music Prompts:")
    basic_prompts = [
        templates.generate_base_prompt(['erhu'], Era.TRADITIONAL, Mood.NOSTALGIC, Tempo.SLOW),
        templates.generate_base_prompt(['guzheng', 'pipa'], Era.TRADITIONAL, Mood.JOYFUL, Tempo.MODERATE),
        templates.generate_base_prompt(['guqin'], Era.TRADITIONAL, Mood.PEACEFUL, Tempo.SLOW)
    ]

    for i, prompt in enumerate(basic_prompts, 1):
        print(f"   {i}. {prompt}")
    print()

    # Historical era prompts
    print("2. Historical Era Prompts:")
    era_prompts = [
        templates.generate_era_specific_prompt(Era.ERA_1930S, ['erhu', 'yangqin']),
        templates.generate_era_specific_prompt(Era.ERA_1940S, ['guqin']),
        templates.generate_era_specific_prompt(Era.ERA_1950S, ['guzheng', 'dizi'])
    ]

    for i, prompt in enumerate(era_prompts, 1):
        print(f"   {i}. {prompt}")
    print()

    # Therapeutic prompts for Alzheimer's patients
    print("3. Therapeutic Prompts for Alzheimer's Care:")
    therapeutic_prompts = [
        templates.generate_alzheimer_therapeutic_prompt(Era.ERA_1940S, "high", Mood.NOSTALGIC),
        templates.generate_alzheimer_therapeutic_prompt(Era.ERA_1950S, "high", Mood.PEACEFUL),
        templates.generate_alzheimer_therapeutic_prompt(Era.ERA_1930S, "medium", Mood.JOYFUL)
    ]

    for i, prompt in enumerate(therapeutic_prompts, 1):
        print(f"   {i}. {prompt}")
    print()

    # Variations from a base prompt
    print("4. Variations from Base Prompt:")
    base_prompt = basic_prompts[0]
    print(f"   Base: {base_prompt}")

    variations = templates.generate_variation_prompts(base_prompt, num_variations=3)
    for i, variation in enumerate(variations, 1):
        print(f"   Var {i}: {variation}")
    print()

    # All examples
    print("5. Complete Example Set:")
    all_examples = templates.get_prompt_examples()

    for category, prompts in all_examples.items():
        print(f"   {category.replace('_', ' ').title()}:")
        for j, prompt in enumerate(prompts[:2], 1):  # Show first 2 examples
            print(f"      {j}. {prompt}")
        print()