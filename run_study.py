import json
from pathlib import Path
from src.tcm_recommender import CCMusicDatasetLoader, TCMRecommendationEngine
from src.musicgen_generator import TCMMusicGenerator
from src.session_runner import SessionManager
from src.analysis_tools import SmallNAnalyzer

def run_complete_study():
    """Execute complete music therapy study workflow."""

    print("=== Traditional Chinese Music Therapy Study ===\n")

    # 1. Load and prepare dataset
    print("1. Loading ccmusic dataset...")
    loader = CCMusicDatasetLoader("data/ccmusic-database-demo")
    df = loader.load_dataset()
    print(f"   Loaded {len(df)} tracks from {df['era'].nunique()} eras")

    # 2. Create recommendation engine
    print("2. Building recommendation engine...")
    recommender = TCMRecommendationEngine(df)
    print("   Recommendation engine ready")

    # 3. Generate AI music variations
    print("3. Generating AI music variations...")
    generator = TCMMusicGenerator()

    # Select top tracks for variation
    top_tracks = df.nlargest(5, 'cultural_authenticity_score')

    for _, track in top_tracks.iterrows():
        variations = generator.generate_variations(
            track.to_dict(),
            num_variations=2
        )

        # Save variations
        for variation in variations:
            output_path = generator.save_variation(
                variation,
                "data/generated_music"
            )
            print(f"   Generated: {output_path}")

    # 4. Prepare session materials
    print("4. Preparing session materials...")
    session_tracks = []

    # Combine original and generated tracks
    for _, track in top_tracks.iterrows():
        session_tracks.append({
            'track_id': track['track_id'],
            'title': track['title'],
            'type': 'original',
            'era': track['era'],
            'instruments': track['instruments'],
            'mood': track['mood'],
            'tempo': track['tempo'],
            'duration': track.get('duration', 180),
            'file_path': track['file_path']
        })

    # Add generated tracks (in practice, load from saved files)

    # Save session tracks
    with open('data/session_tracks.json', 'w') as f:
        json.dump(session_tracks, f, indent=2)

    print("5. Study materials prepared!")
    print("\nNext steps:")
    print("   - Run: streamlit run src/session_runner.py")
    print("   - Conduct sessions with participants")
    print("   - Analyze results with analysis_tools.py")

if __name__ == "__main__":
    run_complete_study()