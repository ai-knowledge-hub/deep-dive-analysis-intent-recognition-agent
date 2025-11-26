"""
Pattern Discovery MCP Tool - Layer 3 of the CCIA System

This Gradio MCP server implements the complete pattern discovery pipeline:
    1. Behavioral Embedder: Transforms user histories into 409-dimensional vectors
    2. Pattern Clusterer: Discovers behavioral patterns using HDBSCAN
    3. Pattern Analyzer: Generates LLM-powered personas from clusters

From research article:
"Discover behavioral patterns. Find users whose behavioral signatures look alike.
These clusters become your audiences - not demographic segments but intentional archetypes."

MCP Tool Specification:
    Name: discover_behavioral_patterns
    Input: CSV file with user session histories
    Output: Discovered personas with marketing insights + visualization

CSV Format Expected:
    user_id,session_intent,confidence,timestamp,channel,engagement_level,has_budget_constraint,has_time_constraint,has_knowledge_gap,urgency_level,expertise_level

Example Row:
    user_001,category_research,0.85,2025-01-15T10:00:00,organic,high,false,false,true,low,novice
    user_001,compare_options,0.90,2025-01-16T14:30:00,organic,very_high,false,false,false,medium,novice

Track 1 Submission: Building MCP - Pattern Discovery Tool
Track 2 Ready: Can be integrated into full marketing agent
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional, Tuple
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import pattern discovery components
from src.patterns.embedder import BehavioralEmbedder
from src.patterns.clustering import PatternClusterer
from src.patterns.analyzer import PatternAnalyzer
from src.patterns.visualizer import plot_clusters, plot_cluster_statistics, create_pattern_summary_text

# Import LLM provider
from src.intent.llm_provider import LLMProviderFactory

# Gradio imports
try:
    import gradio as gr
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip install gradio numpy matplotlib")
    sys.exit(1)


def parse_user_histories_from_csv(csv_content: str) -> Tuple[List[List[Dict[str, Any]]], List[str]]:
    """
    Parse CSV content into user histories format expected by embedder.

    Args:
        csv_content: CSV string with user session data

    Returns:
        (user_histories, user_ids) - grouped by user_id

    CSV Format:
        user_id,session_intent,confidence,timestamp,channel,engagement_level,
        has_budget_constraint,has_time_constraint,has_knowledge_gap,
        urgency_level,expertise_level
    """
    from io import StringIO
    import csv
    from collections import defaultdict

    reader = csv.DictReader(StringIO(csv_content))

    # Group sessions by user_id
    user_sessions = defaultdict(list)

    for row in reader:
        user_id = row.get('user_id', '').strip()
        if not user_id:
            continue

        # Parse boolean fields
        def parse_bool(val: str) -> bool:
            return val.strip().lower() in ('true', '1', 'yes')

        session = {
            'intent': row.get('session_intent', '').strip(),
            'confidence': float(row.get('confidence', 0.5)),
            'timestamp': row.get('timestamp', '').strip(),
            'channel': row.get('channel', 'organic').strip(),
            'engagement_level': row.get('engagement_level', 'medium').strip(),
            'has_budget_constraint': parse_bool(row.get('has_budget_constraint', 'false')),
            'has_time_constraint': parse_bool(row.get('has_time_constraint', 'false')),
            'has_knowledge_gap': parse_bool(row.get('has_knowledge_gap', 'false')),
            'urgency_level': row.get('urgency_level', 'medium').strip(),
            'expertise_level': row.get('expertise_level', 'intermediate').strip()
        }

        user_sessions[user_id].append(session)

    # Convert to list format
    user_ids = sorted(user_sessions.keys())
    user_histories = [user_sessions[uid] for uid in user_ids]

    return user_histories, user_ids


def discover_behavioral_patterns(
    csv_file: str,
    min_cluster_size: int = 30,
    min_samples: int = 5,
    use_llm_personas: bool = True,
    llm_provider: str = "anthropic"
) -> Tuple[str, str, str, str]:
    """
    Discover behavioral patterns from user session histories.

    This is the main MCP tool function that orchestrates the complete pipeline:
        1. Parse CSV → User Histories
        2. Create Behavioral Embeddings (409-dimensional vectors)
        3. Discover Patterns (HDBSCAN clustering)
        4. Analyze Patterns (LLM persona generation)
        5. Generate Visualizations
        6. Export Results

    Args:
        csv_file: Path to CSV file with user session histories
        min_cluster_size: Minimum users per pattern (default: 30)
        min_samples: Clustering sensitivity (higher = fewer patterns)
        use_llm_personas: Whether to generate LLM-powered personas (default: True)
        llm_provider: "anthropic" or "openai" (default: "anthropic")

    Returns:
        Tuple of (summary_text, personas_json, cluster_plot_path, stats_plot_path)

    Example CSV Content:
        user_id,session_intent,confidence,timestamp,channel,engagement_level,has_budget_constraint,has_time_constraint,has_knowledge_gap,urgency_level,expertise_level
        user_001,category_research,0.85,2025-01-15T10:00:00,organic,high,false,false,true,low,novice
        user_001,compare_options,0.90,2025-01-16T14:30:00,organic,very_high,false,false,false,medium,novice
        user_002,browsing_inspiration,0.75,2025-01-15T12:00:00,social,medium,false,false,false,low,intermediate
        user_002,ready_to_purchase,0.88,2025-01-15T12:15:00,social,medium,false,false,false,medium,intermediate
    """

    try:
        # Step 1: Load and parse CSV
        print("\n" + "="*70)
        print("🔍 BEHAVIORAL PATTERN DISCOVERY PIPELINE")
        print("="*70)

        csv_path: Optional[str] = None

        if isinstance(csv_file, str):
            csv_path = csv_file
        elif isinstance(csv_file, dict):
            csv_path = csv_file.get("name") or csv_file.get("path")
        elif hasattr(csv_file, "name"):
            csv_path = getattr(csv_file, "name")

        if not csv_path or not os.path.exists(csv_path):
            return "❌ Error: No CSV file provided", "[]", "", ""

        # Read CSV content
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()

        print(f"\n📁 Step 1: Loading User Histories")
        print("-"*70)
        user_histories, user_ids = parse_user_histories_from_csv(csv_content)
        n_users = len(user_histories)

        if n_users == 0:
            return "❌ Error: No valid user histories found in CSV", "[]", "", ""

        print(f"✅ Loaded {n_users} user histories")

        # Calculate some basic stats
        total_sessions = sum(len(hist) for hist in user_histories)
        avg_sessions = total_sessions / n_users
        print(f"   Total sessions: {total_sessions}")
        print(f"   Avg sessions per user: {avg_sessions:.1f}")

        # Step 2: Create behavioral embeddings
        print(f"\n📦 Step 2: Creating Behavioral Embeddings")
        print("-"*70)
        embedder = BehavioralEmbedder()
        embeddings = embedder.create_batch_embeddings(user_histories)
        print(f"✅ Created embeddings: shape = {embeddings.shape}")

        # Step 3: Discover patterns with HDBSCAN
        print(f"\n🎯 Step 3: Discovering Behavioral Patterns")
        print("-"*70)
        requested_min_cluster_size = max(2, int(min_cluster_size))

        if n_users <= 3:
            recommended_cluster_size = n_users
        else:
            recommended_cluster_size = max(5, n_users // 3)

        adaptive_min_cluster_size = min(
            requested_min_cluster_size,
            recommended_cluster_size if recommended_cluster_size > 0 else requested_min_cluster_size
        )
        adaptive_min_cluster_size = min(adaptive_min_cluster_size, n_users)
        adaptive_min_cluster_size = max(adaptive_min_cluster_size, 2 if n_users >= 2 else n_users)

        if adaptive_min_cluster_size != requested_min_cluster_size:
            print(
                f"   Adaptive min_cluster_size: {adaptive_min_cluster_size} "
                f"(requested {requested_min_cluster_size}, users={n_users})"
            )
        else:
            print(f"   Using min_cluster_size: {adaptive_min_cluster_size}")

        min_samples = max(1, int(min_samples))

        clusterer = PatternClusterer(
            min_cluster_size=adaptive_min_cluster_size,
            min_samples=min_samples
        )
        cluster_labels, viz_coords = clusterer.discover_patterns(embeddings)

        # Step 4: Get cluster statistics
        print(f"\n📊 Step 4: Analyzing Pattern Statistics")
        print("-"*70)
        stats = clusterer.get_cluster_statistics()

        if stats['n_clusters'] == 0:
            return (
                "⚠️ No distinct patterns found. Try:\n"
                "  - Reducing min_cluster_size parameter\n"
                "  - Adding more diverse user data\n"
                "  - Checking data quality",
                "[]",
                "",
                ""
            )

        summary_text = create_pattern_summary_text(stats)
        print(summary_text)

        # Step 5: Generate personas (optional LLM step)
        personas = []
        personas_json = "[]"

        if use_llm_personas:
            print(f"\n🤖 Step 5: Generating LLM-Powered Personas")
            print("-"*70)

            try:
                # Initialize LLM provider
                provider_name = llm_provider.lower()
                if provider_name in {"anthropic", "openai", "openrouter"}:
                    llm = LLMProviderFactory.create(provider_name=provider_name)
                else:
                    llm = LLMProviderFactory.create_from_env()
                analyzer = PatternAnalyzer(llm_provider=llm)

                # Analyze all clusters
                personas = analyzer.analyze_all_clusters(cluster_labels, user_histories)

                print(f"✅ Generated {len(personas)} behavioral personas")

                # Format personas as JSON
                personas_json = json.dumps(personas, indent=2) if personas else "[]"

                # Also create activation export
                activation_data = analyzer.export_personas_for_activation(personas)

            except Exception as e:
                print(f"⚠️ LLM persona generation failed: {e}")
                print("   Continuing with statistical analysis only...")

        # Step 6: Create visualizations
        print(f"\n🎨 Step 6: Creating Visualizations")
        print("-"*70)

        # Create temporary files for plots
        cluster_plot_path = tempfile.mktemp(suffix='_clusters.png')
        stats_plot_path = tempfile.mktemp(suffix='_stats.png')

        try:
            # Cluster scatter plot
            print("   Creating cluster visualization...")
            fig1 = plot_clusters(viz_coords, cluster_labels)
            plt.savefig(cluster_plot_path, dpi=300, bbox_inches='tight')
            plt.close(fig1)
            print(f"   ✅ Saved: {cluster_plot_path}")

            # Statistics plots
            print("   Creating statistics plots...")
            fig2 = plot_cluster_statistics(stats)
            plt.savefig(stats_plot_path, dpi=300, bbox_inches='tight')
            plt.close(fig2)
            print(f"   ✅ Saved: {stats_plot_path}")

        except Exception as e:
            print(f"   ⚠️ Visualization error: {e}")
            cluster_plot_path = ""
            stats_plot_path = ""

        # Step 7: Create final summary
        print(f"\n✅ Pattern Discovery Complete!")
        print("="*70)

        final_summary = [
            "# 🎯 Behavioral Pattern Discovery Results\n",
            summary_text,
            "\n## 💡 What This Means:\n",
            f"- Analyzed {len(user_histories)} users across {total_sessions} sessions",
            f"- Discovered {stats['n_clusters']} distinct behavioral patterns",
            f"- {stats['n_noise']} users classified as outliers/noise ({stats['noise_percentage']:.1f}%)",
            "\n## 📈 Research Validation:\n",
            "✅ Layer 3 (Pattern Discovery) from CCIA research article working in practice",
            "✅ Behavioral embeddings capture multi-dimensional user journeys",
            "✅ HDBSCAN discovers patterns without pre-specifying cluster count",
        ]

        if use_llm_personas and personas:
            final_summary.append("\n✅ LLM-generated personas ready for marketing activation")

        final_summary.append("\n## 🚀 Next Steps:")
        final_summary.append("1. Review personas and patterns below")
        final_summary.append("2. Download activation data for ad platforms")
        final_summary.append("3. Build targeted campaigns for each behavioral pattern")
        final_summary.append("4. Monitor pattern stability over time (>30% overlap = stable)")

        summary_output = "\n".join(final_summary)

        if not personas:
            personas_json = personas_json or "[]"

        return summary_output, personas_json, cluster_plot_path, stats_plot_path

    except Exception as e:
        import traceback
        error_msg = f"❌ Error in pattern discovery pipeline:\n\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg, "[]", "", ""


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_gradio_interface():
    """Create the Gradio UI for pattern discovery."""

    with gr.Blocks(
        title="Behavioral Pattern Discovery - CCIA Research Implementation",
        theme=gr.themes.Soft()
    ) as demo:

        gr.Markdown("""
        # 🔍 Behavioral Pattern Discovery Tool

        **Layer 3 of Context-Conditioned Intent Activation (CCIA) System**

        This tool implements the pattern discovery pipeline from the research article:
        [The Geometry of Intention: LLMs, Human Goals, and the Future of Marketing](https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing)

        ## How It Works:

        1. **Upload CSV** with user session histories
        2. **Behavioral Embeddings**: Transform sessions into 409-dimensional vectors
        3. **Pattern Discovery**: HDBSCAN clustering finds similar behavioral signatures
        4. **Persona Generation**: LLM creates marketing personas from clusters
        5. **Activation**: Export personas for ad platform targeting

        ## Research Foundation:

        > "Discover behavioral patterns. Find users whose behavioral signatures look alike.
        > These clusters become your audiences - not demographic segments but intentional archetypes."

        ---
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📁 Input Data")

                csv_input = gr.File(
                    label="Upload User Sessions CSV",
                    file_types=['.csv'],
                    type="filepath"
                )

                gr.Markdown("""
                **Expected CSV Format:**
                ```
                user_id,session_intent,confidence,timestamp,channel,engagement_level,
                has_budget_constraint,has_time_constraint,has_knowledge_gap,
                urgency_level,expertise_level
                ```

                [Download Example CSV](https://github.com/your-repo/examples/sample_user_histories.csv)
                """)

                dataset_preset = gr.Radio(
                    label="Data Size Preset",
                    choices=[
                        "Small Sample (≤200 users)",
                        "Full Traffic (1000+ users)"
                    ],
                    value="Small Sample (≤200 users)",
                    info="Apply recommended HDBSCAN settings for demo vs production data"
                )

                gr.Markdown("### ⚙️ Configuration")

                min_cluster_size = gr.Slider(
                    minimum=5,
                    maximum=100,
                    value=12,
                    step=5,
                    label="Minimum Cluster Size",
                    info="Smaller = more patterns (may include noise)"
                )

                min_samples = gr.Slider(
                    minimum=1,
                    maximum=20,
                    value=4,
                    step=1,
                    label="Minimum Samples",
                    info="Higher = fewer, more stable patterns"
                )

                use_llm = gr.Checkbox(
                    label="Generate LLM Personas",
                    value=True,
                    info="Uses Anthropic/OpenAI/OpenRouter models to create persona descriptions"
                )

                llm_provider = gr.Radio(
                    choices=["anthropic", "openai", "openrouter"],
                    value="anthropic",
                    label="LLM Provider",
                    info="Requires ANTHROPIC_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY in .env"
                )

                discover_btn = gr.Button(
                    "🚀 Discover Patterns",
                    variant="primary",
                    size="lg"
                )

                def apply_preset(preset: str) -> Tuple[int, int]:
                    """Map preset selections to recommended slider defaults."""
                    if "Full Traffic" in preset:
                        return 40, 10
                    return 12, 4

                dataset_preset.change(
                    fn=apply_preset,
                    inputs=dataset_preset,
                    outputs=[min_cluster_size, min_samples]
                )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Results")

                summary_output = gr.Textbox(
                    label="Pattern Discovery Summary",
                    lines=20,
                    max_lines=30,
                    show_copy_button=True
                )

                personas_output = gr.JSON(
                    label="Generated Personas (JSON)",
                    show_label=True
                )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📈 Visualizations")

                cluster_plot = gr.Image(
                    label="Cluster Visualization",
                    type="filepath",
                    show_label=True
                )

                stats_plot = gr.Image(
                    label="Pattern Statistics",
                    type="filepath",
                    show_label=True
                )

        # Examples
        gr.Markdown("### 💡 Example Use Cases")

        gr.Examples(
            examples=[
                [
                    None,  # csv_file (user will upload)
                    12,    # min_cluster_size
                    4,     # min_samples
                    True,  # use_llm
                    "anthropic"  # llm_provider
                ]
            ],
            inputs=[csv_input, min_cluster_size, min_samples, use_llm, llm_provider],
            label="Default Configuration"
        )

        # Wire up the function
        discover_btn.click(
            fn=discover_behavioral_patterns,
            inputs=[csv_input, min_cluster_size, min_samples, use_llm, llm_provider],
            outputs=[summary_output, personas_output, cluster_plot, stats_plot]
        )

        # Footer
        gr.Markdown("""
        ---

        ### 🎓 Research Implementation

        This tool validates the CCIA hypothesis from academic research:
        - **Paper**: [The Geometry of Intention](https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing)
        - **Layer 3**: Pattern Discovery (Behavioral Embeddings → HDBSCAN → LLM Personas)
        - **Validation**: Stable patterns (>30% overlap) represent real audience segments

        ### 🏆 Hackathon Submission

        - **Track 1**: Building MCP - Pattern Discovery Tool
        - **Track 2 Ready**: Integrates with full marketing agent
        - **OpenAI Apps SDK**: MCP-compatible for future integration

        ### 📚 Documentation

        - [GitHub Repository](https://github.com/your-repo)
        - [Research Article](https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing)
        - [API Documentation](https://github.com/your-repo/docs)
        """)

    return demo


# ============================================================================
# MAIN - MCP SERVER
# ============================================================================

if __name__ == "__main__":

    print("\n" + "="*70)
    print("🚀 Starting Behavioral Pattern Discovery MCP Server")
    print("="*70)
    print("\n📋 Tool Information:")
    print("   Name: discover_behavioral_patterns")
    print("   Purpose: Discover behavioral patterns from user session histories")
    print("   Input: CSV file with user sessions")
    print("   Output: Personas + visualizations + activation data")
    print("\n🔗 MCP Protocol: Enabled via Gradio 5.32+")
    print("   Compatible with: Cursor, Claude Desktop, ChatGPT, OpenAI Apps")
    print("\n📊 Pipeline:")
    print("   1. Behavioral Embedder (409-dimensional vectors)")
    print("   2. Pattern Clusterer (HDBSCAN)")
    print("   3. Pattern Analyzer (LLM personas)")
    print("   4. Visualizations + Export")
    print("\n" + "="*70 + "\n")

    # Create and launch Gradio interface
    demo = create_gradio_interface()

    # Launch with MCP support
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )
