"""
Session Log Template and Data Schema
Comprehensive data structure for music therapy session logging
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import numpy as np

@dataclass
class SessionLogEntry:
    """Single track response entry in a music therapy session."""

    # Session identifiers
    session_id: str
    participant_id: str
    session_date: str  # YYYY-MM-DD format
    session_time: str  # HH:MM:SS format
    timestamp: str     # ISO format for precise timing

    # Track information
    track_id: str
    track_title: str
    track_type: str           # 'original' or 'generated'
    condition_type: str       # 'original' or 'generated' (for analysis)
    track_order: int          # Order within session (1, 2, 3...)

    # Musical characteristics
    era: str                  # '1930s', '1940s', '1950s', '1960s', 'traditional'
    instruments: str          # Comma-separated list
    mood: str                 # 'nostalgic', 'peaceful', 'melancholic', 'joyful'
    tempo: str                # 'slow', 'moderate', 'fast'
    duration: float           # Track duration in seconds

    # Response measurements (1-10 scales)
    engagement_score: int     # 1=no engagement, 10=highly engaged
    mood_response_score: int  # 1=very negative, 10=very positive
    agitation_score: int      # 1=very calm, 10=very agitated

    # Qualitative observations
    caregiver_notes: str      # Free-text observations
    session_notes: str        # Session-level notes

    # Session metadata
    session_duration_minutes: float  # Total planned session duration

    # Optional extended measurements
    response_time_seconds: Optional[float] = None      # Time to show response
    physical_response: Optional[str] = None            # Movement, gestures, etc.
    vocal_response: Optional[str] = None               # Humming, singing along, etc.
    facial_expression: Optional[str] = None            # Smile, frown, neutral, etc.
    attention_duration_seconds: Optional[float] = None # How long they paid attention

    # Technical metadata
    audio_file_path: Optional[str] = None
    generation_prompt: Optional[str] = None    # For AI-generated tracks
    cultural_authenticity_score: Optional[float] = None  # 0-1 scale

class SessionDataManager:
    """Manage session data with validation and export capabilities."""

    def __init__(self, data_file: str = "session_data.csv"):
        self.data_file = data_file
        self.column_descriptions = self._get_column_descriptions()
        self.validation_rules = self._get_validation_rules()

        # Initialize file if it doesn't exist
        self._initialize_data_file()

    def _get_column_descriptions(self) -> Dict[str, str]:
        """Get human-readable descriptions for all columns."""
        return {
            'session_id': 'Unique identifier for each session (UUID format)',
            'participant_id': 'Unique identifier for each participant (e.g., P001, P002)',
            'session_date': 'Date of session in YYYY-MM-DD format',
            'session_time': 'Time session started in HH:MM:SS format',
            'timestamp': 'Precise timestamp when track response was recorded (ISO format)',

            'track_id': 'Unique identifier for the music track',
            'track_title': 'Human-readable title of the track',
            'track_type': 'Type of track: "original" or "generated"',
            'condition_type': 'Experimental condition: "original" or "generated"',
            'track_order': 'Order of track within session (1, 2, 3, etc.)',

            'era': 'Historical era: "1930s", "1940s", "1950s", "1960s", or "traditional"',
            'instruments': 'Comma-separated list of instruments (e.g., "erhu, guqin")',
            'mood': 'Musical mood: "nostalgic", "peaceful", "melancholic", or "joyful"',
            'tempo': 'Musical tempo: "slow", "moderate", or "fast"',
            'duration': 'Track duration in seconds',

            'engagement_score': 'Engagement level (1=no response, 10=highly engaged)',
            'mood_response_score': 'Mood response (1=very negative, 10=very positive)',
            'agitation_score': 'Agitation level (1=very calm, 10=very agitated)',

            'caregiver_notes': 'Free-text observations from caregiver',
            'session_notes': 'General notes about the session',
            'session_duration_minutes': 'Total planned duration of session in minutes',

            'response_time_seconds': 'Time in seconds until participant showed response',
            'physical_response': 'Physical responses: movement, gestures, posture changes',
            'vocal_response': 'Vocal responses: humming, singing, vocalizations',
            'facial_expression': 'Facial expressions: smile, frown, surprise, neutral',
            'attention_duration_seconds': 'Duration of sustained attention in seconds',

            'audio_file_path': 'Path to the audio file used',
            'generation_prompt': 'Prompt used for AI generation (if applicable)',
            'cultural_authenticity_score': 'Assessed cultural authenticity (0-1 scale)'
        }

    def _get_validation_rules(self) -> Dict[str, Dict]:
        """Get validation rules for data quality control."""
        return {
            'engagement_score': {'min': 1, 'max': 10, 'type': int},
            'mood_response_score': {'min': 1, 'max': 10, 'type': int},
            'agitation_score': {'min': 1, 'max': 10, 'type': int},
            'track_order': {'min': 1, 'max': 20, 'type': int},
            'duration': {'min': 10, 'max': 600, 'type': float},  # 10 seconds to 10 minutes
            'session_duration_minutes': {'min': 5, 'max': 120, 'type': float},
            'cultural_authenticity_score': {'min': 0, 'max': 1, 'type': float},
            'era': {'allowed_values': ['1930s', '1940s', '1950s', '1960s', 'traditional']},
            'mood': {'allowed_values': ['nostalgic', 'peaceful', 'melancholic', 'joyful']},
            'tempo': {'allowed_values': ['slow', 'moderate', 'fast']},
            'track_type': {'allowed_values': ['original', 'generated']},
            'condition_type': {'allowed_values': ['original', 'generated']}
        }

    def _initialize_data_file(self):
        """Initialize CSV file with proper headers if it doesn't exist."""
        try:
            # Try to read existing file
            pd.read_csv(self.data_file)
        except FileNotFoundError:
            # Create new file with headers
            empty_df = pd.DataFrame(columns=list(self.column_descriptions.keys()))
            empty_df.to_csv(self.data_file, index=False)
            print(f"Initialized new session log file: {self.data_file}")

    def validate_entry(self, entry: SessionLogEntry) -> List[str]:
        """Validate a session log entry and return list of validation errors."""
        errors = []
        entry_dict = asdict(entry)

        for field, rules in self.validation_rules.items():
            value = entry_dict.get(field)

            if value is None:
                continue  # Skip validation for optional fields

            # Type validation
            if 'type' in rules and not isinstance(value, rules['type']):
                try:
                    # Try to convert
                    if rules['type'] == int:
                        value = int(value)
                    elif rules['type'] == float:
                        value = float(value)
                except (ValueError, TypeError):
                    errors.append(f"{field}: Expected {rules['type'].__name__}, got {type(value).__name__}")
                    continue

            # Range validation
            if 'min' in rules and value < rules['min']:
                errors.append(f"{field}: Value {value} below minimum {rules['min']}")
            if 'max' in rules and value > rules['max']:
                errors.append(f"{field}: Value {value} above maximum {rules['max']}")

            # Allowed values validation
            if 'allowed_values' in rules and value not in rules['allowed_values']:
                errors.append(f"{field}: Value '{value}' not in allowed values {rules['allowed_values']}")

        return errors

    def add_entry(self, entry: SessionLogEntry) -> bool:
        """Add a validated entry to the session log."""

        # Validate entry
        errors = self.validate_entry(entry)
        if errors:
            print(f"Validation errors for entry {entry.session_id}:")
            for error in errors:
                print(f"  - {error}")
            return False

        # Convert to dictionary and add to CSV
        entry_dict = asdict(entry)

        try:
            # Read existing data
            df = pd.read_csv(self.data_file)

            # Add new entry
            new_row = pd.DataFrame([entry_dict])
            df = pd.concat([df, new_row], ignore_index=True)

            # Save back to CSV
            df.to_csv(self.data_file, index=False)
            return True

        except Exception as e:
            print(f"Error adding entry: {e}")
            return False

    def get_data(self,
                 participant_id: Optional[str] = None,
                 session_id: Optional[str] = None,
                 date_range: Optional[tuple] = None) -> pd.DataFrame:
        """Retrieve session data with optional filtering."""

        try:
            df = pd.read_csv(self.data_file)

            # Apply filters
            if participant_id:
                df = df[df['participant_id'] == participant_id]

            if session_id:
                df = df[df['session_id'] == session_id]

            if date_range:
                start_date, end_date = date_range
                df['session_date'] = pd.to_datetime(df['session_date'])
                df = df[(df['session_date'] >= start_date) & (df['session_date'] <= end_date)]

            return df

        except FileNotFoundError:
            return pd.DataFrame()

    def export_for_analysis(self, output_file: str = "analysis_data.csv") -> str:
        """Export cleaned data for statistical analysis."""

        df = self.get_data()

        if df.empty:
            print("No data to export")
            return ""

        # Clean and prepare data for analysis
        analysis_df = df.copy()

        # Convert scores to numeric
        score_columns = ['engagement_score', 'mood_response_score', 'agitation_score']
        for col in score_columns:
            analysis_df[col] = pd.to_numeric(analysis_df[col], errors='coerce')

        # Create derived variables
        analysis_df['positive_response'] = (
            analysis_df['engagement_score'] +
            analysis_df['mood_response_score'] +
            (11 - analysis_df['agitation_score'])  # Invert agitation
        ) / 3

        # Add session-level variables
        analysis_df['session_datetime'] = pd.to_datetime(
            analysis_df['session_date'] + ' ' + analysis_df['session_time']
        )

        # Sort by participant, session, and track order
        analysis_df = analysis_df.sort_values(['participant_id', 'session_datetime', 'track_order'])

        # Save analysis-ready data
        analysis_df.to_csv(output_file, index=False)
        print(f"Analysis data exported to: {output_file}")

        return output_file

    def generate_data_dictionary(self, output_file: str = "data_dictionary.json") -> str:
        """Generate a comprehensive data dictionary."""

        data_dictionary = {
            'title': 'Traditional Chinese Music Therapy Session Data Dictionary',
            'description': 'Comprehensive data structure for recording music therapy session responses in Alzheimer\'s disease research',
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'columns': {}
        }

        # Add column information
        for column, description in self.column_descriptions.items():
            column_info = {
                'description': description,
                'data_type': 'string'  # Default
            }

            # Add validation rules if they exist
            if column in self.validation_rules:
                rules = self.validation_rules[column]

                if 'type' in rules:
                    column_info['data_type'] = rules['type'].__name__
                if 'min' in rules:
                    column_info['minimum'] = rules['min']
                if 'max' in rules:
                    column_info['maximum'] = rules['max']
                if 'allowed_values' in rules:
                    column_info['allowed_values'] = rules['allowed_values']

            data_dictionary['columns'][column] = column_info

        # Save data dictionary
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_dictionary, f, indent=2, ensure_ascii=False)

        print(f"Data dictionary saved to: {output_file}")
        return output_file

