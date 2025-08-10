"""
Traditional Chinese Music Recommendation Engine
Simplified implementation for the music therapy study
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CCMusicDatasetLoader:
    """Load and process the CCMusic dataset for Traditional Chinese Music."""

    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.metadata_file = self.dataset_path / "metadata.json"

    def load_dataset(self) -> pd.DataFrame:
        """Load the CCMusic dataset and return as DataFrame."""

        if not self.dataset_path.exists():
            logger.error(f"Dataset path not found: {self.dataset_path}")
            # Return sample data for development
            return self._create_sample_dataset()

        # Try to load metadata
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                # Convert to DataFrame
                df = pd.DataFrame(metadata)

            else:
                # If no metadata file, scan directory structure
                df = self._scan_dataset_directory()

        except Exception as e:
            logger.warning(f"Failed to load dataset: {e}. Using sample data.")
            df = self._create_sample_dataset()

        # Process and enhance the dataset
        df = self._process_dataset(df)

        logger.info(f"Loaded {len(df)} tracks from CCMusic dataset")
        return df

    def _create_sample_dataset(self) -> pd.DataFrame:
        """Create sample dataset for development/testing."""

        sample_tracks = [
            {
                'track_id': 'ccm_001',
                'title': 'Spring River in the Flower Moon Night',
                'artist': 'Traditional',
                'era': '1950s',
                'instruments': ['guzheng', 'erhu'],
                'mood': 'nostalgic',
                'tempo': 'slow',
                'duration': 180,
                'file_path': 'audio/spring_river.wav',
                'cultural_authenticity_score': 0.92,
                'region': 'Jiangnan',
                'musical_style': 'classical'
            },
            {
                'track_id': 'ccm_002',
                'title': 'High Mountains Flowing Water',
                'artist': 'Traditional',
                'era': 'traditional',
                'instruments': ['guqin'],
                'mood': 'peaceful',
                'tempo': 'slow',
                'duration': 240,
                'file_path': 'audio/high_mountains.wav',
                'cultural_authenticity_score': 0.95,
                'region': 'Classical',
                'musical_style': 'scholarly'
            },
            {
                'track_id': 'ccm_003',
                'title': 'Moonlight on the Second Spring',
                'artist': 'Hua Yanjun (Abing)',
                'era': '1940s',
                'instruments': ['erhu'],
                'mood': 'melancholic',
                'tempo': 'slow',
                'duration': 210,
                'file_path': 'audio/second_spring.wav',
                'cultural_authenticity_score': 0.98,
                'region': 'Jiangnan',
                'musical_style': 'folk'
            },
            {
                'track_id': 'ccm_004',
                'title': 'Fisherman\'s Song at Dusk',
                'artist': 'Traditional',
                'era': '1960s',
                'instruments': ['guzheng', 'pipa'],
                'mood': 'peaceful',
                'tempo': 'moderate',
                'duration': 195,
                'file_path': 'audio/fisherman_song.wav',
                'cultural_authenticity_score': 0.89,
                'region': 'Shandong',
                'musical_style': 'regional'
            },
            {
                'track_id': 'ccm_005',
                'title': 'Plum Blossom Three Variations',
                'artist': 'Traditional',
                'era': 'traditional',
                'instruments': ['guqin'],
                'mood': 'contemplative',
                'tempo': 'slow',
                'duration': 280,
                'file_path': 'audio/plum_blossom.wav',
                'cultural_authenticity_score': 0.94,
                'region': 'Classical',
                'musical_style': 'scholarly'
            },
            {
                'track_id': 'ccm_006',
                'title': 'Autumn Moon on Calm Lake',
                'artist': 'Traditional',
                'era': '1930s',
                'instruments': ['guzheng', 'xiao'],
                'mood': 'nostalgic',
                'tempo': 'slow',
                'duration': 160,
                'file_path': 'audio/autumn_moon.wav',
                'cultural_authenticity_score': 0.88,
                'region': 'Guangdong',
                'musical_style': 'regional'
            },
            {
                'track_id': 'ccm_007',
                'title': 'Ambush from Ten Sides',
                'artist': 'Traditional',
                'era': 'traditional',
                'instruments': ['pipa'],
                'mood': 'dramatic',
                'tempo': 'fast',
                'duration': 220,
                'file_path': 'audio/ambush.wav',
                'cultural_authenticity_score': 0.96,
                'region': 'Classical',
                'musical_style': 'martial'
            },
            {
                'track_id': 'ccm_008',
                'title': 'Purple Bamboo Melody',
                'artist': 'Traditional',
                'era': '1950s',
                'instruments': ['dizi', 'yangqin'],
                'mood': 'joyful',
                'tempo': 'moderate',
                'duration': 145,
                'file_path': 'audio/purple_bamboo.wav',
                'cultural_authenticity_score': 0.85,
                'region': 'Jiangnan',
                'musical_style': 'folk'
            }
        ]

        return pd.DataFrame(sample_tracks)

    def _scan_dataset_directory(self) -> pd.DataFrame:
        """Scan dataset directory and create metadata from file structure."""

        tracks = []
        audio_dir = self.dataset_path / "audio"

        if audio_dir.exists():
            for audio_file in audio_dir.glob("*.wav"):
                track_id = audio_file.stem

                # Basic metadata from filename
                tracks.append({
                    'track_id': track_id,
                    'title': track_id.replace('_', ' ').title(),
                    'file_path': str(audio_file.relative_to(self.dataset_path)),
                    'era': 'unknown',
                    'instruments': ['unknown'],
                    'mood': 'unknown',
                    'tempo': 'moderate',
                    'duration': 180,  # Default duration
                    'cultural_authenticity_score': 0.5  # Default score
                })

        return pd.DataFrame(tracks)

    def _process_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean the dataset."""

        # Ensure required columns exist
        required_columns = [
            'track_id', 'title', 'era', 'instruments', 'mood', 'tempo',
            'duration', 'cultural_authenticity_score'
        ]

        for col in required_columns:
            if col not in df.columns:
                if col == 'instruments':
                    df[col] = [['unknown']] * len(df)
                elif col == 'cultural_authenticity_score':
                    df[col] = 0.5
                elif col == 'duration':
                    df[col] = 180
                else:
                    df[col] = 'unknown'

        # Convert instruments to list if string
        df['instruments'] = df['instruments'].apply(
            lambda x: x if isinstance(x, list) else [x] if isinstance(x, str) else ['unknown']
        )

        # Ensure numeric columns
        df['duration'] = pd.to_numeric(df['duration'], errors='coerce').fillna(180)
        df['cultural_authenticity_score'] = pd.to_numeric(
            df['cultural_authenticity_score'], errors='coerce'
        ).fillna(0.5)

        # Clean era values
        valid_eras = ['1930s', '1940s', '1950s', '1960s', 'traditional']
        df['era'] = df['era'].apply(
            lambda x: x if x in valid_eras else 'traditional'
        )

        # Clean mood values
        valid_moods = ['nostalgic', 'peaceful', 'melancholic', 'joyful', 'contemplative', 'dramatic']
        df['mood'] = df['mood'].apply(
            lambda x: x if x in valid_moods else 'peaceful'
        )

        # Clean tempo values
        valid_tempos = ['slow', 'moderate', 'fast']
        df['tempo'] = df['tempo'].apply(
            lambda x: x if x in valid_tempos else 'moderate'
        )

        return df

