# Quick Start Testing Guide

## 🚀 **Where to Start Testing**

Follow these steps in order to test the Traditional Chinese Music Therapy application:

### **Step 1: Environment Setup (5 minutes)**

```bash
# 1. Create project directory
mkdir tcm_music_therapy
cd tcm_music_therapy

# 2. Create virtual environment
python -m venv tcm_env
source tcm_env/bin/activate  # Linux/Mac
# tcm_env\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### **Step 2: Run System Test (2 minutes)**

```bash
# Run comprehensive system check
python test_installation.py
```

**Expected output:** All tests should pass ✅

If tests fail, fix issues before proceeding:
- Install missing packages: `pip install <package_name>`
- Check Python version (need 3.8+)
- Verify file structure

### **Step 3: Test Core Components (5 minutes)**

#### **A. Test Data Loading**
```bash
python -c "
from tcm_recommender import CCMusicDatasetLoader
loader = CCMusicDatasetLoader('data/ccmusic-database-demo')
df = loader.load_dataset()
print(f'✅ Loaded {len(df)} tracks')
"
```

#### **B. Test Recommendation Engine**
```bash
python -c "
from tcm_recommender import CCMusicDatasetLoader, TCMRecommendationEngine
loader = CCMusicDatasetLoader('data/ccmusic-database-demo')
df = loader.load_dataset()
engine = TCMRecommendationEngine(df)
recs = engine.recommend_tracks({'era': '1950s', 'mood': 'nostalgic'}, 3)
print(f'✅ Generated {len(recs)} recommendations')
for i, track in enumerate(recs, 1):
    print(f'  {i}. {track[\"title\"]} (Score: {track.get(\"final_score\", 0):.3f})')
"
```

#### **C. Test Analysis Tools**
```bash
python -c "
from analysis_tools import SmallNAnalyzer
import pandas as pd, numpy as np
data = pd.DataFrame({
    'participant_id': ['P001']*4, 'session_id': ['S1']*4,
    'condition_type': ['original', 'generated']*2,
    'engagement_score': [7,8,6,9], 'mood_response_score': [6,7,5,8],
    'agitation_score': [2,3,4,2], 'era': ['1950s']*4, 'mood': ['nostalgic']*4
})
analyzer = SmallNAnalyzer(data)
effects = analyzer.calculate_effect_sizes()
print(f'✅ Analysis tools working ({len(effects)} effect sizes calculated)')
"
```

### **Step 4: Test Session Interface (3 minutes)**

```bash
# Launch Streamlit app
streamlit run session_runner.py
```

**What to test:**
1. **Navigate to:** http://localhost:8501
2. **Enter participant ID:** `test_participant_001`
3. **Start new session** with 4 tracks
4. **Rate a few tracks** with sample scores
5. **Check session summary** appears
6. **Verify data saved** in `data/session_data/session_log.csv`

### **Step 5: Test AI Music Generation (Optional - 10 minutes)**

⚠️ **Note:** This requires significant RAM/GPU and downloads ~1.5GB model

```bash
python -c "
from musicgen_generator import TCMMusicGenerator, GenerationConfig
config = GenerationConfig(model_name='facebook/musicgen-small', max_new_tokens=128)
generator = TCMMusicGenerator(config)
print('✅ MusicGen model loaded successfully')

# Test generation
metadata = {
    'track_id': 'test_001', 'title': 'Test Track',
    'instruments': ['erhu'], 'era': '1950s', 'mood': 'nostalgic', 'tempo': 'slow'
}
variations = generator.generate_variations(metadata, num_variations=1)
print(f'✅ Generated {len(variations)} variations')
"
```

### **Step 6: End-to-End Test (5 minutes)**

```bash
# Run complete workflow test
python -c "
# 1. Load data
from tcm_recommender import CCMusicDatasetLoader, TCMRecommendationEngine
loader = CCMusicDatasetLoader('data/ccmusic-database-demo')
df = loader.load_dataset()

# 2. Get recommendations
engine = TCMRecommendationEngine(df)
tracks = engine.get_balanced_session_tracks({'era': '1950s'}, 4)

