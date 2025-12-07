---
title: "Deep Dive Intent Recognition Agent"
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: "5.50.0"
app_file: app.py
pinned: false
license: apache-2.0
python_version: "3.10"
tags:
  - marketing
  - intent-recognition
  - mcp
  - gradio
---

# Context-Conditioned Intent Recognition for Digital Marketing

## Research Implementation & Hackathon Validation

[![HF MCP Hackathon](https://img.shields.io/badge/HF_MCP-Hackathon-orange)](https://huggingface.co/MCP-1st-Birthday)
[![Deep Dive Article](https://img.shields.io/badge/Research-Paper-blue)](https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing)


> **Translating research into production:** This repository implements the **Context-Conditioned Intent Activation (CCIA)** hypothesis from our article "[The Geometry of Intention: How LLMs Recognize Human Goals in Marketing](https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing)". We're validating the approach through the HuggingFace MCP Hackathon to gather real-world feedback and demonstrate practical applications.

---

## 🎯 Overview

Traditional marketing analytics tells you **WHAT** users did. This system tells you **WHY** they did it.

**Core Hypothesis**: LLMs can reliably predict human intention when the prompt supplies enough structured situational context to activate the submanifolds of the model's latent space that encode human social-goal patterns.

**In Practice**: Give an LLM rich behavioral context (not just "user visited page" but "marathon runner researching injury prevention, comparing 3 products, spending 4 minutes on reviews"), and it can recognize intent with surgical precision.

### Research Foundation

This implementation is based on convergent findings from four scientific disciplines:

1. **Evolutionary Biology**: Goal-directed behavior emerges under adaptive pressures (fitness-relevant goals recur in human behavior)
2. **Neuroscience**: Intention is future-directed planning built on memory and scene construction (prefrontal cortex patterns)
3. **Philosophy**: Intention involves commitment and consistency (organizing sub-actions around goals)
4. **Physics (Free Energy Principle)**: Self-maintaining systems act to minimize surprise (goal-pursuit in viable states)

**Key Research References**:
- ACL 2024: Persuasive dialogue intention recognition
- Nature 2024 & PNAS 2024: LLM theory-of-mind capabilities
- Scientific Reports 2025: LLM + knowledge graphs for intention recognition

**Full Article**: [The Geometry of Intention](https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing)

---

## 🏆 Hackathon Strategy

### Why This Approach?

We're using the **Gradio x Anthropic MCP Hackathon** as a validation mechanism:

1. **Rapid User Testing**: Deploy to HuggingFace Spaces → Get real feedback from marketing teams
2. **Technical Validation**: Prove MCP protocol works across platforms (Cursor, Claude Desktop, ChatGPT)
3. **Community Feedback**: Iterate based on actual usage patterns
4. **Production Pathway**: Simplified architecture for hackathon → Full enterprise system post-validation

### Dual Track Submission

**Track 1: Building MCP (Enterprise)**
- ✅ Standalone intent recognition tool
- ✅ Pattern discovery tool
- Bid optimization tool (planned)

**Track 2: MCP in Action (Enterprise)**
- Full marketing intelligence agent
- Autonomous campaign analysis
- Multi-tool orchestration

### Post-Hackathon Roadmap

**Phase 1: OpenAI Apps SDK Integration** 
- Same MCP foundation → Works in ChatGPT
- Reach 800M+ weekly ChatGPT users
- Widget-based visualizations
- OAuth authentication for production

**Phase 2: Enterprise Production** 
- PostgreSQL + Redis (replace SQLite + in-memory)
- Kubernetes deployment
- Multi-channel context capture
- Real-time audience activation

**Phase 3: Research Publication** 
- Publish findings from real-world deployment
- Share anonymized performance metrics
- Open-source refined methodology

---

## 🏗️ Architecture

### The Four-Layer System

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: CONTEXT CAPTURE                                   │
│  Gather rich behavioral signals across 5 dimensions         │
│  • Identity: Who are they?                                  │
│  • History: What have they done?                            │
│  • Situation: Where are they?                               │
│  • Behavioral: What are they doing?                         │
│  • Temporal: When are they acting?                          │
│  • Constraints: What limits their choices?                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: INTENT RECOGNITION                                │
│  LLM infers "what does this person want?"                   │
│  • Structured prompt with full context                      │
│  • Intent taxonomy (8 intents for ecommerce)                │
│  • Confidence calibration                                   │
│  • Behavioral evidence extraction                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: PATTERN DISCOVERY                                 │
│  Find clusters of similar behavioral patterns               │
│  • Behavioral embeddings (sentence-transformers)            │
│  • HDBSCAN clustering                                       │
│  • Persona generation (LLM-based)                           │
│  • Temporal stability validation                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: ACTIVATION                                        │
│  Turn insights into marketing actions                       │
│  • Intent-aware bid modifiers                               │
│  • Audience segmentation                                    │
│  • Content personalization                                  │
│  • Next-best-action predictions                             │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Hackathon Version** (Current):
- **Gradio 6+**: UI + MCP server
- **Claude Sonnet 4**: Intent classification (using Anthropic hackathon credits)
- **SQLite**: Simplified storage
- **In-memory cache**: Response caching
- **HuggingFace Spaces**: Free deployment

**Production Version** (Post-Hackathon):
- **FastAPI**: Production API
- **PostgreSQL + Redis**: Scalable storage + caching
- **Kubernetes**: Container orchestration
- **BigQuery**: Data warehouse
- **Ad Platform APIs**: Real-time activation

---

## 🚀 Quick Start

### Option 1: Try the Live Demo (Fastest)

Visit our deployed HuggingFace Space:
- **Unified Agent**: https://huggingface.co/spaces/Dessi/gradio-mcp-hack
  - Includes both intent recognition + pattern discovery tabs
  - “LLM Settings” accordion lets you paste your own Anthropic/OpenAI/OpenRouter key (stored only in your browser session)

### Option 2: Run Locally (5 minutes)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/intent-recognition-agent
cd intent-recognition-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Choose one provider section to populate:
#   - ANTHROPIC_API_KEY (+ optional ANTHROPIC_MODEL)
#   - OPENAI_API_KEY (+ optional OPENAI_MODEL)
#   - OPENROUTER_API_KEY + OPENROUTER_MODEL (e.g., x-ai/grok-4.1-fast) plus optional OPENROUTER_SITE_URL/NAME

# Run the Intent Recognition MCP tool
python tools/intent_recognition_mcp.py
# Open browser to http://localhost:7860

# OR run the Pattern Discovery MCP tool
python tools/pattern_discovery_mcp.py
# Open browser to http://localhost:7861

# OR run the Bid Optimizer MCP tool
python tools/bid_optimizer_mcp.py
# Open browser to http://localhost:7862

# Optional: configure Google Ads audience exports
cp config/activation/audiences.yaml config/activation/audiences.local.yaml
# Fill in developer_token, login_customer_id, customer_id, client/OAuth creds, then run
```

### Option 3: Use as MCP Server

**With Cursor:**
```json
// Add to your Cursor MCP config
{
  "mcpServers": {
    "marketing-intent": {
      "url": "http://localhost:7860/gradio_api/mcp/sse"
    }
  }
}
```

**With Claude Desktop:**
```json
// Add to claude_desktop_config.json
{
  "mcpServers": {
    "marketing-intent": {
      "command": "python",
      "args": ["tools/intent_recognition_mcp.py"]
    }
  }
}
```

**With ChatGPT** (via OpenAI Apps SDK - Post-Hackathon):
```json
{
  "mcpServers": {
    "marketing-intent": {
      "url": "https://YOUR-SPACE.hf.space/gradio_api/mcp/sse"
    }
  }
}
```

---

## 🧭 User Manual

### Launching the App
```bash
python app.py
```
The Gradio UI runs on http://localhost:7860 and also exposes an MCP endpoint at /gradio_api/mcp/sse.

### Tab 1 — Intent Analyzer
- Fill in user query, page type, prior actions, and dwell time. Advanced controls let you override device, traffic source, scroll depth, and click count.
- Use the sample dropdown to load scenarios from data/sample_contexts.json.
- Click **Analyze Intent** to receive JSON plus a concise markdown summary (primary intent, confidence, bid modifier, conversion probability, recommended actions).
- Provider selection is automatic based on your .env: Claude/OpenAI if those keys exist, otherwise OpenRouter (e.g., Grok 4.1 Fast).


### Tab 2 — Pattern Discovery
- Upload session data as JSON or CSV (one record per session) and/or toggle "Include sample sessions". Fields like user_query, page_type, previous_actions, time_on_page are automatically normalized.
- Adjust the cluster slider to suggest how many personas you want to explore.
- The app returns a cluster summary dataframe, persona JSON (ready for downstream use), and a human-readable markdown recap.

### Tab 3 — MCP & API Guide
- Shows the local MCP URL, configuration snippets for Cursor/Claude Desktop/ChatGPT, and deployment notes for Hugging Face Spaces + OpenRouter leaderboard headers.

Use the app to iterate quickly on prompt changes, demonstrate behavioral personas to stakeholders, or export personas for campaign planning.

### Tab 4 — Bid Optimizer & Audience Activation
- The **Bid Optimizer** tab lets you simulate Layer 4 recommendations by either inferring intent via the engine or overriding it manually. Outputs include JSON for downstream APIs plus a markdown summary for stakeholders.
- Google Ads audience exports use `config/activation/audiences.yaml`. Leave `dry_run: true` to preview hashed payloads locally; set it to `false` (and install the `google-ads` SDK) when you're ready to sync live Customer Match lists.
- The `AudienceManager` orchestrates connectors (starting with Google Ads) so future channels (Meta, LinkedIn, Trade Desk) can be plugged in without changing the UI workflow.

---


## 📊 Intent Taxonomy

Based on behavioral science research, we define 8 core intents across the customer journey:

### Awareness Stage
- **browsing_inspiration**: Exploring with no specific goal (5% conversion likelihood)
- **category_research**: Learning about product types (12% conversion likelihood)

### Consideration Stage
- **compare_options**: Evaluating specific alternatives (35% conversion likelihood)
- **price_discovery**: Understanding cost ranges (22% conversion likelihood)
- **evaluate_fit**: Assessing product-problem fit (48% conversion likelihood)

### Decision Stage
- **ready_to_purchase**: High buying intent (72% conversion likelihood)
- **deal_seeking**: Waiting for promotions (38% conversion likelihood)
- **gift_shopping**: Purchasing for others (55% conversion likelihood)

Each intent includes:
- Typical behavioral signals
- Confidence modifiers
- Recommended marketing actions
- Bid adjustment suggestions
- Transition probabilities to other intents

**Configuration**: See [config/intent_taxonomies/ecommerce.yaml](config/intent_taxonomies/ecommerce.yaml)

---

## 🔬 Research-Backed Design Decisions

### 1. Context is the Master Key

**Research Finding** (ACL 2024): LLM intention recognition accuracy dropped 40% when conversation history was removed.

**Our Implementation**: Five-dimensional context capture
- ✅ Identity context (role, user type)
- ✅ Historical context (past actions, searches)
- ✅ Situational context (device, channel, location)
- ✅ Behavioral signals (engagement, action patterns)
- ✅ Temporal signals (time of day, recency)
- ✅ Constraint signals (budget, urgency, knowledge level)

**Code**: [src/utils/context_builder.py](src/utils/context_builder.py)

### 2. Structured Prompts Activate Latent Knowledge

**Research Finding** (Nature 2024, PNAS 2024): LLM theory-of-mind performance depends entirely on task framing.

**Our Implementation**: Structured prompt template that:
- Presents full behavioral context narratively
- Provides explicit intent taxonomy
- Asks for step-by-step reasoning
- Requires evidence-based justification
- Requests confidence calibration

**Code**: [config/prompts/intent_classification.txt](config/prompts/intent_classification.txt)

### 3. Confidence Calibration Matters

**Research Finding** (Scientific Reports 2025): LLM + knowledge graphs improved accuracy by 35%.

**Our Implementation**: Multi-factor confidence adjustment
- Base LLM confidence score
- Signal strength modifiers (add-to-cart: +0.10, high engagement: +0.05)
- Context quality adjustments
- Historical accuracy tracking (planned for production)

**Code**: [src/intent/engine.py:236](src/intent/engine.py#L236) - `_calibrate_confidence()`

### 4. Behavioral Patterns Over Demographics

**Research Foundation**: Evolutionary biology shows goal-directed behavior is universal but context-dependent.

**Our Implementation**: Pattern discovery through behavioral embeddings
- ✅ 409-dimensional behavioral vectors (semantic + behavioral + temporal + constraints)
- ✅ HDBSCAN clustering for automatic pattern discovery
- ✅ LLM-powered persona generation from clusters
- ✅ Temporal stability validation (>30% overlap = stable patterns)

**Code**: [src/patterns/embedder.py](src/patterns/embedder.py), [src/patterns/clustering.py](src/patterns/clustering.py), [src/patterns/analyzer.py](src/patterns/analyzer.py)

### 5. Modular Architecture for Scientific Iteration

**Research Principle**: Separate hypothesis testing from infrastructure.

**Our Implementation**:
- Each layer can be tested independently
- Swap LLM providers without changing logic
- Replace storage backend without touching algorithms
- A/B test different taxonomies easily

**Result**: We can iterate on the science without touching deployment.

---

## 📂 Repository Structure

```
intent-recognition-agent/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── .gitignore
├── TESTING.md                         # Comprehensive testing guide
│
├── src/                               # Core implementation
│   ├── intent/                        # Layer 2: Intent Recognition
│   │   ├── engine.py                  # Main recognition engine
│   │   ├── taxonomy.py                # Intent taxonomy loader
│   │   └── llm_provider.py            # LLM abstraction (Claude/GPT-4)
│   │
│   ├── patterns/                      # Layer 3: Pattern Discovery ✅
│   │   ├── embedder.py                # Behavioral embeddings (409D vectors)
│   │   ├── clustering.py              # HDBSCAN clustering
│   │   ├── analyzer.py                # LLM persona generation
│   │   └── visualizer.py              # Cluster visualizations
│   │
│   ├── activation/                    # Layer 4: Marketing Activation
│   │   ├── bidding/                   # Bid optimizer + conversion model ✅
│   │   ├── audiences/                 # Audience activation (Google Ads ✅)
│   │   ├── personalization/           # Personalization hooks (planned)
│   │   └── creative/                  # Creative guidance (planned)
│   │
│   └── utils/                         # Layer 1: Context Capture
│       ├── context_builder.py         # Five-dimensional context
│       └── data_parsers.py            # Data parsing utilities ✅
│
├── tools/                             # MCP Tools (Track 1)
│   ├── intent_recognition_mcp.py      # Intent recognition tool ✅
│   ├── pattern_discovery_mcp.py       # Pattern discovery tool ✅
│   └── bid_optimizer_mcp.py           # Bid optimization ✅
│
├── app.py                             # Full Agent (Track 2 - planned)
│
├── config/                            # Configuration
│   ├── intent_taxonomies/
│   │   ├── ecommerce.yaml             # Ecommerce intents ✅
│   │   ├── b2b_saas.yaml              # B2B SaaS (planned)
│   │   └── financial_services.yaml    # Financial (planned)
│   └── prompts/
│       └── intent_classification.txt  # Intent prompt template ✅
│
├── data/                              # Sample data
│   ├── sample_contexts.json           # Test scenarios ✅
│   └── sample_user_histories.csv      # User session histories ✅
│
├── tests/                             # Test suite
│   ├── test_intent_engine.py          # Engine tests ✅
│   ├── test_pattern_discovery_integration.py # Pattern discovery tests ✅
│   ├── test_bid_optimizer.py          # Bid optimizer tests ✅
│   ├── test_audience_manager.py       # Google Ads connector tests ✅
│   ├── test_context_builder.py        # Context tests (planned)
│   └── test_integration.py            # End-to-end tests (planned)
│
├── examples/                          # Usage examples
│   ├── basic_intent_recognition.py    # Intent recognition ✅
│   ├── test_embedder.py               # Embeddings test ✅
│   └── test_clustering.py             # Full pipeline test ✅
│
└── docs/                              # Documentation
    ├── article.md                     # Full research article
    ├── hack-feasibility.md            # Hackathon adaptation analysis
    └── openai-apps-integration.md     # OpenAI Apps SDK roadmap
```

**Legend**: ✅ = Implemented | (planned) = Post-hackathon

---

## 🎯 Usage Examples

### Example 1: High-Intent Purchase Recognition

```python
from src.intent.engine import IntentRecognitionEngine
from src.intent.taxonomy import IntentTaxonomy
from src.intent.llm_provider import LLMProviderFactory

# Initialize
llm = LLMProviderFactory.create_from_env()
taxonomy = IntentTaxonomy.from_domain("ecommerce")
engine = IntentRecognitionEngine(llm_provider=llm, taxonomy=taxonomy)

# Analyze behavior
result = engine.recognize_intent(
    user_query="nike pegasus 40 stability features",
    page_type="product_detail",
    previous_actions="searched_marathon_shoes,viewed_3_products,read_reviews,checked_return_policy",
    time_on_page=245,
    session_history='[{"intent": "compare_options"}]'
)

print(f"Intent: {result['primary_intent']}")
# Output: ready_to_purchase

print(f"Confidence: {result['confidence']:.0%}")
# Output: 87%

print(f"Bid Modifier: {result['bid_modifier_suggestion']:+.0%}")
# Output: +75%

print(f"Next Actions: {result['predicted_next_actions']}")
# Output: ["Check shipping options", "Add to cart", "Complete purchase"]
```

### Example 2: Budget-Conscious Comparison

```python
result = engine.recognize_intent(
    user_query="best running shoes under $100",
    page_type="search_results",
    previous_actions="filtered_by_price,sorted_by_price,viewed_2_products",
    time_on_page=120
)

print(f"Intent: {result['primary_intent']}")
# Output: price_discovery

print(f"Marketing Actions: {result['recommended_marketing_actions']}")
# Output: ["Show value messaging", "Display price matching", "Highlight bundle deals"]
```

### Example 3: Gift Shopping Detection

```python
result = engine.recognize_intent(
    user_query="popular gifts for runners",
    page_type="category",
    previous_actions="viewed_gift_guide,clicked_best_sellers,viewed_gift_wrap_options",
    time_on_page=90
)

print(f"Intent: {result['primary_intent']}")
# Output: gift_shopping

print(f"Conversion Probability: {result['conversion_probability']:.0%}")
# Output: 55%
```

### Example 4: Pattern Discovery & Audience Segmentation

```python
from src.patterns.embedder import BehavioralEmbedder
from src.patterns.clustering import PatternClusterer
from src.patterns.analyzer import PatternAnalyzer
import pandas as pd

# Load user session histories from CSV
df = pd.read_csv('data/sample_user_histories.csv')

# Group sessions by user_id
user_histories = []
for user_id in df['user_id'].unique():
    user_sessions = df[df['user_id'] == user_id].to_dict('records')
    user_histories.append(user_sessions)

# Step 1: Create behavioral embeddings (409-dimensional vectors)
embedder = BehavioralEmbedder()
embeddings = embedder.create_batch_embeddings(user_histories)
# Shape: (n_users, 409)

# Step 2: Discover behavioral patterns with HDBSCAN
clusterer = PatternClusterer(min_cluster_size=30, min_samples=5)
cluster_labels, viz_coords = clusterer.discover_patterns(embeddings)
# Output: Found 3 behavioral patterns

# Step 3: Generate LLM-powered personas
analyzer = PatternAnalyzer()
personas = analyzer.analyze_all_clusters(cluster_labels, user_histories)

# View discovered personas
for persona in personas:
    print(f"\n{persona['persona_name']}")
    print(f"Size: {persona['cluster_size']} users ({persona['percentage']:.1f}%)")
    print(f"Description: {persona['description']}")
    print(f"Recommended bid modifier: {persona['recommended_bid_modifier']:+.0%}")

# Output example:
# Research-Driven Comparers
# Size: 50 users (29.4%)
# Description: Methodical users who thoroughly evaluate options...
# Recommended bid modifier: +25%
```

**Use Case**: Upload CSV of user histories → Discover 3-5 behavioral patterns → Get marketing personas → Export for ad platform targeting

**Try it**: `python tools/pattern_discovery_mcp.py` then upload `data/sample_user_histories.csv`

---

## 🧪 Testing & Validation

### Run Tests Locally

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_intent_engine.py::TestIntentRecognitionEngine -v
```

### Test with Sample Data

```bash
# Test intent recognition with 10 pre-built scenarios
python examples/basic_intent_recognition.py

# Test behavioral embeddings
python examples/test_embedder.py

# Test full pattern discovery pipeline (requires dependencies installed)
python examples/test_clustering.py
```

For comprehensive testing instructions, see [TESTING.md](TESTING.md)

### Expected Results

**Intent Recognition:**
- **60-65% accuracy** with minimal context (page + 1-2 signals)
- **70-75% accuracy** with enhanced context (history + query analysis)
- **75-82% accuracy** with rich context (all five dimensions)
- Research Comparison: ACL 2024 study showed 68% accuracy for persuasive intent

**Pattern Discovery:**
- 3-5 distinct behavioral patterns from 100+ users
- >30% cluster cohesion (stable patterns)
- 10-20% noise/outliers (users who don't fit patterns)
- LLM personas match cluster statistics

---

## 🔄 From Research to Production

### Design Philosophy

**Research Implementation**: Prove the hypothesis works
**Hackathon Validation**: Get real user feedback quickly
**Production Deployment**: Scale with confidence

### Key Simplifications for Hackathon

| Component | Research/Production | Hackathon | Why |
|-----------|-------------------|-----------|-----|
| **Database** | PostgreSQL | SQLite | No server setup needed |
| **Caching** | Redis | In-memory dict | Simpler deployment |
| **API** | FastAPI | Gradio | Built-in MCP support |
| **Auth** | OAuth2 | Optional basic | Focus on functionality |
| **Storage** | S3 + BigQuery | Local files | No cloud costs |
| **Deployment** | Kubernetes | HF Spaces | One-click deploy |

### What We Keep (100% Research Functionality)

**Layer 1 & 2 (Intent Recognition):**
- ✅ All intent recognition logic
- ✅ Five-dimensional context capture
- ✅ LLM integration (Claude/GPT-4)
- ✅ Confidence calibration
- ✅ Intent taxonomy system
- ✅ Marketing recommendations

**Layer 3 (Pattern Discovery):**
- ✅ 409-dimensional behavioral embeddings
- ✅ HDBSCAN clustering algorithm
- ✅ LLM-powered persona generation
- ✅ Stability validation methodology
- ✅ Visualization and export capabilities

---

## 🌐 OpenAI Apps SDK Integration

### Why This Matters

The same MCP foundation that powers our hackathon submission will work in **ChatGPT** via OpenAI Apps SDK, reaching **700M+ weekly users**.

### Timeline

* HuggingFace MCP Hackathon
- Validate core functionality
- Gather user feedback
- Prove technical feasibility

* OpenAI Apps SDK Integration
- Add widget-based visualizations
- Implement OAuth authentication
- Submit to OpenAI App Store

* Public Launch
- Available in ChatGPT conversations
- Monetization via Agentic Commerce Protocol
- Enterprise tier with advanced features

### Technical Compatibility

**What Works Today** (No changes needed):
- ✅ MCP server (Gradio provides this)
- ✅ Tool registration
- ✅ JSON responses
- ✅ SSE transport

**What We'll Add** (Post-hackathon):
- Widget rendering (HTML/JS visualizations)
- Enhanced metadata (`_meta.openai/outputTemplate`)
- OAuth 2.1 for production
- Usage analytics

---

## 🏅 Hackathon Submission Details

### Track 1: Building MCP (Enterprise)

**Tag**: `building-mcp-track-enterprise`

**What We're Submitting**:
- ✅ Intent Recognition MCP Server ([tools/intent_recognition_mcp.py](tools/intent_recognition_mcp.py))
- ✅ Pattern Discovery MCP Server ([tools/pattern_discovery_mcp.py](tools/pattern_discovery_mcp.py))
- ✅ Bid Optimizer MCP Server ([tools/bid_optimizer_mcp.py](tools/bid_optimizer_mcp.py))
- Works standalone in Cursor, Claude Desktop, ChatGPT
- Solves real business problem ($500B digital marketing market)
- Complete Layers 2-4 (bid strategy beta) from research article

### Track 2: MCP in Action

**Tag**: `mcp-in-action-track-enterprise`

**What We're Building**:
- Full marketing intelligence agent
- Chat interface for campaign analysis
- Autonomous use of intent recognition + pattern discovery + bid optimization
- Real-time recommendations

---

## 🤝 Contributing

This is both a research project and a hackathon submission. We welcome:

**During Hackathon** (Nov 14-30):
- Bug reports and fixes
- Documentation improvements
- Additional test scenarios
- UX feedback

**Post-Hackathon**:
- Research contributions (new intent taxonomies, validation studies)
- Production features (ad platform integrations, Layer 4 activation)
- Performance optimizations
- Enterprise deployment guides

**How to Contribute**:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📚 Citation

If you use this work in research or production, please cite:

```bibtex
@article{context_conditioned_intent_2025,
  title={The Geometry of Intention: How LLMs Recognize Human Goals in Marketing},
  author={Performics Labs},
  journal={AI News Hub},
  year={2025},
  url={https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing}
}
```

---

## 🔗 Links

- **Research Article**: [The Geometry of Intention](https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing)
- **HuggingFace Space**: [Coming Soon]
- **Demo Video**: [Coming Soon]
- **GitHub Repository**: [GitHub URL](https://github.com/ai-knowledge-hub/deep-dive-analysis-intent-recognition-agent)
- **Hackathon**: [HF MCP Hackathon](https://huggingface.co/MCP-1st-Birthday)

---

**Questions about the research?** Open a [Discussion](https://github.com/orgs/ai-knowledge-hub/discussions)

**Found a bug?** Open an [Issue](https://github.com/ai-knowledge-hub/deep-dive-analysis-intent-recognition-agent/issues)

**Want to collaborate?** Reach out via email or LinkedIn

---

## 🙏 Acknowledgments

**Research Foundations**:
- ACL 2024 workshop on persuasive dialogue systems
- Nature 2024 & PNAS 2024 studies on LLM theory-of-mind
- Scientific Reports 2025 on LLM intention recognition
- Free Energy Principle research (Friston et al.)
---

<div align="center">

**Built with ❤️ for the marketing community**

*Translating research into tools that actually work*

[⭐ Star on GitHub](https://github.com/YOUR_USERNAME/intent-recognition-agent) | [📖 Read the Research](https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing) | [🎥 Watch Demo](Coming Soon)

</div>
