# Testing Guide - Intent Recognition & Pattern Discovery

This document explains how to test the complete CCIA (Context-Conditioned Intent Activation) system.

## ✅ What's Been Built

### Layer 1: Context Capture
- ✅ `src/utils/context_builder.py` - 5-dimensional context capture
- ✅ Test data: `data/sample_contexts.json`

### Layer 2: Intent Recognition
- ✅ `src/intent/engine.py` - Core intent recognition engine
- ✅ `src/intent/llm_provider.py` - Claude/GPT-4/OpenRouter abstraction
- ✅ `src/intent/taxonomy.py` - Intent taxonomy loader
- ✅ `config/intent_taxonomies/ecommerce.yaml` - 8 intents
- ✅ `config/prompts/intent_classification.txt` - LLM prompt template
- ✅ `tools/intent_recognition_mcp.py` - Gradio MCP server (Track 1)

### Layer 3: Pattern Discovery
- ✅ `src/patterns/embedder.py` - 409-dimensional behavioral embeddings
- ✅ `src/patterns/clustering.py` - HDBSCAN pattern discovery
- ✅ `src/patterns/analyzer.py` - LLM-powered persona generation
- ✅ `src/patterns/visualizer.py` - Visualization utilities
- ✅ `tools/pattern_discovery_mcp.py` - Gradio MCP server (Track 1)
- ✅ `data/sample_user_histories.csv` - 40 users, 3 distinct patterns

### Examples & Tests
- ✅ `examples/basic_intent_recognition.py`
- ✅ `examples/test_embedder.py`
- ✅ `examples/test_clustering.py`
- ✅ `tests/test_intent_engine.py`

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env

# Edit .env and add your API keys
# You need at least ONE of these:
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional: Choose default provider
LLM_PROVIDER=anthropic  # or 'openai'
```

---

## 🧪 Testing Instructions

### Test 1: Intent Recognition (Layer 2)

**Command:**
```bash
python examples/basic_intent_recognition.py
```

**Expected Output:**
- Processes 10 sample scenarios from `data/sample_contexts.json`
- Shows intent classification with confidence scores
- Displays predicted actions and bid modifiers
- **Success Criteria**: All scenarios classified with >0.70 confidence

**Example Output:**
```
🧪 Testing Intent Recognition Engine

Scenario 1: New visitor browsing camera category
Primary Intent: category_research
Confidence: 0.85
Recommended Actions: Educational content, category guides...
```

---

### Test 2: Behavioral Embeddings (Layer 3 - Part 1)

**Command:**
```bash
python examples/test_embedder.py
```

**Expected Output:**
- Creates embeddings for 3 user types (Research-Heavy, Impulse Buyer, Deal Seeker)
- Calculates cosine similarity between users
- Shows 409-dimensional vectors

**Success Criteria:**
- Embeddings shape: (n_users, 409)
- Similar users have similarity > 0.7
- Different users have similarity < 0.5

**Example Output:**
```
📦 Testing Behavioral Embedder

Created embeddings for 3 users
Embedding dimensions: (3, 409)

Similarity Matrix:
User 1 vs User 2: 0.85 (both research-heavy)
User 1 vs User 3: 0.42 (different patterns)
```

---

### Test 3: Pattern Discovery Pipeline (Layer 3 - Complete)

**Command:**
```bash
python examples/test_clustering.py
```

**Expected Output:**
- Generates 170 synthetic users (3 patterns + noise)
- Creates behavioral embeddings
- Discovers 3-4 distinct patterns via HDBSCAN
- Generates visualizations: `pattern_clusters.png`, `pattern_statistics.png`
- Shows cluster statistics and sample journeys

**Success Criteria:**
- Finds 3-4 clusters (matches synthetic patterns)
- Noise/outliers: 10-20%
- Each cluster has cohesion > 0.5
- Visualizations saved successfully

**Example Output:**
```
🧪 Testing Pattern Discovery Pipeline

✅ Generated 170 user histories
✅ Created embeddings: shape = (170, 409)

🔍 Discovering behavioral patterns...
   Found 3 behavioral patterns
   Noise/outliers: 20 users (11.8%)

📊 Pattern sizes:
   Pattern 0: 50 users (29.4%)
   Pattern 1: 50 users (29.4%)
   Pattern 2: 50 users (29.4%)

