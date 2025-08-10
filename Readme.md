# Traditional Chinese Music Therapy AI Study - Setup Guide

## 🎯 Project Overview

This project implements a culturally-tailored music therapy study comparing traditional Chinese music (TCM) with AI-generated variations for Alzheimer's disease research. The system includes:

- **Music Recommendation Engine** for Traditional Chinese Music selection
- **AI Music Generation** using MusicGen with cultural prompts
- **Session Management Interface** for caregiver-friendly data collection
- **Statistical Analysis Tools** for small-N pilot study evaluation

---

## 📋 Prerequisites

### System Requirements
- **Python 3.10+** (3.11 recommended)
- **8GB+ RAM** (16GB recommended for MusicGen)
- **CUDA-compatible GPU** (optional, for faster AI generation)
- **10GB+ free disk space** (for dataset and generated audio)

### Knowledge Requirements
- **Basic Python usage** (running scripts, installing packages)
- **Command line familiarity** (navigating directories, running commands)
- **No AI/ML expertise required** (all models are pre-configured)

---

## 🚀 Quick Start (15 minutes)

### Step 1: Download and Extract
```bash
# Create project directory
mkdir tcm_music_therapy_study
cd tcm_music_therapy_study

# Download ccmusic dataset
wget https://zenodo.org/records/5676893/files/ccmusic-database-demo.zip
unzip ccmusic-database-demo.zip
```

### Step 2: Install Dependencies
```bash
# Create virtual environment
python -m venv tcm_env
source tcm_env/bin/activate  # Linux/Mac
# tcm_env\Scripts\activate  # Windows

# Install required packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118  # GPU version
# pip install torch torchvision torchaudio  # CPU-only version

pip install transformers
pip install streamlit
pip install pandas numpy scipy matplotlib seaborn
pip install plotly
pip install librosa soundfile
pip install faiss-cpu  # or faiss-gpu if CUDA available
pip install sentence-transformers
pip install mido muspy
```

### Step 3: Download Model Weights
```python
# Run this Python script to download MusicGen
from transformers import AutoProcessor, MusicgenForConditionalGeneration

# This will download ~1.5GB of model weights
processor = AutoProcessor.from_pretrained("facebook/musicgen-medium")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium")

print("Models downloaded successfully!")
```

### Step 4: Test Installation
```bash
# Test the recommendation system
python test_installation.py
```

---

## 📁 Project Structure

```
tcm_music_therapy_study/
├── data/
│   ├── ccmusic-database-demo/          # Downloaded dataset
│   ├── session_data/                   # Session logs
│   └── generated_music/                # AI-generated tracks
├── src/
│   ├── tcm_recommender.py             # Music recommendation engine
│   ├── musicgen_generator.py          # AI music generation
│   ├── session_runner.py              # Streamlit session app
│   ├── analysis_tools.py              # Statistical analysis
│   └── prompt_templates.py            # MusicGen prompts
├── config/
│   ├── session_config.json            # Session settings
│   └── analysis_config.json           # Analysis parameters
├── notebooks/
│   ├── data_exploration.ipynb         # Dataset exploration
│   └── analysis_examples.ipynb        # Analysis examples
├── requirements.txt                    # Python dependencies
├── README.md                          # This file
└── run_study.py                       # Main execution script
```

---

## 🔧 Detailed Installation

### Environment Setup

#### Option A: Conda (Recommended)
```bash
# Install Miniconda if not already installed
# https://docs.conda.io/en/latest/miniconda.html

# Create environment
conda create -n tcm_therapy python=3.11
conda activate tcm_therapy

# Install PyTorch with CUDA support
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# Install other dependencies
pip install -r requirements.txt
```

#### Option B: Virtual Environment
```bash
python -m venv tcm_env
source tcm_env/bin/activate  # Linux/Mac
# tcm_env\Scripts\activate    # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

### GPU Setup (Optional but Recommended)

#### NVIDIA GPU Configuration
```bash
# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Install CUDA-enabled packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install faiss-gpu
```

#### Apple Silicon Mac (MPS)
```bash
# PyTorch with Metal Performance Shaders
pip install torch torchvision torchaudio

# Verify MPS availability
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

---

## 📊 Dataset Setup

### Download CCMusic Dataset
```bash
# Download from Zenodo
wget https://zenodo.org/records/5676893/files/ccmusic-database-demo.zip

# Alternative: Manual download
# Visit: https://zenodo.org/records/5676893
# Download ccmusic-database-demo.zip (~302 MB)

# Extract
unzip ccmusic-database-demo.zip -d data/
```

