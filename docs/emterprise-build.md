# Intent-Recognition Agent Starter Kit - Repository Structure

This document outlines the complete repository structure for building an LLM-powered intent recognition agent for digital marketing.

## Repository Overview

```
intent-recognition-agent/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
├── .env.example
├── requirements.txt
├── setup.py
├── docker-compose.yml
├── Dockerfile
│
├── docs/                                    # Documentation
│   ├── index.md
│   ├── getting-started.md
│   ├── architecture.md
│   ├── api-reference.md
│   ├── deployment.md
│   ├── testing-guide.md
│   ├── hypotheses/
│   │   ├── hypothesis-1-context-richness.md
│   │   ├── hypothesis-2-llm-accuracy.md
│   │   ├── hypothesis-3-confidence-calibration.md
│   │   ├── hypothesis-4-pattern-stability.md
│   │   ├── hypothesis-5-targeting-performance.md
│   │   ├── hypothesis-6-bidding-optimization.md
│   │   └── hypothesis-7-feedback-loop.md
│   └── case-studies/
│       ├── athletic-footwear-retailer.md
│       └── template.md
│
├── config/                                  # Configuration files
│   ├── intent-taxonomies/
│   │   ├── ecommerce.yaml
│   │   ├── b2b-saas.yaml
│   │   ├── financial-services.yaml
│   │   └── custom-template.yaml
│   ├── prompts/
│   │   ├── intent-classification.txt
│   │   ├── pattern-description.txt
│   │   ├── content-generation.txt
│   │   └── confidence-calibration.txt
│   ├── schemas/
│   │   ├── context-schema.json
│   │   ├── intent-result-schema.json
│   │   └── pattern-schema.json
│   └── environments/
│       ├── development.yaml
│       ├── staging.yaml
│       └── production.yaml
│
├── src/                                     # Source code
│   ├── __init__.py
│   │
│   ├── context_capture/                    # Phase 1: Context Capture Layer
│   │   ├── __init__.py
│   │   ├── base.py                         # Base context capturer
│   │   ├── schema.py                       # Context schema definitions
│   │   ├── channels/
│   │   │   ├── __init__.py
│   │   │   ├── search.py                   # Google/Bing Ads capture
│   │   │   ├── programmatic.py             # Display ad capture
│   │   │   ├── ecommerce.py                # Website/app capture
│   │   │   ├── social.py                   # Meta/LinkedIn capture
│   │   │   └── email.py                    # Email engagement capture
│   │   ├── enrichers/
│   │   │   ├── __init__.py
│   │   │   ├── temporal.py                 # Add temporal context
│   │   │   ├── historical.py               # Add user history
│   │   │   └── device.py                   # Add device/location info
│   │   ├── validators/
│   │   │   ├── __init__.py
│   │   │   ├── completeness.py             # Check context quality
│   │   │   └── privacy.py                  # PII filtering
│   │   └── pipelines/
│   │       ├── __init__.py
│   │       ├── streaming.py                # Real-time pipeline
│   │       └── batch.py                    # Batch processing
│   │
│   ├── intent_recognition/                 # Phase 2: Intent Recognition Engine
│   │   ├── __init__.py
│   │   ├── engine.py                       # Main intent recognition engine
│   │   ├── taxonomy.py                     # Intent taxonomy management
│   │   ├── llm_providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                     # Base LLM provider interface
│   │   │   ├── openai_provider.py          # OpenAI integration
│   │   │   ├── anthropic_provider.py       # Anthropic integration
│   │   │   ├── aws_bedrock_provider.py     # AWS Bedrock integration
│   │   │   └── google_vertex_provider.py   # Google Vertex AI
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   ├── builder.py                  # Dynamic prompt construction
│   │   │   └── templates.py                # Prompt templates
│   │   ├── calibration/
│   │   │   ├── __init__.py
│   │   │   ├── confidence.py               # Confidence calibration
│   │   │   ├── historical.py               # Historical accuracy tracking
│   │   │   └── bayesian.py                 # Bayesian updating
│   │   ├── validation/
│   │   │   ├── __init__.py
│   │   │   ├── accuracy.py                 # Accuracy measurement
│   │   │   └── consistency.py              # Cross-validation
│   │   └── caching/
│   │       ├── __init__.py
│   │       └── response_cache.py           # Cache frequent patterns
│   │
│   ├── pattern_discovery/                  # Phase 3: Pattern Discovery System
│   │   ├── __init__.py
│   │   ├── embedder.py                     # Behavioral embedding creation
│   │   ├── clustering/
│   │   │   ├── __init__.py
│   │   │   ├── hdbscan.py                  # HDBSCAN clustering
│   │   │   ├── kmeans.py                   # K-means alternative
│   │   │   └── hierarchical.py             # Hierarchical clustering
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── cluster_analyzer.py         # Cluster characteristic extraction
│   │   │   ├── persona_generator.py        # LLM-based persona creation
│   │   │   └── significance.py             # Statistical significance tests
│   │   ├── stability/
│   │   │   ├── __init__.py
│   │   │   ├── temporal.py                 # Temporal validation
│   │   │   └── cross_validation.py         # Cross-period validation
│   │   └── visualization/
│   │       ├── __init__.py
│   │       ├── embeddings.py               # t-SNE/UMAP visualization
│   │       └── patterns.py                 # Pattern distribution plots
│   │
│   ├── activation/                         # Phase 4: Activation Interface
│   │   ├── __init__.py
│   │   ├── base.py                         # Base activation interface
│   │   ├── audiences/
│   │   │   ├── __init__.py
│   │   │   ├── google_ads.py               # Google Ads Customer Match
│   │   │   ├── meta_ads.py                 # Meta Custom Audiences
│   │   │   ├── linkedin_ads.py             # LinkedIn Matched Audiences
│   │   │   ├── the_trade_desk.py           # The Trade Desk integration
│   │   │   └── audience_manager.py         # Unified audience management
│   │   ├── personalization/
│   │   │   ├── __init__.py
│   │   │   ├── content.py                  # Content personalization
│   │   │   ├── recommendations.py          # Product recommendations
│   │   │   └── email.py                    # Email personalization
│   │   ├── bidding/
│   │   │   ├── __init__.py
│   │   │   ├── optimizer.py                # Bid optimization logic
│   │   │   └── conversion_model.py         # Conversion probability model
│   │   └── creative/
│   │       ├── __init__.py
│   │       └── generator.py                # Intent-aware creative generation
│   │
│   ├── measurement/                        # Phase 5: Measurement & Feedback
│   │   ├── __init__.py
│   │   ├── metrics/
│   │   │   ├── __init__.py
│   │   │   ├── accuracy.py                 # Classification accuracy
│   │   │   ├── business.py                 # ROAS, CPA, CVR metrics
│   │   │   └── system.py                   # Latency, reliability
│   │   ├── feedback/
│   │   │   ├── __init__.py
│   │   │   ├── collector.py                # Feedback collection
│   │   │   ├── validator.py                # Ground truth validation
│   │   │   └── loop.py                     # Continuous learning loop
│   │   ├── attribution/
│   │   │   ├── __init__.py
│   │   │   ├── multi_touch.py              # Multi-touch attribution
│   │   │   └── intent_based.py             # Intent-aware attribution
│   │   ├── experimentation/
│   │   │   ├── __init__.py
│   │   │   ├── ab_test.py                  # A/B testing framework
│   │   │   ├── power_analysis.py           # Statistical power calculation
│   │   │   └── hypothesis_tracker.py       # Track hypothesis tests
│   │   └── dashboards/
│   │       ├── __init__.py
│   │       ├── executive.py                # Executive dashboard data
│   │       └── operational.py              # Operational dashboard data
│   │
│   ├── data/                               # Data layer
│   │   ├── __init__.py
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── postgres.py                 # PostgreSQL storage
│   │   │   ├── bigquery.py                 # BigQuery storage
│   │   │   ├── s3.py                       # S3 storage
│   │   │   └── redis.py                    # Redis caching
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── context.py                  # Context data model
│   │   │   ├── intent.py                   # Intent data model
│   │   │   ├── pattern.py                  # Pattern data model
│   │   │   └── feedback.py                 # Feedback data model
│   │   └── migrations/
│   │       ├── versions/
│   │       └── env.py
│   │
│   ├── utils/                              # Utilities
│   │   ├── __init__.py
│   │   ├── config.py                       # Configuration management
│   │   ├── logging.py                      # Logging setup
│   │   ├── encryption.py                   # PII encryption
│   │   ├── validators.py                   # Data validators
│   │   └── monitoring.py                   # System monitoring
│   │
│   └── api/                                # API layer
│       ├── __init__.py
│       ├── main.py                         # FastAPI application
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── context.py                  # Context submission endpoints
│       │   ├── intent.py                   # Intent recognition endpoints
│       │   ├── patterns.py                 # Pattern query endpoints
│       │   ├── activation.py               # Activation endpoints
│       │   └── metrics.py                  # Metrics endpoints
│       ├── middleware/
│       │   ├── __init__.py
│       │   ├── auth.py                     # Authentication
│       │   ├── rate_limit.py               # Rate limiting
│       │   └── cors.py                     # CORS configuration
│       └── dependencies/
│           ├── __init__.py
│           └── common.py                   # Shared dependencies
│
├── tests/                                  # Test suite
│   ├── __init__.py
│   ├── conftest.py                         # Pytest configuration
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── context_samples.py              # Sample contexts
│   │   ├── intent_samples.py               # Sample intents
│   │   └── pattern_samples.py              # Sample patterns
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_context_capture.py
│   │   ├── test_intent_recognition.py
│   │   ├── test_pattern_discovery.py
│   │   ├── test_activation.py
│   │   └── test_measurement.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_end_to_end.py
│   │   ├── test_api.py
│   │   └── test_pipelines.py
│   └── performance/
│       ├── __init__.py
│       ├── test_latency.py
│       └── test_throughput.py
│
├── scripts/                                # Utility scripts
│   ├── setup/
│   │   ├── init_database.py                # Initialize database
│   │   ├── create_tables.py                # Create tables
│   │   └── seed_data.py                    # Seed test data
│   ├── training/
│   │   ├── label_data.py                   # Data labeling interface
│   │   ├── train_calibration.py            # Train calibration model
│   │   └── evaluate_model.py               # Model evaluation
│   ├── deployment/
│   │   ├── deploy_api.sh                   # Deploy API
│   │   ├── deploy_workers.sh               # Deploy background workers
│   │   └── health_check.py                 # Health check script
│   └── analysis/
│       ├── analyze_patterns.py             # Pattern analysis
│       ├── generate_report.py              # Performance report generation
│       └── export_audiences.py             # Audience export script
│
├── notebooks/                              # Jupyter notebooks
│   ├── 01-data-exploration.ipynb
│   ├── 02-intent-analysis.ipynb
│   ├── 03-pattern-discovery.ipynb
│   ├── 04-performance-analysis.ipynb
│   ├── 05-hypothesis-testing.ipynb
│   └── 06-visualization.ipynb
│
├── examples/                               # Example implementations
│   ├── quickstart/
│   │   ├── basic_intent_recognition.py
│   │   ├── simple_pattern_discovery.py
│   │   └── audience_export.py
│   ├── advanced/
│   │   ├── multi_channel_integration.py
│   │   ├── real_time_personalization.py
│   │   └── cross_channel_attribution.py
│   └── channel_specific/
│       ├── google_ads_integration.py
│       ├── meta_ads_integration.py
│       ├── ecommerce_implementation.py
│       └── programmatic_integration.py
│
├── infrastructure/                         # Infrastructure as code
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── modules/
│   │   │   ├── vpc/
│   │   │   ├── database/
│   │   │   ├── api/
│   │   │   └── workers/
│   │   └── environments/
│   │       ├── development/
│   │       ├── staging/
│   │       └── production/
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── api-deployment.yaml
│   │   ├── worker-deployment.yaml
│   │   ├── ingress.yaml
│   │   └── monitoring/
│   │       ├── prometheus.yaml
│   │       └── grafana.yaml
│   └── docker/
│       ├── api.Dockerfile
│       ├── worker.Dockerfile
│       └── notebook.Dockerfile
│
├── monitoring/                             # Monitoring configuration
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alerts.yml
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── executive-dashboard.json
│   │   │   ├── operational-dashboard.json
│   │   │   └── system-health.json
│   │   └── datasources/
│   │       └── prometheus.yaml
│   └── logs/
│       └── logstash.conf
│
├── data/                                   # Data directory (gitignored)
│   ├── raw/
│   ├── processed/
│   ├── models/
│   └── exports/
│
└── deployments/                            # Deployment artifacts
    ├── docker-compose.dev.yml
    ├── docker-compose.prod.yml
    └── .dockerignore
```

