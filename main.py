#!/usr/bin/env python3
"""
Traditional Chinese Music Therapy AI Study - Main Execution Script
Fixed version with proper error handling and import paths
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('study_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_project_structure():
    """Create necessary directories for the project."""
    logger.info("Setting up project structure...")

    directories = [
        'data/ccmusic-database-demo',
        'data/session_data',
        'data/generated_music',
        'config',
        'results/plots',
        'results/reports',
        'logs'
    ]

    for directory in directories:
        dir_path = Path(directory)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created/verified directory: {directory}")
        except Exception as e:
            logger.error(f"❌ Failed to create directory {directory}: {e}")
            return False

    return True

def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("Checking dependencies...")

    required_packages = [
        'torch', 'transformers', 'streamlit', 'pandas', 'numpy',
        'scipy', 'matplotlib', 'plotly', 'soundfile', 'librosa'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package}")
        except ImportError:
            logger.error(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)

    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.error("Install with: pip install " + " ".join(missing_packages))
        return False

    logger.info("✅ All dependencies check passed")
    return True

def load_dataset():
    """Load and prepare the ccmusic dataset."""
    logger.info("Loading ccmusic dataset...")

    try:
        # Import with proper error handling
        from src.tcm_recommender import CCMusicDatasetLoader

        dataset_path = "data/ccmusic-database-demo"

        # Check if dataset exists
        if not Path(dataset_path).exists():
            logger.warning(f"Real dataset not found at {dataset_path}")
            logger.info("Using sample data for development/testing")

        loader = CCMusicDatasetLoader(dataset_path)
        df = loader.load_dataset()

        logger.info(f"✅ Loaded {len(df)} tracks from dataset")

        # Save dataset summary
        summary = {
            'total_tracks': len(df),
            'eras': df['era'].value_counts().to_dict() if 'era' in df else {},
            'moods': df['mood'].value_counts().to_dict() if 'mood' in df else {},
            'loaded_at': datetime.now().isoformat(),
            'data_source': 'real_dataset' if Path(dataset_path).exists() else 'sample_data'
        }

        os.makedirs('data', exist_ok=True)
        with open('data/dataset_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        return df

    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        logger.info("This is normal if running for the first time")
        return None

def generate_ai_music(df, num_tracks=3):
    """Generate AI music variations from selected tracks."""
    logger.info(f"Generating AI music variations for {num_tracks} tracks...")

    try:
        from src.musicgen_generator import TCMMusicGenerator, GenerationConfig

        # Use smaller model and shorter clips for testing
        config = GenerationConfig(
            model_name="facebook/musicgen-small",  # Smaller model for testing
            max_new_tokens=128,  # ~10 seconds (faster)
            temperature=1.0
        )

        generator = TCMMusicGenerator(config)
        logger.info("✅ MusicGen generator initialized")

        # Select tracks for generation
        if df is not None and len(df) > 0:
            if 'cultural_authenticity_score' in df.columns:
                selected_tracks = df.nlargest(num_tracks, 'cultural_authenticity_score')
            else:
                selected_tracks = df.head(num_tracks)
        else:
            logger.warning("No dataset available, skipping AI generation")
            return []

        generated_tracks = []

        for i, (_, track) in enumerate(selected_tracks.iterrows()):
            logger.info(f"Generating variations for track {i+1}/{num_tracks}: {track.get('title', track.get('track_id', 'Unknown'))}")

            try:
                # Convert series to dict
                track_metadata = track.to_dict()

                # Ensure required fields exist
                if 'instruments' not in track_metadata or not track_metadata['instruments']:
                    track_metadata['instruments'] = ['erhu', 'guqin']
                if 'era' not in track_metadata:
                    track_metadata['era'] = '1950s'
                if 'mood' not in track_metadata:
                    track_metadata['mood'] = 'nostalgic'
                if 'tempo' not in track_metadata:
                    track_metadata['tempo'] = 'slow'

                variations = generator.generate_variations(
                    track_metadata,
                    num_variations=1,  # Just 1 variation for testing
                    use_melody_conditioning=False  # Disable for stability
                )

                # Save variations
                os.makedirs("data/generated_music", exist_ok=True)
                for variation in variations:
                    filepath = generator.save_variation(
                        variation,
                        "data/generated_music"
                    )
                    generated_tracks.append({
                        'original_track_id': track['track_id'],
                        'variation_id': variation['variation_id'],
                        'filepath': filepath,
                        'prompt': variation['prompt']
                    })
                    logger.info(f"   ✅ Saved: {filepath}")

            except Exception as e:
                logger.error(f"Failed to generate for track {track.get('track_id', 'unknown')}: {e}")
                continue

        # Save generation summary
        generation_summary = {
            'total_generated': len(generated_tracks),
            'generated_tracks': generated_tracks,
            'generated_at': datetime.now().isoformat()
        }

        with open('data/generation_summary.json', 'w') as f:
            json.dump(generation_summary, f, indent=2)

        logger.info(f"✅ Generated {len(generated_tracks)} AI music variations")
        return generated_tracks

    except Exception as e:
        logger.error(f"AI music generation failed: {e}")
        logger.info("This is normal if GPU/model requirements aren't met")
        return []

def prepare_session_materials(df, generated_tracks):
    """Prepare materials for therapy sessions."""
    logger.info("Preparing session materials...")

    try:
        session_tracks = []

        # Add original tracks (use sample data if no real dataset)
        if df is not None and len(df) > 0:
            # Select representative tracks
            selected_original = df.head(5)  # Take first 5 tracks

            for _, track in selected_original.iterrows():
                track_dict = track.to_dict()

                # Ensure all required fields exist
                session_track = {
                    'track_id': track_dict.get('track_id', f"original_{len(session_tracks)}"),
                    'title': track_dict.get('title', 'Traditional Chinese Music'),
                    'type': 'original',
                    'era': track_dict.get('era', '1950s'),
                    'instruments': track_dict.get('instruments', ['erhu']),
                    'mood': track_dict.get('mood', 'nostalgic'),
                    'tempo': track_dict.get('tempo', 'slow'),
                    'duration': track_dict.get('duration', 180),
                    'file_path': track_dict.get('file_path', 'original_track.wav'),
                    'cultural_authenticity_score': track_dict.get('cultural_authenticity_score', 0.8)
                }

                # Ensure instruments is a list
                if isinstance(session_track['instruments'], str):
                    session_track['instruments'] = [session_track['instruments']]

                session_tracks.append(session_track)

        # Add generated tracks
        for gen_track in generated_tracks:
            try:
                # Find original track info if available
                original_id = gen_track['original_track_id']
                if df is not None:
                    original_match = df[df['track_id'] == original_id]
                    if not original_match.empty:
                        original_track = original_match.iloc[0]
                    else:
                        # Use default values
                        original_track = {
                            'title': 'Traditional Chinese Music',
                            'era': '1950s',
                            'instruments': ['erhu'],
                            'mood': 'nostalgic',
                            'tempo': 'slow'
                        }
                else:
                    original_track = {
                        'title': 'Traditional Chinese Music',
                        'era': '1950s',
                        'instruments': ['erhu'],
                        'mood': 'nostalgic',
                        'tempo': 'slow'
                    }

                session_tracks.append({
                    'track_id': gen_track['variation_id'],
                    'title': f"{original_track.get('title', 'TCM')} (AI Variation)",
                    'type': 'generated',
                    'era': original_track.get('era', '1950s'),
                    'instruments': original_track.get('instruments', ['erhu']),
                    'mood': original_track.get('mood', 'nostalgic'),
                    'tempo': original_track.get('tempo', 'slow'),
                    'duration': 180,
                    'file_path': gen_track['filepath'],
                    'original_track_id': gen_track['original_track_id'],
                    'generation_prompt': gen_track['prompt'],
                    'cultural_authenticity_score': 0.75
                })
            except Exception as e:
                logger.error(f"Failed to process generated track: {e}")
                continue

        # Ensure we have some tracks even if everything failed
        if not session_tracks:
            logger.warning("No tracks prepared, creating minimal sample tracks")
            session_tracks = [
                {
                    'track_id': 'sample_001',
                    'title': 'Sample Traditional Chinese Music',
                    'type': 'original',
                    'era': '1950s',
                    'instruments': ['erhu'],
                    'mood': 'nostalgic',
                    'tempo': 'slow',
                    'duration': 180,
                    'file_path': 'sample_track.wav',
                    'cultural_authenticity_score': 0.8
                }
            ]

        # Save session materials
        os.makedirs('data', exist_ok=True)
        with open('data/session_tracks.json', 'w', encoding='utf-8') as f:
            json.dump(session_tracks, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Prepared {len(session_tracks)} tracks for sessions")
        logger.info(f"   Original tracks: {sum(1 for t in session_tracks if t['type'] == 'original')}")
        logger.info(f"   Generated tracks: {sum(1 for t in session_tracks if t['type'] == 'generated')}")

        return session_tracks

    except Exception as e:
        logger.error(f"Failed to prepare session materials: {e}")
        return []

def launch_session_interface():
    """Launch the Streamlit session interface."""
    logger.info("Launching session interface...")

    try:
        logger.info("🌐 Starting Streamlit session runner...")
        logger.info("   Navigate to: http://localhost:8501")
        logger.info("   Press Ctrl+C to stop the interface")

        # Check if session_runner.py exists
        if not Path("session_runner.py").exists():
            logger.error("session_runner.py not found in current directory")
            return False

        # Launch Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            'session_runner.py',
            '--server.port', '8501',
            '--server.headless', 'false'
        ])

        return True

    except KeyboardInterrupt:
        logger.info("Session interface stopped by user")
        return True
    except Exception as e:
        logger.error(f"Failed to launch session interface: {e}")
        return False

def analyze_session_data():
    """Analyze collected session data."""
    logger.info("Analyzing session data...")

    try:
        from src.analysis_tools import SmallNAnalyzer
        import pandas as pd

        # Check for session data
        session_log_path = "data/session_data/session_log.csv"
        if not Path(session_log_path).exists():
            logger.warning("No session data found for analysis")
            logger.info("Session data will be created as participants complete sessions")
            return False

        # Load and analyze data
        session_data = pd.read_csv(session_log_path)
        logger.info(f"Loaded {len(session_data)} session responses")

        if len(session_data) < 4:
            logger.warning("Insufficient data for meaningful analysis (need at least 4 responses)")
            return False

        # Initialize analyzer
        analyzer = SmallNAnalyzer(session_data)

        # Perform analysis
        effect_sizes = analyzer.calculate_effect_sizes()
        statistical_tests = analyzer.perform_statistical_tests()
        individual_patterns = analyzer.analyze_individual_patterns()

        # Generate comprehensive report
        os.makedirs("results/reports", exist_ok=True)
        report_path = analyzer.generate_report("results/reports/study_analysis_report.html")

        # Create visualizations
        plots_dir = "results/plots"
        os.makedirs(plots_dir, exist_ok=True)
        plots = analyzer.create_visualizations(plots_dir)

        logger.info(f"✅ Analysis complete!")
        logger.info(f"   Report: {report_path}")
        logger.info(f"   Plots: {plots_dir}")

        return True

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return False

def main():
    """Main study execution function."""
    parser = argparse.ArgumentParser(description="Traditional Chinese Music Therapy AI Study")
    parser.add_argument('--setup', action='store_true', help='Setup project structure and check dependencies')
    parser.add_argument('--generate-music', action='store_true', help='Generate AI music variations')
    parser.add_argument('--launch-interface', action='store_true', help='Launch session interface')
    parser.add_argument('--analyze', action='store_true', help='Analyze session data')
    parser.add_argument('--full-setup', action='store_true', help='Complete setup workflow')
    parser.add_argument('--test', action='store_true', help='Run system tests')
    parser.add_argument('--num-tracks', type=int, default=3, help='Number of tracks for AI generation')

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        print("\n🚀 Quick start: python main.py --full-setup")
        return 0

    # Setup logging
    logger.info("Starting Traditional Chinese Music Therapy AI Study")
    logger.info(f"Arguments: {vars(args)}")

    success = True

    try:
        if args.test:
            # Run system tests
            logger.info("Running system tests...")
            try:
                result = subprocess.run([sys.executable, 'test_installation.py'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("✅ System tests passed")
                else:
                    logger.error("❌ System tests failed")
                    print(result.stdout)
                    print(result.stderr)
                    success = False
            except FileNotFoundError:
                logger.warning("test_installation.py not found, skipping system tests")

        if args.setup or args.full_setup:
            success &= setup_project_structure()
            success &= check_dependencies()

            # Load dataset
            df = load_dataset()
            # Note: df can be None and that's OK for development

            if success:
                logger.info("✅ Setup completed successfully")
            else:
                logger.error("❌ Setup encountered errors")

        if args.generate_music or args.full_setup:
            # Load dataset if not already loaded
            if 'df' not in locals():
                df = load_dataset()

            generated_tracks = generate_ai_music(df, args.num_tracks)
            session_tracks = prepare_session_materials(df, generated_tracks)

            if session_tracks:
                logger.info("✅ Session materials prepared")
            else:
                logger.error("❌ Session material preparation failed")
                success = False

        if args.launch_interface:
            interface_success = launch_session_interface()
            if not interface_success:
                success = False

        if args.analyze:
            analysis_success = analyze_session_data()
            if not analysis_success:
                logger.warning("Analysis completed with warnings or insufficient data")

        if args.full_setup and success:
            print("\n" + "="*70)
            print("🎉 TRADITIONAL CHINESE MUSIC THERAPY AI STUDY - READY!")
            print("="*70)
            print("\n📁 Project Structure:")
            print("   ├── data/session_data/     # Session logs will be saved here")
            print("   ├── data/session_tracks.json  # Available tracks for sessions")
            print("   ├── config/               # Study configuration files")
            print("   └── results/              # Analysis outputs")

            print("\n🚀 Next Steps:")
            print("   1. Launch interface:  python main.py --launch-interface")
            print("   2. Or manually:       streamlit run session_runner.py")
            print("   3. Navigate to:       http://localhost:8501")
            print("   4. Start sessions with participants!")

            print("\n💡 Testing Tips:")
            print("   • Use participant ID: test_participant_001")
            print("   • Try 4-6 tracks per session")
            print("   • Rate responses on 1-10 scales")
            print("   • Add notes about specific reactions")

            # Ask if user wants to launch interface
            try:
                response = input("\n🚀 Launch session interface now? (y/N): ")
                if response.lower() in ['y', 'yes']:
                    launch_session_interface()
            except (KeyboardInterrupt, EOFError):
                print("\nSkipping interface launch.")

    except KeyboardInterrupt:
        logger.info("Study execution interrupted by user")
    except Exception as e:
        logger.error(f"Study execution failed: {e}")
        success = False

    if success:
        logger.info("🎉 Study execution completed successfully!")
        return 0
    else:
        logger.error("❌ Study execution completed with errors")
        print("\n🔧 Troubleshooting:")
        print("   1. Run: python test_installation.py")
        print("   2. Check logs: study_execution.log")
        print("   3. Install missing deps: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)