### Verify Dataset Structure
```python
import os
from pathlib import Path

dataset_path = Path("data/ccmusic-database-demo")
print(f"Dataset exists: {dataset_path.exists()}")

# Check subdirectories
for subdir in dataset_path.iterdir():
    if subdir.is_dir():
        file_count = len(list(subdir.rglob("*")))
        print(f"{subdir.name}: {file_count} files")
```

---

## ⚙️ Configuration

### Session Configuration
Create `config/session_config.json`:
```json
{
  "session_settings": {
    "tracks_per_session": 6,
    "session_duration_minutes": 30,
    "randomize_order": true,
    "balance_conditions": true
  },
  "music_selection": {
    "eras": ["1930s", "1940s", "1950s", "1960s", "traditional"],
    "preferred_instruments": ["erhu", "guqin", "guzheng", "pipa"],
    "cultural_authenticity_threshold": 0.7
  },
  "generation_settings": {
    "model_name": "facebook/musicgen-medium",
    "max_duration_seconds": 180,
    "temperature": 1.0,
    "use_melody_conditioning": true
  }
}
```

### Analysis Configuration
Create `config/analysis_config.json`:
```json
{
  "statistical_tests": {
    "primary_test": "wilcoxon_signed_rank",
    "effect_size": "cliffs_delta",
    "alpha_level": 0.05,
    "confidence_interval": 0.95
  },
  "visualization": {
    "plot_style": "plotly",
    "color_scheme": "husl",
    "figure_format": "html",
    "include_individual_trajectories": true
  },
  "export_settings": {
    "include_raw_data": true,
    "anonymize_participants": true,
    "data_dictionary": true
  }
}
```

---

## 🎵 Usage Examples

### 1. Load and Explore Dataset
```python
from src.tcm_recommender import CCMusicDatasetLoader

# Load dataset
loader = CCMusicDatasetLoader("data/ccmusic-database-demo")
df = loader.load_dataset()

print(f"Loaded {len(df)} tracks")
print(f"Eras: {df['era'].value_counts()}")
print(f"Instruments: {df['instruments'].explode().value_counts().head()}")
```

### 2. Generate Music Recommendations
```python
from src.tcm_recommender import TCMRecommendationEngine

# Create recommendation engine
recommender = TCMRecommendationEngine(df)

# Get recommendations for elderly Chinese listener
preferences = {
    'era': '1950s',
    'instruments': ['erhu', 'guqin'],
    'mood': 'nostalgic',
    'tempo': 'slow'
}

recommendations = recommender.recommend_tracks(preferences, num_recommendations=5)

for i, track in enumerate(recommendations, 1):
    print(f"{i}. {track['title']} ({track['era']}) - Score: {track['final_score']:.3f}")
```

### 3. Generate AI Music Variations
```python
from src.musicgen_generator import TCMMusicGenerator, GenerationConfig

# Initialize generator
config = GenerationConfig(
    model_name="facebook/musicgen-medium",
    max_new_tokens=256,  # ~20 seconds
    temperature=1.0
)

generator = TCMMusicGenerator(config)

# Generate variations
track_metadata = {
    'track_id': 'traditional_001',
    'title': 'Spring River in Flower Moon Night',
    'instruments': ['guzheng', 'erhu'],
    'era': '1950s',
    'mood': 'nostalgic',
    'tempo': 'slow',
    'cultural_authenticity_score': 0.9
}

variations = generator.generate_variations(
    track_metadata,
    num_variations=3,
    use_melody_conditioning=True
)

for variation in variations:
    print(f"Generated: {variation['variation_id']} ({variation['duration']:.1f}s)")
```

### 4. Run Session Interface
```bash
# Launch Streamlit app
streamlit run src/session_runner.py

# Navigate to http://localhost:8501 in web browser
# Follow on-screen instructions for session management
```

### 5. Analyze Session Data
```python
from src.analysis_tools import SmallNAnalyzer
import pandas as pd

# Load session data
session_data = pd.read_csv("data/session_data/session_log.csv")

# Create analyzer
analyzer = SmallNAnalyzer(session_data)

# Perform statistical analysis
effect_sizes = analyzer.calculate_effect_sizes()
statistical_tests = analyzer.perform_statistical_tests()

# Generate comprehensive report
report_path = analyzer.generate_report("analysis_results.html")
print(f"Analysis complete! Report saved to: {report_path}")
```

---

## 🎯 Running a Complete Study

### Full Study Workflow
```python
# run_study.py - Complete study execution script

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
```