## Key Files Detailed Description

### Root Level Files

#### README.md
```markdown
# Intent-Recognition Agent Starter Kit

Enterprise-grade LLM-powered intent recognition system for digital marketing.

## Features
- Multi-channel context capture (Search, Social, Display, Ecommerce)
- LLM-based intent classification with confidence calibration
- Behavioral pattern discovery and clustering
- Automated audience activation across ad platforms
- Continuous feedback loops and model improvement

## Quick Start
[Installation and setup instructions]

## Documentation
[Links to comprehensive docs]

## Examples
[Links to example implementations]

## Support
[Community and commercial support information]
```

#### requirements.txt
```
# Core dependencies
fastapi==0.104.1
pydantic==2.5.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
alembic==1.12.1

# LLM providers
openai==1.3.7
anthropic==0.7.7
boto3==1.29.7  # AWS Bedrock
google-cloud-aiplatform==1.38.1

# Data processing
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
sentence-transformers==2.2.2

# Clustering
hdbscan==0.8.33
umap-learn==0.5.5

# Storage
psycopg2-binary==2.9.9
redis==5.0.1
google-cloud-bigquery==3.13.0

# Ad platform integrations
google-ads==23.0.0
facebook-business==18.0.0

# API
uvicorn==0.24.0
httpx==0.25.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Monitoring
prometheus-client==0.19.0
sentry-sdk==1.38.0

# Utilities
pyyaml==6.0.1
jsonschema==4.20.0
python-dateutil==2.8.2
```