def create_sample_data(num_participants: int = 3,
                      sessions_per_participant: int = 4,
                      tracks_per_session: int = 6) -> pd.DataFrame:
    """Create sample session data for testing and demonstration."""

    np.random.seed(42)  # For reproducible results

    sample_entries = []

    eras = ['1930s', '1940s', '1950s', '1960s', 'traditional']
    moods = ['nostalgic', 'peaceful', 'melancholic', 'joyful']
    tempos = ['slow', 'moderate', 'fast']
    instruments_list = [
        ['erhu'], ['guqin'], ['guzheng'], ['pipa'], ['dizi'],
        ['erhu', 'guqin'], ['guzheng', 'pipa'], ['dizi', 'xiao']
    ]

    for p in range(num_participants):
        participant_id = f"P{p+1:03d}"

        # Create participant-specific preferences
        preferred_era = np.random.choice(eras)
        preferred_mood = np.random.choice(moods)
        baseline_engagement = np.random.normal(6, 1)
        ai_preference = np.random.choice([-0.5, 0.5])  # Some prefer AI, some don't

        for s in range(sessions_per_participant):
            session_id = f"{participant_id}_S{s+1:02d}"
            session_date = (datetime.now() - timedelta(days=30-s*7)).strftime('%Y-%m-%d')
            session_time = f"{9+s}:00:00"

            for t in range(tracks_per_session):
                # Randomize track characteristics
                era = np.random.choice(eras, p=[0.3 if e == preferred_era else 0.175 for e in eras])
                mood = np.random.choice(moods, p=[0.4 if m == preferred_mood else 0.2 for m in moods])
                tempo = np.random.choice(tempos)
                instruments = np.random.choice(instruments_list)

                # Determine condition (alternating with some randomization)
                condition_type = 'original' if t % 2 == 0 else 'generated'

                # Generate realistic scores with individual differences
                base_score = baseline_engagement + np.random.normal(0, 1)

                # Add condition effect
                if condition_type == 'generated':
                    base_score += ai_preference

                # Add era/mood preference bonus
                if era == preferred_era:
                    base_score += 0.5
                if mood == preferred_mood:
                    base_score += 0.5

                # Generate correlated scores
                engagement = np.clip(base_score + np.random.normal(0, 0.5), 1, 10)
                mood_response = np.clip(engagement + np.random.normal(0, 1), 1, 10)
                agitation = np.clip(8 - engagement + np.random.normal(0, 1), 1, 10)

                # Create sample notes
                notes_options = [
                    "Smiled and nodded along",
                    "Closed eyes and appeared relaxed",
                    "Tapped fingers to the rhythm",
                    "Seemed to recognize the melody",
                    "Became more alert during this track",
                    "No obvious response",
                    "Appeared restless",
                    "Hummed along quietly"
                ]

                entry = SessionLogEntry(
                    session_id=session_id,
                    participant_id=participant_id,
                    session_date=session_date,
                    session_time=session_time,
                    timestamp=datetime.now().isoformat(),

                    track_id=f"{condition_type}_{p+1:03d}_{s+1:02d}_{t+1:02d}",
                    track_title=f"Traditional Chinese Music {t+1}",
                    track_type=condition_type,
                    condition_type=condition_type,
                    track_order=t+1,

                    era=era,
                    instruments=', '.join(instruments),
                    mood=mood,
                    tempo=tempo,
                    duration=float(np.random.randint(120, 300)),

                    engagement_score=int(round(engagement)),
                    mood_response_score=int(round(mood_response)),
                    agitation_score=int(round(agitation)),

                    caregiver_notes=np.random.choice(notes_options),
                    session_notes=f"Session {s+1} with {participant_id}",
                    session_duration_minutes=float(tracks_per_session * 4),  # 4 minutes per track

                    response_time_seconds=float(np.random.randint(5, 30)),
                    physical_response="gentle movement" if engagement > 7 else "minimal movement",
                    vocal_response="humming" if mood_response > 8 else "none",
                    facial_expression="smile" if mood_response > 7 else "neutral",
                    attention_duration_seconds=float(np.random.randint(60, 180)),

                    cultural_authenticity_score=0.9 if condition_type == 'original' else 0.75
                )

                sample_entries.append(asdict(entry))

    return pd.DataFrame(sample_entries)