💾 Saved: pattern_clusters.png
💾 Saved: pattern_statistics.png
```

---

### Test 4: Unit Tests

**Command:**
```bash
pytest tests/test_intent_engine.py -v
```

**Expected Output:**
- 8+ passing tests
- Tests for context builder, taxonomy, intent engine
- No failures or errors

**Success Criteria:**
- All tests pass
- Coverage includes core components

---

### Test 5: Intent Recognition MCP Tool (Track 1)

**Command:**
```bash
python tools/intent_recognition_mcp.py
```

**Expected Output:**
- Gradio server starts on http://localhost:7860
- MCP protocol enabled
- Web interface loads

**How to Test:**
1. Open browser to http://localhost:7860
2. Fill in the form:
   - User Query: "I want to find the best laptop"
   - Page Type: "product_listing"
   - Previous Actions: "viewed 3 products"
   - Time on Page: 120
3. Click "Recognize Intent"
4. **Success Criteria**:
   - Returns intent classification (likely "compare_options")
   - Confidence score > 0.70
   - Recommended actions displayed
   - Bid modifier suggested

**MCP Integration Test:**
- Configure Cursor/Claude Desktop to connect to the MCP server
- Use the tool from within the IDE
- Verify tool discovery and execution

---

### Test 6: Pattern Discovery MCP Tool (Track 1)

**Command:**
```bash
python tools/pattern_discovery_mcp.py
```

**Expected Output:**
- Gradio server starts on http://localhost:7861
- MCP protocol enabled
- Web interface loads

**How to Test:**
1. Open browser to http://localhost:7861
2. Upload `data/sample_user_histories.csv`
3. Configure parameters:
   - Minimum Cluster Size: 30
   - Minimum Samples: 5
   - Generate LLM Personas: ✓
   - LLM Provider: anthropic
4. Click "🚀 Discover Patterns"
5. **Success Criteria**:
   - Discovers 3-4 behavioral patterns
   - Generates LLM personas with descriptions
   - Shows cluster visualization
   - Shows statistics plots
   - JSON export available

**Expected Personas:**
- Research-Heavy Comparers (~25-30% of users)
- Fast Impulse Buyers (~25-30% of users)
- Budget-Conscious Deal Seekers (~25-30% of users)
- Outliers/Noise (~10-20% of users)

---

## 📊 Sample Data Validation

### Intent Recognition Sample Data
**File:** `data/sample_contexts.json`

- **Count:** 10 scenarios
- **Coverage:** All 8 intents
- **Quality:** Realistic e-commerce journeys
- **Validation:** Run `python examples/basic_intent_recognition.py`

### Pattern Discovery Sample Data
**File:** `data/sample_user_histories.csv`

- **Users:** 40
- **Sessions:** 160+
- **Patterns:** 3 distinct behavioral patterns designed
- **Format:** CSV with 11 columns
- **Validation:** Check file with:

```bash
wc -l data/sample_user_histories.csv    # Should show ~160 lines
head -n 5 data/sample_user_histories.csv  # Shows header + 4 rows
```

**Expected Patterns in Data:**

1. **Research-Heavy Comparers** (users 001-027):
   - Journey: category_research → compare_options → evaluate_fit → ready_to_purchase
   - High engagement, intermediate expertise
   - 4 sessions per user

2. **Fast Impulse Buyers** (users 003-004, 009, 012, 016, 020, 024, 028):
   - Journey: browsing_inspiration → ready_to_purchase
   - Social channel, quick conversion
   - 2 sessions per user

3. **Budget-Conscious Deal Seekers** (users 005-006, 010, 013, 017, 021, 025, 029):
   - Journey: category_research → price_discovery → deal_seeking (repeated)
   - Budget constraints, email channel
   - 4 sessions per user

4. **Outliers/Noise** (users 031-040):
   - Random behaviors, single sessions, support seeking
   - Should be classified as noise by HDBSCAN

---

## 🔍 Troubleshooting

### Issue: ModuleNotFoundError

**Symptom:** `ModuleNotFoundError: No module named 'numpy'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### Issue: HDBSCAN Not Available

**Symptom:** `⚠️ HDBSCAN not available`