#### .env.example
```bash
# Environment
ENVIRONMENT=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# LLM Providers
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=us-east-1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/intent_db
REDIS_URL=redis://localhost:6379/0

# BigQuery (optional)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
BIGQUERY_PROJECT_ID=your_project_id
BIGQUERY_DATASET=intent_data

# Ad Platform Credentials
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token

META_ACCESS_TOKEN=your_meta_token
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret

# Monitoring
SENTRY_DSN=your_sentry_dsn
PROMETHEUS_PORT=9090

# Feature Flags
ENABLE_CACHING=true
ENABLE_REAL_TIME_PROCESSING=true
ENABLE_FEEDBACK_LOOP=true
```

## Configuration Files

### config/intent-taxonomies/ecommerce.yaml
```yaml
name: "Ecommerce Intent Taxonomy"
version: "1.0"
description: "Standard intent taxonomy for ecommerce retail"

intents:
  # Awareness Stage
  browsing_inspiration:
    stage: awareness
    description: "User is exploring with no specific goal"
    typical_signals:
      - high_page_variety
      - low_time_per_page
      - no_search_queries
    
  category_research:
    stage: awareness
    description: "Learning about product types and categories"
    typical_signals:
      - category_page_views
      - guide_reading
      - comparison_article_views
  
  # Consideration Stage
  compare_options:
    stage: consideration
    description: "Evaluating specific alternatives"
    typical_signals:
      - multiple_product_views
      - comparison_tool_usage
      - review_reading
      - spec_comparison
  
  price_discovery:
    stage: consideration
    description: "Understanding cost ranges and seeking value"
    typical_signals:
      - price_filter_usage
      - sort_by_price
      - promotion_page_views
  
  # Decision Stage  
  ready_to_purchase:
    stage: decision
    description: "High buying intent, final validation"
    typical_signals:
      - add_to_cart
      - checkout_initiation
      - shipping_calculator_usage
      - return_policy_view
  
  deal_seeking:
    stage: decision
    description: "Waiting for promotion or discount"
    typical_signals:
      - coupon_search
      - sale_page_visits
      - price_alert_signup
  
  gift_shopping:
    stage: decision
    description: "Purchasing for someone else"
    typical_signals:
      - gift_filter_usage
      - gift_guide_views
      - gift_card_consideration
      - popular_items_browsing

confidence_modifiers:
  strong_signals:
    add_to_cart: 0.3
    checkout_initiated: 0.4
    review_reading: 0.2
  
  weak_signals:
    single_page_view: -0.1
    high_bounce: -0.2
    
  temporal_factors:
    returning_user: 0.15
    recent_purchase: -0.25
    session_duration_long: 0.1
```