class TCMRecommendationEngine:
    """Traditional Chinese Music recommendation engine for therapy sessions."""

    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset
        self.instrument_weights = self._calculate_instrument_weights()

    def _calculate_instrument_weights(self) -> Dict[str, float]:
        """Calculate weights for different instruments based on cultural significance."""

        # Traditional Chinese instruments with therapy relevance weights
        weights = {
            'erhu': 0.95,      # High emotional expression
            'guqin': 0.90,     # Meditative, scholarly
            'guzheng': 0.85,   # Accessible, bright
            'pipa': 0.80,      # Dramatic, storytelling
            'dizi': 0.75,      # Natural, pastoral
            'xiao': 0.85,      # Deep, contemplative
            'yangqin': 0.70,   # Rhythmic, decorative
            'unknown': 0.50    # Default for unknown instruments
        }

        return weights

    def recommend_tracks(self,
                        preferences: Dict,
                        num_recommendations: int = 10,
                        include_scores: bool = True) -> List[Dict]:
        """
        Recommend tracks based on user preferences.

        Args:
            preferences: Dict with keys like 'era', 'instruments', 'mood', 'tempo'
            num_recommendations: Number of tracks to recommend
            include_scores: Whether to include recommendation scores

        Returns:
            List of recommended tracks with metadata
        """

        df = self.dataset.copy()

        # Calculate recommendation scores
        df['recommendation_score'] = df.apply(
            lambda row: self._calculate_track_score(row, preferences), axis=1
        )

        # Sort by score and take top recommendations
        recommendations = df.nlargest(num_recommendations, 'recommendation_score')

        # Convert to list of dictionaries
        result = []
        for _, track in recommendations.iterrows():
            track_dict = track.to_dict()
            if include_scores:
                track_dict['final_score'] = track['recommendation_score']
            result.append(track_dict)

        return result

    def _calculate_track_score(self, track: pd.Series, preferences: Dict) -> float:
        """Calculate recommendation score for a track given preferences."""

        score = 0.0

        # Era matching (weight: 0.3)
        if 'era' in preferences:
            if track['era'] == preferences['era']:
                score += 0.3
            elif track['era'] == 'traditional':  # Traditional always gets some points
                score += 0.15

        # Instrument matching (weight: 0.25)
        if 'instruments' in preferences:
            pref_instruments = preferences['instruments']
            if isinstance(pref_instruments, str):
                pref_instruments = [pref_instruments]

            track_instruments = track['instruments']
            if isinstance(track_instruments, str):
                track_instruments = [track_instruments]

            # Calculate instrument overlap
            overlap = len(set(pref_instruments) & set(track_instruments))
            if overlap > 0:
                instrument_score = overlap / len(pref_instruments)

                # Apply instrument therapy weights
                weighted_score = 0
                for instrument in track_instruments:
                    weighted_score += self.instrument_weights.get(instrument, 0.5)
                weighted_score /= len(track_instruments)

                score += 0.25 * instrument_score * weighted_score

        # Mood matching (weight: 0.2)
        if 'mood' in preferences:
            if track['mood'] == preferences['mood']:
                score += 0.2
            elif track['mood'] in ['peaceful', 'nostalgic']:  # Therapeutic moods
                score += 0.1

        # Tempo matching (weight: 0.15)
        if 'tempo' in preferences:
            if track['tempo'] == preferences['tempo']:
                score += 0.15
            elif track['tempo'] == 'slow':  # Slow tempo preferred for therapy
                score += 0.075

        # Cultural authenticity bonus (weight: 0.1)
        authenticity_score = track.get('cultural_authenticity_score', 0.5)
        score += 0.1 * authenticity_score

        return score

    def get_balanced_session_tracks(self,
                                   session_preferences: Dict,
                                   num_tracks: int = 6) -> List[Dict]:
        """
        Get a balanced set of tracks for a therapy session.

        Args:
            session_preferences: Overall session preferences
            num_tracks: Number of tracks for the session

        Returns:
            List of tracks balanced for variety and therapeutic value
        """

        # Get initial recommendations
        candidates = self.recommend_tracks(session_preferences, num_tracks * 2)

        # Balance by mood and tempo
        selected_tracks = []
        used_tracks = set()

        # Ensure mood diversity
        mood_counts = {'peaceful': 0, 'nostalgic': 0, 'melancholic': 0, 'joyful': 0}
        max_per_mood = max(1, num_tracks // len(mood_counts))

        for track in candidates:
            if len(selected_tracks) >= num_tracks:
                break

            track_id = track['track_id']
            if track_id in used_tracks:
                continue

            track_mood = track.get('mood', 'peaceful')

            # Check mood balance
            if mood_counts.get(track_mood, 0) < max_per_mood:
                selected_tracks.append(track)
                used_tracks.add(track_id)
                mood_counts[track_mood] = mood_counts.get(track_mood, 0) + 1

        # Fill remaining slots with highest scoring tracks
        for track in candidates:
            if len(selected_tracks) >= num_tracks:
                break

            track_id = track['track_id']
            if track_id not in used_tracks:
                selected_tracks.append(track)
                used_tracks.add(track_id)

        return selected_tracks[:num_tracks]

    def get_dataset_statistics(self) -> Dict:
        """Get statistics about the loaded dataset."""

        stats = {
            'total_tracks': len(self.dataset),
            'eras': self.dataset['era'].value_counts().to_dict(),
            'moods': self.dataset['mood'].value_counts().to_dict(),
            'tempos': self.dataset['tempo'].value_counts().to_dict(),
            'avg_duration': self.dataset['duration'].mean(),
            'avg_authenticity': self.dataset['cultural_authenticity_score'].mean(),
        }

        # Instrument statistics
        all_instruments = []
        for instruments in self.dataset['instruments']:
            if isinstance(instruments, list):
                all_instruments.extend(instruments)
            else:
                all_instruments.append(instruments)

        instrument_counts = pd.Series(all_instruments).value_counts()
        stats['instruments'] = instrument_counts.to_dict()

        return stats

# Example usage and testing
if __name__ == "__main__":
    # Test the recommendation engine
    loader = CCMusicDatasetLoader("data/ccmusic-database-demo")
    df = loader.load_dataset()

    print(f"Loaded {len(df)} tracks")
    print("\nDataset overview:")
    print(df[['track_id', 'title', 'era', 'mood', 'cultural_authenticity_score']].head())

    # Create recommendation engine
    recommender = TCMRecommendationEngine(df)

    # Test recommendations
    preferences = {
        'era': '1950s',
        'instruments': ['erhu', 'guqin'],
        'mood': 'nostalgic',
        'tempo': 'slow'
    }

    recommendations = recommender.recommend_tracks(preferences, num_recommendations=5)

    print(f"\nTop 5 recommendations for {preferences}:")
    for i, track in enumerate(recommendations, 1):
        print(f"{i}. {track['title']} - Score: {track.get('final_score', 0):.3f}")

    # Test session tracks
    session_tracks = recommender.get_balanced_session_tracks(preferences, num_tracks=6)
    print(f"\nBalanced session playlist ({len(session_tracks)} tracks):")
    for i, track in enumerate(session_tracks, 1):
        print(f"{i}. {track['title']} ({track['mood']}, {track['tempo']})")

    # Dataset statistics
    stats = recommender.get_dataset_statistics()
    print(f"\nDataset statistics:")
    print(f"Total tracks: {stats['total_tracks']}")
    print(f"Eras: {stats['eras']}")
    print(f"Top instruments: {dict(list(stats['instruments'].items())[:5])}")