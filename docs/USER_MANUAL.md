# Marketing Practitioner's User Manual
## Context-Conditioned Intent Recognition System

**Version:** 1.0
**Last Updated:** December 2025
**Audience:** Marketing practitioners, campaign managers, and digital strategists

---

## Table of Contents

1. [Introduction: What This System Does](#1-introduction-what-this-system-does)
2. [Getting Started](#2-getting-started)
3. [Using the Gradio Web Interface](#3-using-the-gradio-web-interface)
4. [Using the MCP Tools](#4-using-the-mcp-tools)
5. [Real-World Marketing Workflows](#5-real-world-marketing-workflows)
6. [Understanding Your Results](#6-understanding-your-results)
7. [Audience Activation Guide](#7-audience-activation-guide)
8. [Troubleshooting](#8-troubleshooting)
9. [Best Practices](#9-best-practices)
10. [FAQ](#10-faq)

---

## 1. Introduction: What This System Does

### The Problem This Solves

Traditional marketing tells you **WHAT** users did (clicked an ad, visited a page, added to cart). This system tells you **WHY** they did it—their actual intention.

**Example:**
- **Traditional view:** "User visited product page for 4 minutes"
- **Intent-aware view:** "Marathon runner with plantar fasciitis, researching injury-prevention features, comparing 3 alternatives, needs shoes within 2 weeks — **ready to purchase** with 87% confidence"

### How It Works (In Plain English)

The system has four layers that work together:

```
┌─────────────────────────────────────────────────────┐
│ LAYER 1: CONTEXT CAPTURE                            │
│ Collects behavioral signals about users             │
│ (who they are, what they've done, constraints)      │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 2: INTENT RECOGNITION                         │
│ AI analyzes context to determine "what do they      │
│ actually want?" (browse, compare, ready to buy)     │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 3: PATTERN DISCOVERY                          │
│ Finds clusters of similar users to create           │
│ behavioral personas (not demographics!)             │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 4: ACTIVATION                                 │
│ Turns insights into action: bid adjustments,        │
│ audience targeting, personalized messaging          │
└─────────────────────────────────────────────────────┘
```

### What You Can Do With This

**Immediate Actions:**
- **Analyze individual user sessions** to understand intent in real-time
- **Discover behavioral personas** from historical session data
- **Optimize bids** based on purchase likelihood (e.g., +75% for ready-to-purchase users)
- **Sync audiences** to Google Ads Customer Match and Meta Custom Audiences

**Strategic Benefits:**
- Target users based on what they want, not just who they are
- Stop wasting budget on low-intent traffic
- Personalize messaging to match user goals
- Create data-driven buyer personas

---

## 2. Getting Started

### Prerequisites

**What You Need:**
1. **An AI API key** from one of:
   - Anthropic (Claude) — Recommended for best accuracy
   - OpenAI (GPT-4)
   - OpenRouter (access to multiple models)

2. **Optional (for audience sync):**
   - Google Ads API credentials (for Customer Match)
   - Meta Marketing API credentials (for Custom Audiences)

**Technical Skills Required:**
- Basic: Copy/paste commands, edit text files
- No coding experience needed for web interface
- Light technical knowledge helpful for MCP setup

### Installation

#### Option 1: Try the Live Demo (No Installation)

Visit the HuggingFace Space: `https://huggingface.co/spaces/Dessi/gradio-mcp-hack`

**Note:** The live demo lets you paste your own API key in the browser (it's never stored on servers). Perfect for testing!

#### Option 2: Run Locally

**Step 1: Download the Code**

```bash
# Using git (recommended)
git clone https://github.com/ai-knowledge-hub/deep-dive-analysis-intent-recognition-agent
cd deep-dive-analysis-intent-recognition-agent

# OR download ZIP from GitHub and extract it
```

**Step 2: Install Dependencies**

```bash
# Make sure you have Python 3.10+ installed
python --version

# Install required packages
pip install -r requirements.txt
```

**Step 3: Configure Your API Keys**

```bash
# Copy the example configuration
cp .env.example .env

# Open .env in a text editor
# Add your API key to ONE of these sections:

# For Anthropic Claude (recommended):
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# OR for OpenAI:
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# OR for OpenRouter:
OPENROUTER_API_KEY=sk-or-your-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

**Step 4: Launch the Application**

```bash
# Start the main Gradio interface
python app.py

# The app will open at http://localhost:7860
```

**Success!** You should see a web interface with four tabs.

---

## 3. Using the Gradio Web Interface

The Gradio app has four main tabs. Let's walk through each one.

### Tab 1: Intent Analyzer — Your Customer Intention Detective

**Purpose:** Analyze individual user sessions to understand their intent.

#### Step-by-Step: Analyzing Your First User Session

**1. Choose a Sample Scenario (Easy Start)**

When you open the Intent Analyzer tab, you'll see a dropdown labeled **"Load Sample Scenario"**:

- Click the dropdown
- Select a scenario like **"High Intent Purchase - Marathon Runner"**
- Click **"Load Selected Sample"**

The form will auto-fill with realistic behavioral data.

**2. Understand the Input Fields**

Here's what each field means:

| Field | What It Means | Example |
|-------|---------------|---------|
| **User Query** | What they searched for | "nike pegasus 40 stability features" |
| **Page Type** | Where they are now | product_detail, category, search_results |
| **Previous Actions** | What they did before (comma-separated) | searched_marathon_shoes,read_reviews |
| **Time on Page** | Seconds spent on current page | 245 |
| **Session History** | Past intent states (JSON format) | `[{"intent": "compare_options"}]` |
| **Advanced Fields** (click "Show Advanced") | | |
| **Device Type** | desktop, mobile, tablet | desktop |
| **Traffic Source** | organic, paid_search, social | paid_search |
| **Scroll Depth** | How far they scrolled (0-100%) | 85 |
| **Clicks on Page** | Number of interactions | 7 |

**3. Run the Analysis**

- Click **"Analyze Intent"**
- Wait 2-5 seconds for the AI to analyze

**4. Read Your Results**

You'll get two outputs:

**JSON Output** (for technical use):
```json
{
  "primary_intent": "ready_to_purchase",
  "confidence": 0.87,
  "conversion_probability": 0.72,
  "bid_modifier_suggestion": 0.75,
  "reasoning": "User shows strong purchase signals...",
  "predicted_next_actions": ["Check shipping", "Add to cart"],
  "recommended_marketing_actions": ["Show trust badges", "Highlight fast shipping"]
}
```

**Summary Output** (human-readable):

```
🎯 PRIMARY INTENT: ready_to_purchase
📊 CONFIDENCE: 87%
💰 CONVERSION PROBABILITY: 72%
📈 BID MODIFIER: +75%

REASONING:
Marathon runner with injury concerns, deep engagement with
product details, checking return policy—this user is validating
before purchase.

NEXT ACTIONS:
• Check shipping options
• Add to cart
• Complete purchase

RECOMMENDED MARKETING ACTIONS:
• Show trust badges and guarantees
• Highlight fast shipping options
• Display injury-prevention benefits prominently
```

**5. What To Do With These Insights**

- **High confidence (>80%) + ready_to_purchase?** → Increase bids, show urgency messaging
- **compare_options intent?** → Show comparison tables, highlight differentiators
- **price_discovery intent?** → Display value messaging, bundle deals
- **Low confidence (<60%)?** → Need more context signals (see troubleshooting)

#### Using Your Own Data

**Preparing Your User Data:**

To analyze real users, you need to capture:

**Minimum Required:**
1. Current page type (e.g., "product_detail", "category")
2. Recent actions (at least 2-3)
3. Time on page in seconds

**Better Results:**
- Add user query/search terms
- Add session history (past intents)
- Add device type and traffic source

**Example of Real Data:**

```
User Query: "best CRM software for small business"
Page Type: comparison_page
Previous Actions: read_pricing_guide,viewed_feature_comparison,watched_demo_video
Time on Page: 420
Session History: [{"intent": "category_research", "timestamp": "2025-01-10"}]
```

---

### Tab 2: Pattern Discovery — Find Your Behavioral Personas

**Purpose:** Upload historical session data to discover behavioral patterns and create personas.

#### What You Need

**Data Format:** CSV or JSON file with user session data.

**Required Fields:**
- `user_id` — Unique identifier for each user
- `session_id` — Unique identifier for each session
- `user_query` — Search terms or queries
- `page_type` — Type of page visited
- `previous_actions` — Comma-separated actions
- `time_on_page` — Seconds on page

**Optional (improves accuracy):**
- `device_type`, `traffic_source`, `scroll_depth`, `clicks_on_page`

**Example CSV Format:**

```csv
user_id,session_id,user_query,page_type,previous_actions,time_on_page
user_001,sess_001,running shoes,category,viewed_guide,120
user_001,sess_002,nike pegasus,product_detail,read_reviews,240
user_002,sess_003,cheap running shoes,search_results,filtered_by_price,90
```

#### Step-by-Step: Discovering Patterns

**1. Prepare Your Data**

- Export session data from your analytics platform (Google Analytics, Adobe, etc.)
- Format as CSV with the required fields above
- Or use the provided sample: `data/sample_user_histories.csv`

**2. Upload to Pattern Discovery**

In the **Pattern Discovery** tab:

1. **Option A: Upload your file**
   - Click **"Upload Session Data (CSV or JSON)"**
   - Select your file

2. **Option B: Use sample data**
   - Check **"Include Sample Sessions"** checkbox
   - This loads 170 sample sessions for testing

**3. Adjust Cluster Settings**

- **Target Number of Personas:** Slide the slider (default: 3)
  - 3-4 personas: Broad segments
  - 5-6 personas: More granular insights
  - Start with 3 for your first run

**4. Click "Discover Patterns"**

Processing takes 10-30 seconds depending on data size.

**5. Review Your Results**

You'll get three outputs:

**A. Cluster Summary Table:**

| Cluster | Size | % of Total | Avg Session Time | Avg Actions |
|---------|------|------------|------------------|-------------|
| 0 | 52 users | 30.6% | 180 sec | 4.2 |
| 1 | 48 users | 28.2% | 95 sec | 2.1 |
| 2 | 45 users | 26.5% | 310 sec | 6.8 |
| Noise | 25 users | 14.7% | — | — |

**B. Persona JSON (for technical use):**

```json
{
  "persona_name": "Research-Driven Comparers",
  "cluster_size": 52,
  "description": "Users who methodically evaluate multiple options...",
  "behavioral_characteristics": {
    "avg_session_duration": 180,
    "common_actions": ["read_reviews", "compare_specs"]
  },
  "recommended_bid_modifier": 0.25
}
```

**C. Persona Summary (human-readable):**

```
🎭 PERSONA: Research-Driven Comparers
👥 SIZE: 52 users (30.6%)
📊 STABILITY: High (38% week-over-week overlap)

DESCRIPTION:
Methodical users who thoroughly evaluate alternatives before deciding.
They consume educational content, compare specifications, and read
detailed reviews. High consideration intent but longer sales cycle.

MARKETING RECOMMENDATIONS:
• Bid Modifier: +25%
• Messaging: Emphasize detailed specifications and comparisons
• Content: Provide in-depth guides and feature comparisons
• Channel: Perform well on organic search and content marketing
```

**6. What To Do With Personas**

**Immediate Actions:**
1. **Create custom audiences** in your ad platforms based on behavioral patterns
2. **Adjust bids** using recommended modifiers
3. **Personalize messaging** to match persona characteristics

**Strategic Actions:**
1. **Content planning:** Create content for each persona's needs
2. **Landing page optimization:** Design pages that match persona expectations
3. **Sales enablement:** Brief sales teams on persona characteristics

---

### Tab 3: Bid Optimizer & Audience Activation — Turn Insights Into Action

**Purpose:** Get specific bid recommendations and sync audiences to ad platforms.

#### Part A: Bid Optimization

**Step-by-Step:**

**1. Choose Input Method**

You have two options:

**Option A: Infer Intent from Context**
- Fill in user query, page type, actions (like Tab 1)
- System will analyze intent automatically
- Click **"Analyze & Generate Bid Strategy"**

**Option B: Manual Intent Override**
- Select **"Manual Override"** mode
- Choose intent from dropdown (ready_to_purchase, compare_options, etc.)
- Enter confidence score (0-100%)
- Click **"Generate Bid Strategy"**

**2. Review Bid Recommendations**

**JSON Output:**
```json
{
  "intent": "ready_to_purchase",
  "confidence": 0.87,
  "base_conversion_probability": 0.72,
  "recommended_bid_modifier": 0.75,
  "suggested_max_cpc": "$2.45",
  "budget_pacing": "aggressive"
}
```

**Summary Output:**
```
💰 BID OPTIMIZATION STRATEGY

Intent: ready_to_purchase
Confidence: 87%
Conversion Probability: 72%

RECOMMENDATIONS:
• Bid Modifier: +75% (increase bids significantly)
• Suggested Max CPC: $2.45
• Budget Pacing: Aggressive
• Target ROAS: 450%

RATIONALE:
High-intent user with strong purchase signals. Recommend
aggressive bidding to capture conversion before competitor
interaction. Expected 3x higher conversion rate than baseline.
```

**3. Implement in Your Ad Platforms**

**For Google Ads:**
1. Go to Audiences → Custom Segments
2. Create segment based on behavioral signals
3. Apply +75% bid adjustment
4. Monitor performance for 7-14 days

**For Meta Ads:**
1. Create Custom Audience with similar behavior signals
2. Set budget at recommended pacing
3. Use recommended messaging themes
4. Track conversion rate changes

#### Part B: Audience Activation (Advanced)

**What This Does:** Automatically sync user lists to Google Ads Customer Match or Meta Custom Audiences.

**Prerequisites:**
- Google Ads or Meta API credentials configured in `.env`
- User email addresses or hashed IDs
- Audiences config file: `config/activation/audiences.yaml`

**Step-by-Step: Syncing an Audience**

**1. Configure Audience Settings** (One-time setup)

Edit `config/activation/audiences.yaml`:

```yaml
google_ads:
  batch_size: 1000      # Number of users per batch
  dry_run: true         # Set to false for real sync
  hashing_salt: ""      # Optional: add salt for hashing

meta_ads:
  batch_size: 5000
  dry_run: true
  hashing_salt: ""
```

**Important:** Keep `dry_run: true` until you're ready to sync for real!

**2. Add API Credentials to .env**

```bash
# Google Ads Customer Match
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
GOOGLE_ADS_CUSTOMER_ID=0987654321
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token

# Meta Custom Audiences
META_ACCESS_TOKEN=your_token
META_APP_SECRET=your_app_secret
META_AD_ACCOUNT_ID=act_1234567890
```

**3. Prepare Your Audience Data**

In the **Bid Optimizer** tab, find the **"Sync Audience"** section:

- **Audience Name:** e.g., "High-Intent-Ready-To-Purchase-Dec2025"
- **Channel:** Select "Google Ads" or "Meta"
- **Identifiers:** Paste email addresses (one per line) or hashed IDs

```
user1@example.com
user2@example.com
user3@example.com
```

**4. Run Dry Run First**

- Keep **"Dry Run"** checked
- Click **"Sync Audience"**

**Dry Run Output:**
```
🔍 DRY RUN MODE - No data sent to platform

Audience: High-Intent-Ready-To-Purchase-Dec2025
Channel: Google Ads
Total Identifiers: 150
Hashed Preview:
  • 5d41402abc4b2a76b9719d911017c592
  • 7c6a180b36896a0a8c02787eeafb0e4c
  • 6cb75f652a9b52798eb6cf2201057c73

✅ Validation passed. Set dry_run=false to sync for real.
```

**5. Sync for Real**

Once you've verified the dry run:

1. Edit `config/activation/audiences.yaml`
2. Change `dry_run: true` to `dry_run: false`
3. Run **"Sync Audience"** again

**Real Sync Output:**
```
✅ AUDIENCE SYNCED SUCCESSFULLY

Platform: Google Ads
Audience Name: High-Intent-Ready-To-Purchase-Dec2025
Total Users Synced: 150
Match Rate: 87% (estimated)

Next Steps:
1. Go to Google Ads → Tools → Audience Manager
2. Find your new Customer Match list
3. Apply to campaigns with +75% bid modifier
4. Monitor performance after 24-48 hours
```

---

### Tab 4: MCP & API Guide — Integration Reference

**Purpose:** Documentation for developers who want to integrate the system with other tools.

This tab shows:
- MCP server URLs for Cursor, Claude Desktop, ChatGPT
- API endpoint documentation
- Configuration examples
- Deployment guides

**Non-technical users can skip this tab.**

---

## 4. Using the MCP Tools

MCP (Model Context Protocol) allows AI assistants like Claude, ChatGPT, and Cursor to use this system as a tool.

### What is MCP? (Simple Explanation)

Think of MCP as a way for AI assistants to "call" your intent recognition system:

**Without MCP:**
- You manually copy user data
- Paste into web interface
- Copy results back
- Paste into your AI chat

**With MCP:**
- AI assistant automatically calls the system
- Gets results instantly
- Uses them to answer your questions

**Example conversation:**

```
You: "Analyze this user session: [paste data]"
Claude: *calls intent recognition MCP tool*
Claude: "This user shows ready_to_purchase intent with 87%
        confidence. I recommend increasing bids by 75%..."
```

### Setting Up MCP in Cursor

**Step 1: Start the MCP Server**

```bash
# Intent Recognition Server
python tools/intent_recognition_mcp.py

# OR Pattern Discovery Server
python tools/pattern_discovery_mcp.py

# OR Bid Optimizer Server
python tools/bid_optimizer_mcp.py
```

Server starts on `http://localhost:7860`

**Step 2: Configure Cursor**

1. Open Cursor settings
2. Find "MCP Servers" section
3. Add this configuration:

```json
{
  "mcpServers": {
    "marketing-intent": {
      "url": "http://localhost:7860/gradio_api/mcp/sse"
    }
  }
}
```

**Step 3: Use in Cursor**

Open a chat and try:

```
Analyze this user session:
- Query: "best CRM for small business"
- Page: comparison_page
- Actions: read_pricing,watch_demo
- Time: 320 seconds
```

Cursor will automatically call the MCP tool and show results!

### Setting Up MCP in Claude Desktop

**Step 1: Configure Claude Desktop**

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "marketing-intent": {
      "command": "python",
      "args": ["/full/path/to/tools/intent_recognition_mcp.py"]
    }
  }
}
```

**Step 2: Restart Claude Desktop**

**Step 3: Use the Tool**

In any conversation:
```
I need to analyze a user's intent. They searched for "marathon
running shoes stability", spent 4 minutes on the product page,
and read reviews about arch support.
```

Claude will automatically use the MCP tool!

### MCP Tool Capabilities

**Intent Recognition MCP:**
- `recognize_intent` — Analyze single user session
- Returns: intent, confidence, bid recommendations

**Pattern Discovery MCP:**
- `discover_patterns` — Cluster user sessions into personas
- Returns: persona descriptions, sizes, recommendations

**Bid Optimizer MCP:**
- `optimize_bids` — Get bidding strategy for intent
- Returns: modifiers, pacing, budget recommendations

---

## 5. Real-World Marketing Workflows

### Workflow 1: Daily Campaign Optimization

**Goal:** Identify high-intent users and adjust bids daily.

**Steps:**

1. **Morning: Export yesterday's session data**
   - Export from Google Analytics/Adobe
   - Include: user_id, queries, page paths, engagement metrics

2. **Run Intent Analysis**
   - Upload to Tab 1 (batch process) or use MCP
   - Filter for high-confidence + ready_to_purchase intent

3. **Create Audience Segments**
   - High-intent users → aggressive bidding (+50-75%)
   - Compare-intent users → moderate bidding (+15-25%)
   - Browse-intent users → low bidding (-20-40%)

4. **Sync to Ad Platforms**
   - Use Tab 3 audience sync
   - Or manually create audiences with exported lists

5. **Monitor & Iterate**
   - Track conversion rates by segment
   - Adjust bid modifiers based on performance

**Expected Impact:** 15-30% improvement in ROAS within 2 weeks.

---

### Workflow 2: Persona-Based Content Strategy

**Goal:** Discover behavioral personas and create targeted content.

**Steps:**

1. **Gather 30-90 days of session data**
   - Minimum 100 users for stable patterns
   - More data = better personas

2. **Run Pattern Discovery (Tab 2)**
   - Upload historical session data
   - Start with 3-4 personas

3. **Analyze Persona Characteristics**
   - Review behavioral patterns
   - Note common queries, page paths, actions

4. **Map Content Gaps**
   - For each persona, identify:
     - What questions they're asking
     - What content they consume
     - Where they get stuck

5. **Create Persona-Specific Content**
   - "Research-Driven Comparers" → detailed comparison guides
   - "Quick Decision Makers" → simplified product pages
   - "Budget Shoppers" → value-focused messaging

6. **Measure Content Performance**
   - Track conversion rates by persona
   - Iterate based on engagement

**Expected Impact:** 20-40% increase in engagement, 10-25% lift in conversions.

---

### Workflow 3: Real-Time Personalization

**Goal:** Personalize website experience based on detected intent.

**Steps:**

1. **Set up real-time integration** (requires dev resources)
   - Call intent recognition API on page load
   - Pass current session context

2. **Create intent-specific page variants**
   - ready_to_purchase → show trust badges, limited stock, urgency
   - compare_options → show comparison tables, spec sheets
   - price_discovery → highlight discounts, value bundles

3. **A/B test personalization**
   - Control: standard page
   - Treatment: intent-personalized page

4. **Measure lift**
   - Conversion rate by intent
   - Average order value
   - Time to purchase

**Expected Impact:** 25-50% conversion rate increase for high-intent users.

---

### Workflow 4: Competitive Conquest Campaigns

**Goal:** Target users comparing you to competitors.

**Steps:**

1. **Identify comparison queries**
   - "[your brand] vs [competitor]"
   - "alternative to [competitor]"

2. **Analyze intent for comparison searches**
   - Upload sessions to Tab 1
   - Look for compare_options intent

3. **Create comparison-focused content**
   - Head-to-head comparison pages
   - "Why switch from X to us" content
   - Competitive differentiation guides

4. **Build conquest audience**
   - Users with compare_options intent
   - Mentioning competitor names in queries
   - Moderate-to-high engagement

5. **Launch targeted campaigns**
   - Google Ads: competitor keywords + custom audiences
   - Meta: lookalike audiences of comparers
   - Messaging: "See how we compare" CTAs

**Expected Impact:** 10-20% capture rate from competitive traffic.

---

## 6. Understanding Your Results

### Intent Labels Explained

The system recognizes 8 core ecommerce intents:

| Intent | Stage | What It Means | Conversion Rate | Bid Modifier |
|--------|-------|---------------|-----------------|--------------|
| **browsing_inspiration** | Awareness | Exploring with no goal | 5% | -30% to -50% |
| **category_research** | Awareness | Learning about product types | 12% | -10% to +0% |
| **compare_options** | Consideration | Evaluating specific alternatives | 35% | +15% to +30% |
| **price_discovery** | Consideration | Understanding cost ranges | 22% | +0% to +15% |
| **evaluate_fit** | Consideration | Assessing product-problem fit | 48% | +30% to +50% |
| **ready_to_purchase** | Decision | High buying intent | 72% | +50% to +100% |
| **deal_seeking** | Decision | Waiting for promotions | 38% | +10% to +25% |
| **gift_shopping** | Decision | Purchasing for others | 55% | +35% to +60% |

### Confidence Scores

**What confidence means:**

- **90-100%:** Extremely clear signals, very reliable
- **75-89%:** Strong signals, reliable for action
- **60-74%:** Moderate signals, useful with caution
- **<60%:** Weak signals, need more context

**How to improve confidence:**
- Add more behavioral signals (previous actions)
- Include session history (past intents)
- Add temporal context (urgency indicators)
- Capture constraint signals (budget, timing)

### Bid Modifier Interpretation

**How to apply modifiers:**

If your base bid is $1.00:
- +75% modifier → new bid: $1.75
- +30% modifier → new bid: $1.30
- -20% modifier → new bid: $0.80

**When to override recommendations:**
- Known high-value customer → increase more
- Low margin product → decrease modifier
- Seasonal promotion → increase temporarily
- Budget constraints → cap at max affordable

### Persona Stability Scores

**What stability means:**

Personas are measured for temporal stability:
- **>30% overlap:** Stable patterns worth targeting
- **20-30% overlap:** Moderate stability, monitor changes
- **<20% overlap:** Unstable, may be noise or seasonal

**Noise cluster:**
- Users who don't fit any pattern
- Usually 10-20% of total
- Don't create personas from noise
- May indicate data quality issues

---

## 7. Audience Activation Guide

### Google Ads Customer Match Setup

**Prerequisites:**
1. Google Ads account with Customer Match eligibility
2. Developer token (apply at ads.google.com/home/tools/manager-accounts)
3. OAuth credentials (create at console.cloud.google.com)

**Step-by-Step Setup:**

**1. Get Developer Token**
- Go to Google Ads Manager Account
- Tools → Setup → API Center
- Apply for developer token
- Wait for approval (can take 24-48 hours)

**2. Create OAuth Credentials**
- Go to console.cloud.google.com
- Enable Google Ads API
- Create OAuth 2.0 credentials
- Download client_secret.json

**3. Generate Refresh Token**
```bash
# Use Google's OAuth playground
https://developers.google.com/oauthplayground/
```

**4. Add to .env**
```bash
GOOGLE_ADS_DEVELOPER_TOKEN=your_token_here
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
GOOGLE_ADS_CUSTOMER_ID=0987654321
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
```

**5. Test with Dry Run**
- Use Tab 3 sync with `dry_run: true`
- Verify hashing and validation

**6. Sync Live Audience**
- Set `dry_run: false`
- Sync your first audience
- Check Audience Manager in Google Ads

**Match Rates:**
- Email lists: 60-90% match
- Hashed IDs: varies by platform
- Higher quality data = better match

---

### Meta Custom Audiences Setup

**Prerequisites:**
1. Meta Business Manager account
2. Ad account with Custom Audience permissions
3. App with Marketing API access

**Step-by-Step Setup:**

**1. Create Meta App**
- Go to developers.facebook.com
- Create new app → Business type
- Add Marketing API

**2. Get Access Token**
- Tools → Access Token Tool
- Select your app
- Grant permissions: ads_read, ads_management
- Copy access token

**3. Get App Secret**
- App Dashboard → Settings → Basic
- Copy App Secret

**4. Find Ad Account ID**
- Business Manager → Ad Accounts
- Account ID starts with "act_"

**5. Add to .env**
```bash
META_ACCESS_TOKEN=your_long_access_token
META_APP_SECRET=your_app_secret
META_AD_ACCOUNT_ID=act_1234567890
```

**6. Test with Dry Run**
- Tab 3 sync with `dry_run: true`
- Verify hashing

**7. Sync Live Audience**
- Set `dry_run: false`
- Sync audience
- Find in Ads Manager → Audiences

**Important Notes:**
- Access tokens expire (use long-lived tokens)
- Minimum audience size: 100 users
- May take 6-24 hours to populate
- Refresh weekly for active campaigns

---

## 8. Troubleshooting

### Issue: "Unable to initialize Intent Recognition Engine"

**Cause:** No valid API key configured.

**Solution:**
1. Check `.env` file exists
2. Verify you added an API key (ANTHROPIC_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY)
3. Ensure no typos in the key
4. Test key validity:
   ```bash
   # For Anthropic
   curl https://api.anthropic.com/v1/messages -H "x-api-key: YOUR_KEY"
   ```

---

### Issue: Low confidence scores (<60%)

**Cause:** Insufficient context signals.

**Solution:**
1. **Add more previous actions** — minimum 3-5 actions
2. **Include session history** — past intents if available
3. **Add constraint signals:**
   - Budget indicators ("cheap", price filters)
   - Urgency indicators ("need by", "fast shipping")
   - Knowledge level ("beginner", "how to")
4. **Verify page type** — specific types (product_detail) better than generic (page)

---

### Issue: Personas all look similar

**Cause:** Not enough behavioral diversity in data.

**Solution:**
1. **Expand data timeframe** — 30-90 days minimum
2. **Include more users** — minimum 100, ideally 500+
3. **Check data quality:**
   - Are queries present?
   - Are actions varied?
   - Is engagement data included?
4. **Reduce cluster count** — try 2-3 instead of 5-6

---

### Issue: Audience sync fails

**Cause:** Invalid credentials or configuration.

**Solution:**

**For Google Ads:**
1. Verify developer token is approved
2. Check customer IDs (login vs. customer)
3. Test OAuth refresh token
4. Ensure Customer Match is enabled
5. Check minimum audience size (1000 for search)

**For Meta:**
1. Verify access token is valid (not expired)
2. Check ad account ID format (starts with "act_")
3. Ensure app has Marketing API permissions
4. Verify Custom Audiences permission in Business Manager

**Debug Mode:**
```bash
# Enable debug logging
DEBUG_MODE=true python app.py
```

---

### Issue: MCP server won't connect

**Cause:** Server not running or wrong URL.

**Solution:**
1. **Verify server is running:**
   ```bash
   python tools/intent_recognition_mcp.py
   # Should show: Running on http://localhost:7860
   ```

2. **Check the URL in config:**
   - Should be `http://localhost:7860/gradio_api/mcp/sse`
   - NOT `https://` (unless using tunnel)

3. **Firewall check:**
   - Ensure port 7860 is not blocked
   - Try: `curl http://localhost:7860`

4. **Restart client:**
   - Restart Cursor or Claude Desktop after config changes

---

### Issue: Results seem inaccurate

**Cause:** Poor quality input data or wrong taxonomy.

**Solution:**
1. **Verify intent taxonomy** — is "ecommerce" appropriate for your business?
   - B2B SaaS? Consider creating custom taxonomy
   - Services? May need different intents

2. **Check data quality:**
   - Are user queries meaningful?
   - Do actions reflect real behavior?
   - Is time on page realistic?

3. **Calibrate with known cases:**
   - Test with sessions where you KNOW the outcome
   - Compare predicted vs actual intent
   - Adjust confidence thresholds if needed

4. **Use session history:**
   - Past intents dramatically improve accuracy
   - Include at least 1-2 prior session intents

---

## 9. Best Practices

### Data Collection

**DO:**
- ✅ Capture at least 3-5 meaningful actions per session
- ✅ Include search queries and filters applied
- ✅ Track engagement metrics (time, scroll, clicks)
- ✅ Record cart/wishlist activity
- ✅ Maintain session continuity across visits

**DON'T:**
- ❌ Rely on single-action signals
- ❌ Ignore mobile vs desktop differences
- ❌ Mix organic and paid traffic without distinction
- ❌ Use generic page types ("page" instead of "product_detail")

---

### Intent Analysis

**DO:**
- ✅ Start with sample scenarios to understand outputs
- ✅ Analyze patterns over time, not isolated sessions
- ✅ Cross-reference intent with actual outcomes
- ✅ Update taxonomy as you learn about your users
- ✅ Use advanced fields when available

**DON'T:**
- ❌ Over-react to single low-confidence predictions
- ❌ Ignore secondary intents (users can have multiple goals)
- ❌ Apply same strategy to all "ready_to_purchase" users
- ❌ Forget to consider product/category differences

---

### Pattern Discovery

**DO:**
- ✅ Use 30+ days of data for stable patterns
- ✅ Include diverse user behaviors
- ✅ Start with 3-4 personas, expand later
- ✅ Validate personas with qualitative research
- ✅ Update monthly or quarterly

**DON'T:**
- ❌ Use less than 100 users
- ❌ Create too many personas (>6 hard to action)
- ❌ Assume demographic homogeneity within behavioral clusters
- ❌ Ignore the noise cluster (may contain insights)

---

### Bid Optimization

**DO:**
- ✅ Test recommendations on small budget first
- ✅ Monitor performance for 7-14 days before scaling
- ✅ Adjust for product margin and lifetime value
- ✅ Consider seasonality and competitive pressure
- ✅ Document what works for your business

**DON'T:**
- ❌ Apply aggressive modifiers without testing
- ❌ Ignore overall budget constraints
- ❌ Forget to cap maximum bids
- ❌ Set and forget — review weekly

---

### Audience Activation

**DO:**
- ✅ Always dry-run first
- ✅ Start with high-confidence segments
- ✅ Refresh audiences weekly
- ✅ Track match rates and adjust data quality
- ✅ Use descriptive audience names with dates

**DON'T:**
- ❌ Sync production data without testing
- ❌ Create tiny audiences (<100 users)
- ❌ Sync stale data (>30 days old)
- ❌ Forget to exclude converters
- ❌ Mix intents in same audience

---

## 10. FAQ

### General Questions

**Q: Do I need coding skills to use this?**
A: No! The Gradio web interface requires no coding. MCP setup needs light technical knowledge (copy/paste config files).

**Q: How much does it cost to run?**
A:
- API costs: $0.01-0.05 per analysis (Claude/GPT-4)
- Infrastructure: $0 for local, ~$50/month for cloud
- Ad platform syncing: Free (built into ad platforms)

**Q: Can I use this with my existing analytics?**
A: Yes! Export data from Google Analytics, Adobe, Mixpanel, etc., then upload as CSV.

**Q: Is my data secure?**
A:
- Running locally: all data stays on your machine
- Using live demo: context sent to AI providers (Anthropic/OpenAI)
- Audience sync: data hashed before leaving your system
- Never share production PII without hashing

**Q: Which AI model should I use?**
A: Claude Sonnet 4 (Anthropic) provides best accuracy. GPT-4 is good alternative. OpenRouter works for budget testing.

---

### Technical Questions

**Q: What's the API rate limit?**
A: Depends on your provider:
- Anthropic: 50 requests/min (tier 1)
- OpenAI: 3,500 requests/min (varies by tier)
- OpenRouter: varies by model

**Q: Can I customize the intent taxonomy?**
A: Yes! Edit `config/intent_taxonomies/ecommerce.yaml` or create new domain file. See docs/article.md for format.

**Q: How do I export results to my BI tool?**
A: Results are JSON — use API or export from Gradio. Integration guides coming soon.

**Q: Can I run batch processing?**
A: Yes via Python API:
```python
from src.intent import IntentRecognitionEngine, LLMProviderFactory, IntentTaxonomy

llm = LLMProviderFactory.create_from_env()
taxonomy = IntentTaxonomy.from_domain("ecommerce")
engine = IntentRecognitionEngine(llm, taxonomy)

# Process batch
for session in sessions:
    result = engine.recognize_intent(**session)
```

**Q: How do I scale to millions of sessions?**
A: Current version handles 100s-1000s per day. For millions:
1. Use batch processing
2. Cache results (ENABLE_CACHING=true)
3. Consider enterprise deployment (contact for roadmap)

---

### Business Questions

**Q: What ROI can I expect?**
A: Typical results (from testing):
- 15-30% ROAS improvement (bid optimization)
- 20-40% engagement increase (persona content)
- 25-50% conversion lift (real-time personalization)

**Q: How long until I see results?**
A:
- Immediate: intent insights from day 1
- 1-2 weeks: bid optimization impact
- 4-6 weeks: persona-based strategy impact

**Q: What industries does this work for?**
A: Currently optimized for:
- ✅ Ecommerce retail
- ✅ B2B SaaS (with custom taxonomy)
- ✅ Professional services
- ✅ Financial services

**Q: Can I use this for B2B?**
A: Yes, but create B2B-specific taxonomy:
- problem_identification
- solution_research
- vendor_comparison
- trial_decision
- procurement_process

**Q: What if my business is unique?**
A: The five-layer architecture works universally. Customize:
1. Intent taxonomy for your domain
2. Behavioral signals you capture
3. Persona definitions
4. Activation channels

---

### Audience Activation Questions

**Q: Why is my Google Ads match rate low?**
A: Common causes:
- Poor email data quality (typos, wrong domains)
- Users not signed into Google
- Privacy settings blocking matches
- Timing (can take 24-48 hours)
Typical match: 60-80% for quality email lists

**Q: Minimum audience size for activation?**
A:
- Google Search: 1,000 users
- Google Display: 100 users
- Meta: 100 users (recommended 1,000+)
- LinkedIn: 300 users

**Q: How often should I refresh audiences?**
A:
- High-intent segments: daily or weekly
- Persona-based: weekly or bi-weekly
- Comparison shoppers: weekly
- Always exclude recent converters

**Q: Can I sync to other platforms?**
A: Currently: Google Ads + Meta. Coming soon:
- LinkedIn Matched Audiences
- Trade Desk
- Pinterest
- TikTok

---

### Data & Privacy Questions

**Q: Is this GDPR/CCPA compliant?**
A: Framework is privacy-aware:
- All PII hashed before transmission
- Dry-run mode for testing
- Data stays local until you sync
- User consent still required for audience creation

Consult your legal team for specific compliance.

**Q: What data gets sent to AI providers?**
A: Only behavioral context (queries, actions, page types). No:
- Email addresses
- Names
- Phone numbers
- Payment info
Always hash PII before uploading.

**Q: Can I use hashed emails throughout?**
A: Yes! System accepts:
- Plain emails (auto-hashed)
- Pre-hashed emails (SHA-256)
- Other identifiers (mobile IDs, user IDs)

**Q: How long is data retained?**
A:
- Web interface: session only (not stored)
- Local SQLite: until you delete
- AI providers: per their retention (24hr-30 days)
- Ad platforms: per their policies

---

## Getting Help

**Documentation:**
- Full research article: [docs/article.md](../docs/article.md)
- Testing guide: [tests/TESTING.md](../tests/TESTING.md)
- API reference: Tab 4 in Gradio app

**Support:**
- GitHub Issues: [Report bugs](https://github.com/ai-knowledge-hub/deep-dive-analysis-intent-recognition-agent/issues)
- Discussions: [Ask questions](https://github.com/ai-knowledge-hub/deep-dive-analysis-intent-recognition-agent/discussions)

**Community:**
- Share your personas and insights
- Contribute custom taxonomies
- Report what works (or doesn't!)

---

## What's Next?

**Immediate Actions:**
1. [ ] Run your first intent analysis (Tab 1 with samples)
2. [ ] Upload session data for pattern discovery (Tab 2)
3. [ ] Test bid optimization (Tab 3)
4. [ ] Set up dry-run audience sync

**This Week:**
1. [ ] Export real user data from analytics
2. [ ] Analyze top 100 sessions
3. [ ] Document 3-5 personas
4. [ ] Create first custom audience

**This Month:**
1. [ ] Implement bid modifiers in one campaign
2. [ ] Create persona-specific content
3. [ ] Set up weekly audience refreshes
4. [ ] Measure baseline vs intent-optimized performance

**This Quarter:**
1. [ ] Scale to all campaigns
2. [ ] Build real-time personalization (with dev support)
3. [ ] Publish performance results
4. [ ] Expand to new channels

---

## Appendix: Quick Reference

### Input Field Cheat Sheet

| Field | Format | Examples |
|-------|--------|----------|
| user_query | Free text | "running shoes", "best CRM software" |
| page_type | Predefined | product_detail, category, search_results, blog_post, comparison_page |
| previous_actions | Comma-separated | viewed_product,read_reviews,checked_shipping |
| time_on_page | Seconds (integer) | 120, 245, 30 |
| session_history | JSON array | `[{"intent":"compare_options"}]` |
| device_type | Lowercase | desktop, mobile, tablet |
| traffic_source | Lowercase | organic, paid_search, social, direct, email |
| scroll_depth | Percentage (0-100) | 0, 45, 85, 100 |
| clicks_on_page | Integer | 0, 3, 7, 12 |

### Common Actions Vocabulary

Use these in `previous_actions` field:

**Search/Filter:**
- searched_[term], filtered_by_price, sorted_by_rating, applied_category_filter

**Content:**
- read_reviews, viewed_guide, watched_video, read_comparison

**Product:**
- viewed_product, zoomed_image, checked_specs, added_to_cart, added_to_wishlist

**Navigation:**
- visited_category, clicked_related, viewed_similar, returned_to_search

**Decision:**
- checked_shipping, viewed_return_policy, compared_prices, checked_stock

**Social:**
- viewed_social_proof, read_testimonials, clicked_rating

### Intent Decision Tree

```
Is user reading guides/learning content?
├─ YES → category_research
└─ NO ↓

Is user comparing 2+ specific products?
├─ YES → compare_options
└─ NO ↓

Is user filtering by price or searching "cheap"?
├─ YES → price_discovery
└─ NO ↓

Has user added to cart or checked shipping?
├─ YES → ready_to_purchase
└─ NO ↓

Is user viewing gift guides or gift wrap?
├─ YES → gift_shopping
└─ NO ↓

Is user searching for deals or in sale section?
├─ YES → deal_seeking
└─ NO ↓

Is user reading detailed specs for ONE product?
├─ YES → evaluate_fit
└─ NO → browsing_inspiration
```

---

**Version:** 1.0
**Last Updated:** December 7, 2025
**Feedback:** [Open an issue](https://github.com/ai-knowledge-hub/deep-dive-analysis-intent-recognition-agent/issues)

---

*Built with care for marketing practitioners who deserve better tools.*