### config/prompts/intent-classification.txt
```
You are an expert behavioral analyst specializing in customer intent recognition.

Given the following user context, identify the user's primary intent and provide justification.

USER CONTEXT:
{context_json}

INTENT TAXONOMY:
{intent_definitions}

ANALYSIS INSTRUCTIONS:
1. Review the user's actions in sequence
2. Consider both explicit signals (clicks, searches) and implicit signals (time, scroll depth)
3. Weight recent actions more heavily than historical context
4. Consider temporal context (day, time, urgency indicators)
5. Identify the most likely intent from the taxonomy

OUTPUT FORMAT (JSON):
{
  "primary_intent": "<intent_label>",
  "confidence": <0.0-1.0>,
  "justification": "<reasoning>",
  "secondary_intents": ["<intent_label>", ...],
  "behavioral_evidence": [
    "evidence_point_1",
    "evidence_point_2"
  ],
  "predicted_next_actions": [
    "likely_action_1",
    "likely_action_2"
  ],
  "uncertainty_factors": [
    "ambiguity_1",
    "ambiguity_2"
  ]
}

Provide your analysis:
```

## Source Code Structure

### src/context_capture/base.py
```python
"""
Base context capture interface.
All channel-specific capturers inherit from this.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from .schema import ContextSchema

class BaseContextCapturer(ABC):
    """Base class for context capture implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.schema = ContextSchema()
    
    @abstractmethod
    async def capture(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture and normalize context from raw data.
        
        Args:
            raw_data: Raw event data from the channel
            
        Returns:
            Normalized context dict following the schema
        """
        pass
    
    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> bool:
        """
        Validate captured context meets quality standards.
        
        Args:
            context: Captured context to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def enrich(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich context with additional data.
        Override in subclasses for channel-specific enrichment.
        
        Args:
            context: Base context to enrich
            
        Returns:
            Enriched context
        """
        return context
    
    def _add_timestamp(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add capture timestamp to context."""
        context['captured_at'] = datetime.utcnow().isoformat()
        return context
    
    def _filter_pii(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove PII from context."""
        pii_fields = ['email', 'phone', 'name', 'address']
        for field in pii_fields:
            context.pop(field, None)
        return context
```