### Running Sessions
```bash
# 1. Launch session interface
streamlit run src/session_runner.py

# 2. Follow web interface:
#    - Enter participant ID
#    - Configure session settings
#    - Start new session
#    - Play tracks and record responses
#    - Review session summary

# 3. Data is automatically saved to:
#    data/session_data/session_log.csv
```

### Analysis and Reporting
```bash
# Run analysis on collected data
python -c "
from src.analysis_tools import SmallNAnalyzer
import pandas as pd

# Load session data
data = pd.read_csv('data/session_data/session_log.csv')

# Analyze
analyzer = SmallNAnalyzer(data)
report = analyzer.generate_report('study_results.html')

print(f'Analysis complete: {report}')
"
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. CUDA Out of Memory
```python
# Reduce model size or use CPU
config = GenerationConfig(
    model_name="facebook/musicgen-small",  # Smaller model
    max_new_tokens=128  # Shorter generation
)

# Or force CPU usage
import torch
device = torch.device("cpu")
generator = TCMMusicGenerator(config)
generator.model.to(device)
```

#### 2. Dataset Loading Errors
```python
# Check dataset path
import os
dataset_path = "data/ccmusic-database-demo"
print(f"Path exists: {os.path.exists(dataset_path)}")
print(f"Contents: {os.listdir(dataset_path) if os.path.exists(dataset_path) else 'Not found'}")

# Alternative dataset location
loader = CCMusicDatasetLoader("/path/to/your/ccmusic-database-demo")
```

#### 3. Streamlit Issues
```bash
# Clear cache
streamlit cache clear

# Run on different port
streamlit run src/session_runner.py --server.port 8502

# Check firewall settings for port access
```

#### 4. Audio Playback Problems
```python
# Test audio libraries
import soundfile as sf
import librosa

# Test file loading
audio, sr = librosa.load("test_audio.wav")
print(f"Loaded audio: {len(audio)} samples at {sr} Hz")

# Alternative audio backends
import torchaudio
torchaudio.set_audio_backend("soundfile")  # or "sox_io"
```

### Performance Optimization

#### Memory Management
```python
# Clear GPU memory between generations
import torch
torch.cuda.empty_cache()

# Use mixed precision for MusicGen
from transformers import MusicgenForConditionalGeneration
model = MusicgenForConditionalGeneration.from_pretrained(
    "facebook/musicgen-medium",
    torch_dtype=torch.float16  # Half precision
)
```

#### Batch Processing
```python
# Generate multiple variations efficiently
def batch_generate_variations(tracks, generator):
    all_variations = []

    for track in tracks:
        try:
            variations = generator.generate_variations(track, num_variations=2)
            all_variations.extend(variations)

            # Clear memory
            torch.cuda.empty_cache()

        except Exception as e:
            print(f"Failed to generate for {track['track_id']}: {e}")
            continue

    return all_variations
```

---

## 📚 Additional Resources

### Documentation
- **MusicGen Paper:** [Simple and Controllable Music Generation](https://arxiv.org/abs/2306.05284)
- **CCMusic Dataset:** [Multi-functional Music Database](https://zenodo.org/records/5676893)
- **Streamlit Docs:** [Building Data Apps](https://docs.streamlit.io/)

### Example Studies
- **Bleibel et al. (2023):** [Music therapy systematic review](https://doi.org/10.1186/s13195-023-01214-9)
- **Moreira et al. (2023):** [Episodic memory enhancement](https://doi.org/10.3390/healthcare11222912)

### Technical References
- **Small-N Analysis:** [Single-case research methods](https://www.taylorfrancis.com/books/mono/10.4324/9780203180938/single-case-research-methods-john-creswell)
- **Effect Sizes:** [Cliff's Delta interpretation](https://en.wikipedia.org/wiki/Cliff%27s_delta)

---

## 🤝 Getting Help

### Technical Support
1. **Check logs:** Look for error messages in console output
2. **Update dependencies:** Ensure all packages are up-to-date
3. **Verify dataset:** Confirm ccmusic data is properly extracted
4. **Test incrementally:** Run components individually before full study

### Community Resources
- **GitHub Issues:** Report bugs and feature requests
- **Discussion Forum:** Share experiences and solutions
- **Documentation Wiki:** Community-contributed guides and tips

### Research Support
- **Statistical consultation:** For analysis questions
- **Cultural consultation:** For Traditional Chinese Music authenticity
- **Ethics guidance:** For research ethics considerations

---

*Last updated: December 2024*
*Version: 1.0*
*Maintainer: TCM Music Therapy Research Team*