import os
from openai import AsyncOpenAI
from typing import List, Optional
import json
from dotenv import load_dotenv

load_dotenv()

class GPTClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Era-specific knowledge base
        self.era_topics = {
            "1940s": ["World War II", "Big Band music", "Radio shows", "Victory gardens", "Rationing"],
            "1950s": ["Rock and Roll", "Drive-in theaters", "TV shows", "Soda fountains", "Poodle skirts"],
            "1960s": ["Beatles", "Moon landing", "Woodstock", "Civil rights", "Muscle cars"],
            "1970s": ["Disco", "Bell bottoms", "Watergate", "Oil crisis", "Star Wars"]
        }

        self.memory_triggers = {
            "family": ["wedding day", "children's births", "family vacations", "holiday traditions", "Sunday dinners"],
            "work": ["first job", "colleagues", "retirement party", "daily commute", "lunch breaks"],
            "hobbies": ["dancing", "gardening", "cooking", "card games", "church activities"],
            "events": ["first car", "graduation", "moving houses", "anniversaries", "community events"]
        }

    async def get_memory_prompts(self, emotional_state: str, current_song: Optional[str] = None,
                                 memory_response: str = "None") -> dict:
        """
        Generate conversation starters and memory prompts for caregivers
        Adapted for Alzheimer's patients instead of ASD behavioral suggestions
        """
        try:
            # Build context based on patient's current state
            context = self._build_context(emotional_state, current_song, memory_response)

            # Create the prompt for GPT
            system_prompt = """You are a memory care specialist helping caregivers engage with Alzheimer's patients through music therapy.
            Provide gentle, appropriate conversation starters and memory prompts based on the patient's current state and the music playing.
            Focus on positive memories from the 1940s-1970s era. Keep suggestions simple and non-threatening.
            Always be respectful of the patient's dignity and current cognitive abilities."""

            user_prompt = f"""
            Current situation:
            - Emotional state: {emotional_state}
            - Memory response level: {memory_response}
            - Current song/era: {current_song if current_song else "General oldies music"}

            Please provide:
            1. Three simple conversation starters related to the music era
            2. Two memory prompts that might trigger positive recollections
            3. One activity suggestion that combines music and memory

            Format as JSON with keys: conversation_starters, memory_prompts, activity_suggestion
            """

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # Parse the response
            content = response.choices[0].message.content

            # Try to parse as JSON, fallback to structured text if needed
            try:
                suggestions = json.loads(content)
            except:
                suggestions = self._parse_text_response(content)

            # Add era-specific trivia
            suggestions["era_trivia"] = self._get_era_trivia(current_song)

            # Add emotional state guidance
            suggestions["caregiver_tips"] = self._get_caregiver_tips(emotional_state, memory_response)

            return suggestions

        except Exception as e:
            print(f"Error getting GPT suggestions: {e}")
            return self._get_fallback_suggestions(emotional_state)

    def _build_context(self, emotional_state: str, current_song: str, memory_response: str) -> str:
        """Build context for GPT based on current situation"""
        context_parts = []

        # Emotional state guidance
        if emotional_state == "Distressed":
            context_parts.append("Patient is showing signs of distress. Focus on calming, familiar topics.")
        elif emotional_state == "Neutral":
            context_parts.append("Patient is calm and receptive. Good opportunity for engagement.")
        elif emotional_state == "Content":
            context_parts.append("Patient is in a positive state. Encourage continued interaction.")
        elif emotional_state == "Joyful":
            context_parts.append("Patient is very happy. Build on this positive momentum.")

        # Memory response guidance
        if memory_response == "Good":
            context_parts.append("Patient is showing good memory recall. Explore related memories.")
        elif memory_response == "Some":
            context_parts.append("Patient has partial recall. Provide gentle hints and support.")
        else:
            context_parts.append("No memory response yet. Try different approaches.")

        return " ".join(context_parts)

    def _get_era_trivia(self, current_song: Optional[str]) -> List[str]:
        """Get era-specific trivia to spark conversation"""
        # Determine era from song or default to 1950s
        era = "1950s"  # Default
        if current_song:
            for decade in ["1940s", "1950s", "1960s", "1970s"]:
                if decade in current_song.lower():
                    era = decade
                    break

        topics = self.era_topics.get(era, self.era_topics["1950s"])
        return [f"Did you know: In the {era}, {topic} was very popular" for topic in topics[:2]]

    def _get_caregiver_tips(self, emotional_state: str, memory_response: str) -> List[str]:
        """Provide specific tips for caregivers based on current state"""
        tips = []

        # Emotional state tips
        if emotional_state == "Distressed":
            tips.append("Speak slowly and calmly. Consider switching to more familiar music.")
            tips.append("Physical comfort may help - offer a hand to hold.")
        elif emotional_state == "Neutral":
            tips.append("Good time to introduce new songs from their era.")
            tips.append("Watch for signs of recognition - slight smile, foot tapping.")
        elif emotional_state == "Content" or emotional_state == "Joyful":
            tips.append("Encourage singing along or gentle movement to the music.")
            tips.append("This is a good time to look at old photos together.")

        # Memory response tips
        if memory_response == "None":
            tips.append("Try asking about feelings rather than facts: 'How does this music make you feel?'")
        elif memory_response == "Some":
            tips.append("Build on partial memories with gentle prompts: 'That sounds nice, tell me more.'")
        elif memory_response == "Good":
            tips.append("Record or write down these memories for future sessions.")

        return tips[:3]  # Return top 3 tips

    def _parse_text_response(self, text: str) -> dict:
        """Parse text response if JSON parsing fails"""
        # Basic parsing logic
        suggestions = {
            "conversation_starters": [
                "This song is from your generation. Do you remember dancing to music like this?",
                "The rhythm reminds me of the old days. What kind of music did you enjoy?",
                "Such a beautiful melody. Did you have a favorite radio show?"
            ],
            "memory_prompts": [
                "Tell me about a special celebration you remember.",
                "What was Sunday like when you were younger?"
            ],
            "activity_suggestion": "Try gentle swaying or tapping along to the rhythm together."
        }
        return suggestions

    def _get_fallback_suggestions(self, emotional_state: str) -> dict:
        """Provide fallback suggestions if GPT fails"""
        base_suggestions = {
            "Distressed": {
                "conversation_starters": [
                    "This is peaceful music. Let's just listen together.",
                    "You're safe here with me.",
                    "Would you like to hear a different song?"
                ],
                "memory_prompts": [
                    "Think of a place where you felt happy and calm.",
                    "Remember your favorite comfort food?"
                ],
                "activity_suggestion": "Hold hands and breathe slowly together with the music."
            },
            "Neutral": {
                "conversation_starters": [
                    "This music is from the good old days.",
                    "Do you recognize this style of music?",
                    "Music was different back then, wasn't it?"
                ],
                "memory_prompts": [
                    "Tell me about your favorite singer from the old days.",
                    "Did you ever go to dances?"
                ],
                "activity_suggestion": "Look through a photo album while the music plays."
            },
            "Content": {
                "conversation_starters": [
                    "You seem to enjoy this music.",
                    "This brings back memories, doesn't it?",
                    "Shall we sing along together?"
                ],
                "memory_prompts": [
                    "Tell me about a happy celebration you remember.",
                    "What was your wedding song?"
                ],
                "activity_suggestion": "Sing or hum along with familiar songs."
            },
            "Joyful": {
                "conversation_starters": [
                    "You have a beautiful smile when you hear this music!",
                    "This must bring back happy memories!",
                    "Shall we dance a little?"
                ],
                "memory_prompts": [
                    "Tell me about the happiest day you remember.",
                    "What celebrations did you enjoy most?"
                ],
                "activity_suggestion": "Do simple dance movements or clap along to the beat."
            }
        }

        suggestions = base_suggestions.get(emotional_state, base_suggestions["Neutral"])
        suggestions["era_trivia"] = [
            "Music from the 1950s often played on the radio all day long.",
            "Big band music was popular for dancing at community halls."
        ]
        suggestions["caregiver_tips"] = [
            "Maintain eye contact and smile warmly.",
            "Be patient - allow time for responses.",
            "Validate all responses, even if confused."
        ]

        return suggestions