# 3. Test session management
from session_runner import SessionManager, create_session_playlist
manager = SessionManager('data/test_session')
playlist = create_session_playlist(tracks, 4)

# 4. Test analysis
from analysis_tools import SmallNAnalyzer
import pandas as pd, numpy as np
sample_data = pd.DataFrame({
    'participant_id': ['P001']*6, 'session_id': ['S1']*6,
    'condition_type': ['original', 'generated']*3,
    'engagement_score': np.random.randint(1,10,6),
    'mood_response_score': np.random.randint(1,10,6),
    'agitation_score': np.random.randint(1,10,6),
    'era': ['1950s']*6, 'mood': ['nostalgic']*6
})
analyzer = SmallNAnalyzer(sample_data)
report = analyzer.generate_report('test_report.html')

print('🎉 END-TO-END TEST PASSED!')
print(f'  - Loaded {len(df)} tracks')
print(f'  - Generated {len(tracks)} session recommendations')
print(f'  - Created {len(playlist)} track playlist')
print(f'  - Analysis report: {report}')
"
```

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: Module Import Errors**
```bash
# Solution: Ensure you're in the right directory
pwd  # Should show your project directory
ls   # Should show: analysis_tools.py, session_runner.py, etc.
```

### **Issue 2: Missing Dataset**
```bash
# Download CCMusic dataset (optional for basic testing)
mkdir -p data/ccmusic-database-demo
# The app will use sample data if the real dataset isn't available
```

### **Issue 3: Streamlit Won't Start**
```bash
# Clear Streamlit cache
streamlit cache clear

# Try different port
streamlit run session_runner.py --server.port 8502
```

### **Issue 4: CUDA/GPU Errors**
```bash
# Force CPU usage
python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print('Use CPU if CUDA causes issues')
"
```

### **Issue 5: Audio Library Errors**
```bash
# Install audio dependencies
pip install soundfile librosa

# For Linux, may need system packages:
# sudo apt-get install libsndfile1
```

---

## 📊 **Expected Test Results**

### **Successful System Test Output:**
```
🧪 TCM MUSIC THERAPY APPLICATION - SYSTEM TEST
============================================================

🐍 Checking Python version...
✅ Python 3.11.0 - Compatible

📦 Checking required packages...
✅ PyTorch
✅ Transformers
✅ Streamlit
... (all packages)

📋 TEST SUMMARY
============================================================
Python Version           ✅ PASS
Required Packages        ✅ PASS
PyTorch Setup            ✅ PASS
... (all tests)

Overall: 11/11 tests passed

🎉 ALL TESTS PASSED!
```

### **Successful Session Interface:**
- Web interface loads at http://localhost:8501
- Can enter participant ID and start session
- Track information displays correctly
- Scoring sliders work (1-10 scale)
- Session data saves to CSV file
- Session summary shows plots and statistics

### **Successful Analysis Output:**
- Effect sizes calculated (Cliff's Delta, Hedges' g)
- Statistical tests run (Wilcoxon, Mann-Whitney)
- Visualizations generated (Plotly charts)
- HTML report created with findings

---

## 🎯 **Success Criteria**

✅ **Basic Functionality:**
- All system tests pass
- Streamlit app launches without errors
- Can create and run a mock therapy session
- Session data saves correctly

✅ **Core Features:**
- Music recommendation engine works
- Session management interface functional
- Statistical analysis produces results
- Visualizations generate correctly

✅ **Advanced Features (Optional):**
- AI music generation works (if GPU available)
- Real CCMusic dataset loads (if downloaded)
- Full end-to-end workflow completes

---

## 🚀 **Next Steps After Testing**

1. **Recruit Participants:** Family members, community members
2. **Conduct Pilot Sessions:** 2-3 participants, 2-3 sessions each
3. **Collect Data:** Use the Streamlit interface for data collection
4. **Analyze Results:** Use analysis tools to generate reports
5. **Iterate:** Refine based on initial findings

---

**🎉 Ready to revolutionize music therapy research!**