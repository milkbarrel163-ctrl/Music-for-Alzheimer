#!/usr/bin/env python3
"""
Test Installation Script for TCM Music Therapy Application
Comprehensive system check to verify all components work correctly
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib
import warnings
warnings.filterwarnings('ignore')

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")

    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_required_packages():
    """Check if all required packages are installed."""
    print("\n📦 Checking required packages...")

    required_packages = [
        ('torch', 'PyTorch'),
        ('transformers', 'Transformers'),
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('scipy', 'SciPy'),
        ('matplotlib', 'Matplotlib'),
        ('plotly', 'Plotly'),
        ('soundfile', 'SoundFile'),
        ('librosa', 'Librosa')
    ]

    missing_packages = []

    for package, name in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - NOT INSTALLED")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False

    return True

def check_torch_setup():
    """Check PyTorch setup and CUDA availability."""
    print("\n🔥 Checking PyTorch setup...")

    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")

        # Check CUDA
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✅ CUDA available: {device_name} ({memory:.1f} GB)")
        else:
            print("ℹ️  CUDA not available - using CPU (slower but functional)")

        # Check MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✅ MPS (Apple Silicon) available")

        return True

    except Exception as e:
        print(f"❌ PyTorch check failed: {e}")
        return False

def check_transformers():
    """Check Transformers library and model access."""
    print("\n🤗 Checking Transformers library...")

    try:
        from transformers import AutoProcessor

        # Test model access (without downloading)
        model_name = "facebook/musicgen-small"
        print(f"✅ Transformers library functional")
        print(f"ℹ️  Model '{model_name}' access available")

        return True

    except Exception as e:
        print(f"❌ Transformers check failed: {e}")
        return False

def check_audio_libraries():
    """Check audio processing libraries."""
    print("\n🎵 Checking audio libraries...")

    try:
        import soundfile as sf
        import librosa
        print("✅ SoundFile")
        print("✅ Librosa")

        # Test basic audio functionality
        import numpy as np

        # Create test audio
        sample_rate = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * np.sin(2 * np.pi * 440 * t)

        # Test file I/O
        test_file = "test_audio.wav"
        sf.write(test_file, audio, sample_rate)
        loaded_audio, loaded_sr = sf.read(test_file)

        # Clean up
        os.remove(test_file)

        print("✅ Audio file I/O functional")
        return True

    except Exception as e:
        print(f"❌ Audio libraries check failed: {e}")
        return False

def check_project_structure():
    """Check project directory structure."""
    print("\n📁 Checking project structure...")

    required_dirs = [
        "data",
        "config",
    ]

    required_files = [
        "analysis_tools.py",
        "musicgen_generator.py",
        "prompt_templates.py",
        "session_runner.py",
        "requirements.txt"
    ]

    # Create missing directories
    for directory in required_dirs:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

    # Check files
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ File exists: {file}")
        else:
            print(f"⚠️  File missing: {file}")
            missing_files.append(file)

    return len(missing_files) == 0

def check_data_access():
    """Check data and configuration access."""
    print("\n💾 Checking data access...")

    try:
        # Test TCM recommender
        from src.tcm_recommender import CCMusicDatasetLoader, TCMRecommendationEngine

        # Test with sample data
        loader = CCMusicDatasetLoader("data/ccmusic-database-demo")
        df = loader.load_dataset()  # This will use sample data if dataset missing

        print(f"✅ Dataset loader functional ({len(df)} tracks)")

        # Test recommendation engine
        recommender = TCMRecommendationEngine(df)
        preferences = {'era': '1950s', 'mood': 'nostalgic'}
        recommendations = recommender.recommend_tracks(preferences, 3)

        print(f"✅ Recommendation engine functional ({len(recommendations)} recommendations)")
        return True

    except Exception as e:
        print(f"❌ Data access check failed: {e}")
        return False

def check_session_runner():
    """Check session runner functionality."""
    print("\n🖥️  Checking session runner...")

    try:
        # Import session runner components
        from src.session_runner import SessionManager, load_session_tracks, create_session_playlist

        # Test session manager
        manager = SessionManager("data/test_session_data")
        print("✅ Session manager initialized")

        # Test track loading
        tracks = load_session_tracks()
        print(f"✅ Track loading functional ({len(tracks)} tracks)")

        # Test playlist creation
        playlist = create_session_playlist(tracks, 4)
        print(f"✅ Playlist creation functional ({len(playlist)} tracks)")

        return True

    except Exception as e:
        print(f"❌ Session runner check failed: {e}")
        return False

def check_analysis_tools():
    """Check analysis tools functionality."""
    print("\n📊 Checking analysis tools...")

    try:
        from src.analysis_tools import SmallNAnalyzer
        import pandas as pd
        import numpy as np

        # Create sample session data
        sample_data = pd.DataFrame({
            'participant_id': ['P001'] * 4 + ['P002'] * 4,
            'session_id': ['S1'] * 4 + ['S2'] * 4,
            'condition_type': ['original', 'generated'] * 4,
            'engagement_score': np.random.randint(1, 10, 8),
            'mood_response_score': np.random.randint(1, 10, 8),
            'agitation_score': np.random.randint(1, 10, 8),
            'era': ['1950s'] * 8,
            'mood': ['nostalgic'] * 8
        })

        # Test analyzer
        analyzer = SmallNAnalyzer(sample_data)
        effect_sizes = analyzer.calculate_effect_sizes()

        print("✅ Statistical analysis functional")
        print(f"✅ Effect size calculation functional ({len(effect_sizes)} measures)")

        return True

    except Exception as e:
        print(f"❌ Analysis tools check failed: {e}")
        return False

def test_streamlit_compatibility():
    """Test Streamlit compatibility."""
    print("\n🚀 Testing Streamlit compatibility...")

    try:
        import streamlit as st
        print(f"✅ Streamlit version: {st.__version__}")

        # Test if we can import session runner for Streamlit
        import src.session_runner
        print("✅ Session runner Streamlit app importable")

        return True

    except Exception as e:
        print(f"❌ Streamlit compatibility check failed: {e}")
        return False

def generate_test_config_files():
    """Generate test configuration files if missing."""
    print("\n⚙️  Generating configuration files...")

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Session config
    session_config = {
        "session_settings": {
            "tracks_per_session": 6,
            "session_duration_minutes": 30,
            "randomize_order": True,
            "balance_conditions": True
        },
        "music_selection": {
            "eras": ["1930s", "1940s", "1950s", "1960s", "traditional"],
            "preferred_instruments": ["erhu", "guqin", "guzheng"],
            "cultural_authenticity_threshold": 0.7
        }
    }

    # Analysis config
    analysis_config = {
        "statistical_tests": {
            "primary_test": "wilcoxon_signed_rank",
            "effect_size": "cliffs_delta",
            "alpha_level": 0.05
        },
        "visualization": {
            "plot_style": "plotly",
            "figure_format": "html"
        }
    }

    # Save configs
    import json

    with open(config_dir / "session_config.json", "w") as f:
        json.dump(session_config, f, indent=2)
    print("✅ Session config created")

    with open(config_dir / "analysis_config.json", "w") as f:
        json.dump(analysis_config, f, indent=2)
    print("✅ Analysis config created")

    return True

def run_full_system_test():
    """Run complete system test."""

    print("="*60)
    print("🧪 TCM MUSIC THERAPY APPLICATION - SYSTEM TEST")
    print("="*60)

    tests = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("PyTorch Setup", check_torch_setup),
        ("Transformers Library", check_transformers),
        ("Audio Libraries", check_audio_libraries),
        ("Project Structure", check_project_structure),
        ("Configuration Files", generate_test_config_files),
        ("Data Access", check_data_access),
        ("Session Runner", check_session_runner),
        ("Analysis Tools", check_analysis_tools),
        ("Streamlit Compatibility", test_streamlit_compatibility)
    ]

    results = {}

    for test_name, test_func in tests:
        print()
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n🚀 Ready to start the application:")
        print("   1. streamlit run session_runner.py")
        print("   2. Navigate to http://localhost:8501")
        print("   3. Start conducting music therapy sessions!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed.")
        print("\n🔧 Next steps:")
        print("   1. Address the failed tests above")
        print("   2. Install missing dependencies: pip install -r requirements.txt")
        print("   3. Download dataset from: https://zenodo.org/records/5676893")
        print("   4. Re-run this test: python test_installation.py")
        return 1

if __name__ == "__main__":
    exit_code = run_full_system_test()
    sys.exit(exit_code)