### src/intent_recognition/engine.py
```python
"""
Main intent recognition engine.
Coordinates LLM inference, calibration, and caching.
"""
from typing import Dict, Any, Optional, List
from .llm_providers.base import BaseLLMProvider
from .calibration.confidence import ConfidenceCalibrator
from .taxonomy import IntentTaxonomy
from .caching.response_cache import ResponseCache

class IntentRecognitionEngine:
    """LLM-powered intent recognition engine."""
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        taxonomy: IntentTaxonomy,
        calibrator: Optional[ConfidenceCalibrator] = None,
        cache: Optional[ResponseCache] = None
    ):
        self.llm = llm_provider
        self.taxonomy = taxonomy
        self.calibrator = calibrator or ConfidenceCalibrator()
        self.cache = cache
    
    async def recognize_intent(
        self,
        context: Dict[str, Any],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Recognize user intent from behavioral context.
        
        Args:
            context: User behavioral context
            use_cache: Whether to use cached results
            
        Returns:
            Intent classification result with confidence
        """
        # Check cache
        if use_cache and self.cache:
            cached_result = await self.cache.get(context)
            if cached_result:
                return cached_result
        
        # Build prompt
        prompt = self._build_prompt(context)
        
        # Get LLM inference
        raw_result = await self.llm.classify(prompt)
        
        # Calibrate confidence
        calibrated_result = self.calibrator.calibrate(
            raw_result,
            context
        )
        
        # Cache result
        if use_cache and self.cache:
            await self.cache.set(context, calibrated_result)
        
        return calibrated_result
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Build intent classification prompt."""
        # Implementation in prompts/builder.py
        pass
    
    async def batch_recognize(
        self,
        contexts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Recognize intents for multiple contexts in batch.
        
        Args:
            contexts: List of user contexts
            
        Returns:
            List of intent results
        """
        # Parallel processing implementation
        pass
```