# Example usage and testing
if __name__ == "__main__":

    # Initialize session data manager
    print("=== Session Data Management System ===\n")

    manager = SessionDataManager("example_session_data.csv")

    # Generate data dictionary
    dict_file = manager.generate_data_dictionary("example_data_dictionary.json")
    print(f"Data dictionary created: {dict_file}\n")

    # Create sample data
    print("Creating sample session data...")
    sample_df = create_sample_data(num_participants=3, sessions_per_participant=2, tracks_per_session=4)

    # Save sample data
    sample_df.to_csv("sample_session_data.csv", index=False)
    print(f"Sample data created: sample_session_data.csv ({len(sample_df)} entries)\n")

    # Show data summary
    print("Sample Data Summary:")
    print(f"Participants: {sample_df['participant_id'].nunique()}")
    print(f"Sessions: {sample_df['session_id'].nunique()}")
    print(f"Total track responses: {len(sample_df)}")
    print(f"Conditions: {sample_df['condition_type'].value_counts().to_dict()}")
    print(f"Average engagement: {sample_df['engagement_score'].mean():.2f}")
    print(f"Average mood response: {sample_df['mood_response_score'].mean():.2f}")
    print(f"Average agitation: {sample_df['agitation_score'].mean():.2f}")

    # Show column descriptions
    print("\nColumn Descriptions (first 10):")
    for i, (col, desc) in enumerate(manager.column_descriptions.items()):
        if i < 10:
            print(f"  {col}: {desc}")
        else:
            print(f"  ... and {len(manager.column_descriptions) - 10} more columns")
            break

    print(f"\nComplete data dictionary saved to: {dict_file}")
    print("Sample data files created for testing and development.")