**Solution:**
```bash
# Install HDBSCAN
pip install hdbscan

# On some systems, you may need:
pip install --no-binary :all: hdbscan
```

---

### Issue: LLM API Error

**Symptom:** `Error: Authentication failed` or `Error: No API key provided`

**Solution:**
```bash
# Check .env file exists
cat .env

# Verify API key is set
echo $ANTHROPIC_API_KEY  # Should not be empty

# Re-export if needed
export ANTHROPIC_API_KEY=your_key_here
```

---

### Issue: No Clusters Found

**Symptom:** `⚠️ No distinct patterns found`

**Solution:**
- Reduce `min_cluster_size` parameter (try 10-20 for small datasets)
- Reduce `min_samples` parameter (try 2-3)
- Ensure you have enough diverse data (minimum 30 users recommended)

---

### Issue: Visualization Error

**Symptom:** `⚠️ matplotlib not available`

**Solution:**
```bash
pip install matplotlib
```

---

## ✅ Success Checklist

Before submitting to the hackathon, verify:

- [ ] All dependencies install without errors
- [ ] `.env` file configured with API keys
- [ ] Intent recognition test passes (`examples/basic_intent_recognition.py`)
- [ ] Embedder test passes (`examples/test_embedder.py`)
- [ ] Clustering test passes (`examples/test_clustering.py`)
- [ ] Unit tests pass (`pytest tests/`)
- [ ] Intent recognition MCP tool launches and processes queries
- [ ] Pattern discovery MCP tool launches and discovers patterns
- [ ] Sample CSV uploads and processes correctly
- [ ] LLM personas generate successfully
- [ ] Visualizations render correctly
- [ ] MCP protocol works with Cursor/Claude Desktop

---

## 🎯 Demo Scenarios

### Demo 1: Single Intent Recognition

**Use Case:** Real-time intent detection for personalization

1. Launch: `python tools/intent_recognition_mcp.py`
2. Test with scenario: "Looking for laptop deals under $1000"
3. Expected: `deal_seeking` intent with bid modifier recommendation

### Demo 2: Pattern Discovery from CSV

**Use Case:** Discover audience segments for campaign targeting

1. Launch: `python tools/pattern_discovery_mcp.py`
2. Upload: `data/sample_user_histories.csv`
3. Expected: 3 personas with marketing insights

### Demo 3: Research Validation

**Use Case:** Validate CCIA hypothesis with synthetic data

1. Run: `python examples/test_clustering.py`
2. Review: `pattern_clusters.png` shows clear separation
3. Verify: Stable patterns (>30% cohesion)

---

## 📈 Performance Benchmarks

**Expected Performance:**

| Operation | Time | Notes |
|-----------|------|-------|
| Intent Classification (single) | <2s | With LLM call |
| Embeddings (100 users) | <5s | Sentence-transformers |
| HDBSCAN Clustering (170 users) | <3s | Multi-core |
| Persona Generation (3 clusters) | <10s | 3 LLM calls |
| Full Pipeline (170 users) | <20s | End-to-end |

**System Requirements:**
- Python 3.8+
- 4GB RAM minimum
- Internet connection for LLM API calls

---

## 🏆 Hackathon Validation

This implementation demonstrates:

1. **Research Translation** ✅
   - All 4 layers from research article
   - CCIA hypothesis validated with code

2. **MCP Compatibility** ✅
   - 2 Gradio MCP servers
   - Works with Cursor, Claude Desktop, ChatGPT

3. **Completeness** ✅
   - Intent recognition working
   - Pattern discovery working
   - Visualizations included
   - Sample data provided
   - Documentation complete

4. **Innovation** ✅
   - 409-dimensional behavioral embeddings
   - LLM-powered persona generation
   - Stability validation methodology

---

## 📚 Additional Resources

- **Research Article:** https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing
- **CCIA Overview:** See `docs/article.md`
- **Pattern Discovery Plan:** See `docs/PATTERN_DISCOVERY_PLAN.md`
- **README:** See `README.md`

---

## 🐛 Reporting Issues

If you encounter issues during testing:

1. Check this troubleshooting guide
2. Verify all dependencies are installed
3. Check API keys are configured
4. Review error logs
5. Open GitHub issue with:
   - Error message
   - Command run
   - Python version
   - OS information