### src/pattern_discovery/embedder.py
```python
"""
Behavioral embedding creation.
Transforms intent sequences into vector representations.
"""
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler

class BehavioralEmbedder:
    """Creates embeddings from user intent histories."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.text_encoder = SentenceTransformer(model_name)
        self.scaler = StandardScaler()
    
    def create_embedding(
        self,
        user_history: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Create behavioral embedding for a user.
        
        Args:
            user_history: List of intent records for a user
            
        Returns:
            Feature vector representing behavioral pattern
        """
        # 1. Intent sequence embedding
        intent_sequence = " -> ".join([
            r['primary_intent'] for r in user_history
        ])
        intent_embedding = self.text_encoder.encode(intent_sequence)
        
        # 2. Behavioral features
        behavioral_features = self._extract_behavioral_features(user_history)
        
        # 3. Temporal features
        temporal_features = self._extract_temporal_features(user_history)
        
        # 4. Channel features
        channel_features = self._extract_channel_features(user_history)
        
        # Concatenate all features
        full_embedding = np.concatenate([
            intent_embedding,
            behavioral_features,
            temporal_features,
            channel_features
        ])
        
        return full_embedding
    
    def _extract_behavioral_features(
        self,
        history: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Extract behavioral statistics."""
        return np.array([
            len(history),  # Session count
            np.mean([r['confidence'] for r in history]),  # Avg confidence
            len(set(r['primary_intent'] for r in history)),  # Intent diversity
            # ... more features
        ])
    
    def _extract_temporal_features(
        self,
        history: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Extract temporal patterns."""
        # Time between sessions, day of week patterns, etc.
        pass
    
    def _extract_channel_features(
        self,
        history: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Extract channel distribution."""
        # Channel mix, cross-channel patterns
        pass
```

### src/activation/audiences/google_ads.py
```python
"""
Google Ads Customer Match integration.
Creates and manages intent-based audiences.
"""
from typing import Dict, Any, List
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

class GoogleAdsActivator:
    """Manages Google Ads audience creation and updates."""
    
    def __init__(self, credentials_path: str):
        self.client = GoogleAdsClient.load_from_storage(credentials_path)
    
    async def create_intent_audience(
        self,
        customer_id: str,
        pattern: Dict[str, Any]
    ) -> str:
        """
        Create a Customer Match audience from an intent pattern.
        
        Args:
            customer_id: Google Ads customer ID
            pattern: Intent pattern with user IDs
            
        Returns:
            Resource name of created user list
        """
        user_list_service = self.client.get_service("UserListService")
        
        # Create user list
        user_list_operation = self.client.get_type("UserListOperation")
        user_list = user_list_operation.create
        
        user_list.name = f"Intent: {pattern['description']['persona_name']}"
        user_list.description = pattern['description']['behavioral_description']
        user_list.membership_life_span = 540  # 540 days
        user_list.crm_based_user_list.upload_key_type = (
            self.client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
        )
        
        # Upload user list
        response = user_list_service.mutate_user_lists(
            customer_id=customer_id,
            operations=[user_list_operation]
        )
        
        user_list_resource_name = response.results[0].resource_name
        
        # Add members
        await self._add_members_to_list(
            customer_id,
            user_list_resource_name,
            pattern['user_ids']
        )
        
        return user_list_resource_name
    
    async def _add_members_to_list(
        self,
        customer_id: str,
        user_list: str,
        user_ids: List[str]
    ):
        """Add users to the Customer Match list."""
        # Implementation for adding hashed user data
        pass
    
    async def update_audience(
        self,
        customer_id: str,
        user_list_resource_name: str,
        new_user_ids: List[str]
    ):
        """Update existing audience with new users."""
        pass
    
    async def remove_users(
        self,
        customer_id: str,
        user_list_resource_name: str,
        user_ids_to_remove: List[str]
    ):
        """Remove users from audience."""
        pass
```

### src/api/main.py
```python
"""
FastAPI application for the Intent Recognition API.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routes import context, intent, patterns, activation, metrics
from .middleware.auth import auth_middleware
from .middleware.rate_limit import rate_limit_middleware
from src.utils.config import get_settings
from src.utils.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    setup_logging()
    # Initialize database connections
    # Initialize LLM providers
    # Initialize cache
    yield
    # Shutdown
    # Close connections

app = FastAPI(
    title="Intent Recognition API",
    description="LLM-powered intent recognition for digital marketing",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(auth_middleware)
app.middleware("http")(rate_limit_middleware)

# Routes
app.include_router(context.router, prefix="/api/v1/context", tags=["context"])
app.include_router(intent.router, prefix="/api/v1/intent", tags=["intent"])
app.include_router(patterns.router, prefix="/api/v1/patterns", tags=["patterns"])
app.include_router(activation.router, prefix="/api/v1/activation", tags=["activation"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Intent Recognition API",
        "version": "1.0.0",
        "docs": "/docs"
    }
```

## Testing Structure

### tests/unit/test_intent_recognition.py
```python
"""
Unit tests for intent recognition engine.
"""
import pytest
from src.intent_recognition.engine import IntentRecognitionEngine
from src.intent_recognition.taxonomy import IntentTaxonomy
from tests.fixtures.context_samples import sample_contexts

@pytest.fixture
def intent_engine():
    """Create intent recognition engine for testing."""
    # Setup with mock LLM provider
    pass

@pytest.mark.asyncio
async def test_recognize_intent_high_confidence(intent_engine):
    """Test intent recognition with high-confidence signals."""
    context = sample_contexts['ready_to_purchase']
    result = await intent_engine.recognize_intent(context)
    
    assert result['primary_intent'] == 'ready_to_purchase'
    assert result['confidence'] > 0.8
    assert len(result['behavioral_evidence']) >= 3

@pytest.mark.asyncio
async def test_recognize_intent_ambiguous(intent_engine):
    """Test intent recognition with ambiguous signals."""
    context = sample_contexts['ambiguous']
    result = await intent_engine.recognize_intent(context)
    
    assert result['confidence'] < 0.6
    assert len(result['uncertainty_factors']) > 0

def test_confidence_calibration(intent_engine):
    """Test confidence score calibration."""
    # Test that confidence aligns with actual accuracy
    pass

def test_caching_behavior(intent_engine):
    """Test that caching works correctly."""
    # Test cache hit/miss behavior
    pass
```

## Example Implementations

### examples/quickstart/basic_intent_recognition.py
```python
"""
Quickstart: Basic intent recognition.
Demonstrates minimal setup for intent classification.
"""
import asyncio
from src.context_capture.channels.ecommerce import EcommerceContextCapturer
from src.intent_recognition.engine import IntentRecognitionEngine
from src.intent_recognition.llm_providers.openai_provider import OpenAIProvider
from src.intent_recognition.taxonomy import IntentTaxonomy

async def main():
    # 1. Load intent taxonomy
    taxonomy = IntentTaxonomy.from_file('config/intent-taxonomies/ecommerce.yaml')
    
    # 2. Initialize LLM provider
    llm_provider = OpenAIProvider(
        api_key="your_api_key",
        model="gpt-4"
    )
    
    # 3. Create intent recognition engine
    engine = IntentRecognitionEngine(
        llm_provider=llm_provider,
        taxonomy=taxonomy
    )
    
    # 4. Capture context (example: ecommerce session)
    capturer = EcommerceContextCapturer()
    context = await capturer.capture({
        'user_id': 'user_123',
        'page_type': 'product_detail',
        'actions': ['view', 'add_to_cart'],
        'time_on_page': 180
    })
    
    # 5. Recognize intent
    intent = await engine.recognize_intent(context)
    
    # 6. Display results
    print(f"Primary Intent: {intent['primary_intent']}")
    print(f"Confidence: {intent['confidence']:.2f}")
    print(f"Justification: {intent['justification']}")
    print(f"Next Actions: {', '.join(intent['predicted_next_actions'])}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Scripts

### scripts/training/label_data.py
```python
"""
Interactive data labeling tool for creating ground truth dataset.
"""
import streamlit as st
from src.data.storage.postgres import PostgresStorage

def main():
    st.title("Intent Labeling Tool")
    
    # Load unlabeled contexts
    storage = PostgresStorage()
    contexts = storage.get_unlabeled_contexts(limit=100)
    
    # Labeling interface
    for i, context in enumerate(contexts):
        st.subheader(f"Context {i+1}/{len(contexts)}")
        
        # Display context
        st.json(context)
        
        # Intent selection
        intent_label = st.selectbox(
            "Select primary intent:",
            options=taxonomy.get_all_intents(),
            key=f"intent_{i}"
        )
        
        # Confidence
        confidence = st.slider(
            "How confident are you?",
            0.0, 1.0, 0.8,
            key=f"confidence_{i}"
        )
        
        # Notes
        notes = st.text_area(
            "Additional notes:",
            key=f"notes_{i}"
        )
        
        # Save
        if st.button(f"Save Label {i+1}", key=f"save_{i}"):
            storage.save_label(
                context_id=context['id'],
                intent_label=intent_label,
                confidence=confidence,
                notes=notes
            )
            st.success("Label saved!")

if __name__ == "__main__":
    main()
```

This repository structure provides a complete, production-ready foundation for building an intent-recognition agent with clear separation of concerns, comprehensive testing, and deployment infrastructure.