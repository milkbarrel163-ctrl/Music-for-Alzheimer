"""
Small-N Music Therapy Analysis Script
Statistical analysis and visualization for Traditional Chinese Music therapy pilot study
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import wilcoxon, mannwhitneyu
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from typing import Dict, List, Tuple, Optional
import warnings
from pathlib import Path
import json
from datetime import datetime, timedelta

# Set plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
warnings.filterwarnings('ignore')

class SmallNAnalyzer:
    """Statistical analyzer designed for small sample sizes and pilot studies."""

    def __init__(self, session_data: pd.DataFrame):
        """
        Initialize analyzer with session data.

        Args:
            session_data: DataFrame with columns including engagement_score,
                         mood_response_score, agitation_score, condition_type, etc.
        """
        self.data = session_data.copy()
        self.results = {}

        # Ensure required columns exist
        required_cols = ['engagement_score', 'mood_response_score', 'agitation_score', 'condition_type']
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Clean and prepare data
        self._prepare_data()

    def _prepare_data(self):
        """Clean and prepare data for analysis."""

        # Remove any invalid scores
        score_cols = ['engagement_score', 'mood_response_score', 'agitation_score']
        for col in score_cols:
            self.data = self.data[(self.data[col] >= 1) & (self.data[col] <= 10)]

        # Create condition indicators
        self.data['is_original'] = (self.data['condition_type'] == 'original').astype(int)
        self.data['is_generated'] = (self.data['condition_type'] == 'generated').astype(int)

        # Calculate composite scores
        self.data['positive_response'] = (
            self.data['engagement_score'] +
            self.data['mood_response_score'] +
            (11 - self.data['agitation_score'])  # Invert agitation (lower is better)
        ) / 3

        print(f"Data prepared: {len(self.data)} observations from {self.data['participant_id'].nunique()} participants")

    def calculate_effect_sizes(self) -> Dict:
        """Calculate effect sizes appropriate for small samples."""

        effects = {}

        # Separate original and generated conditions
        original_data = self.data[self.data['condition_type'] == 'original']
        generated_data = self.data[self.data['condition_type'] == 'generated']

        if len(original_data) == 0 or len(generated_data) == 0:
            print("Warning: Cannot calculate effect sizes - missing one condition type")
            return {}

        score_measures = {
            'engagement': 'engagement_score',
            'mood_response': 'mood_response_score',
            'agitation': 'agitation_score',
            'positive_response': 'positive_response'
        }

        for measure_name, column in score_measures.items():
            original_scores = original_data[column].values
            generated_scores = generated_data[column].values

            # Cohen's d (with small sample correction)
            pooled_std = np.sqrt(((len(original_scores) - 1) * np.var(original_scores, ddof=1) +
                                 (len(generated_scores) - 1) * np.var(generated_scores, ddof=1)) /
                                (len(original_scores) + len(generated_scores) - 2))

            if pooled_std > 0:
                cohens_d = (np.mean(generated_scores) - np.mean(original_scores)) / pooled_std

                # Hedges' g (bias-corrected for small samples)
                correction_factor = 1 - (3 / (4 * (len(original_scores) + len(generated_scores)) - 9))
                hedges_g = cohens_d * correction_factor
            else:
                cohens_d = 0
                hedges_g = 0

            # Cliff's Delta (robust, non-parametric effect size)
            cliffs_delta = self._calculate_cliffs_delta(original_scores, generated_scores)

            effects[measure_name] = {
                'cohens_d': cohens_d,
                'hedges_g': hedges_g,
                'cliffs_delta': cliffs_delta,
                'interpretation': self._interpret_effect_size(abs(hedges_g))
            }

        self.results['effect_sizes'] = effects
        return effects

    def _calculate_cliffs_delta(self, group1: np.ndarray, group2: np.ndarray) -> float:
        """Calculate Cliff's Delta effect size."""

        if len(group1) == 0 or len(group2) == 0:
            return 0

        # Count pairs where group2 > group1, group2 < group1
        dominance = 0
        for x in group1:
            for y in group2:
                if y > x:
                    dominance += 1
                elif y < x:
                    dominance -= 1

        # Normalize by total number of pairs
        total_pairs = len(group1) * len(group2)
        return dominance / total_pairs if total_pairs > 0 else 0

    def _interpret_effect_size(self, effect_size: float) -> str:
        """Interpret effect size magnitude."""
        if effect_size < 0.2:
            return "negligible"
        elif effect_size < 0.5:
            return "small"
        elif effect_size < 0.8:
            return "medium"
        else:
            return "large"

    def perform_statistical_tests(self) -> Dict:
        """Perform appropriate statistical tests for small samples."""

        tests = {}

        # Check if we have paired or independent data
        # For within-subject design, use paired tests
        participant_counts = self.data.groupby(['participant_id', 'condition_type']).size()
        is_paired = all(participant_counts >= 1)  # Each participant has both conditions

        score_measures = ['engagement_score', 'mood_response_score', 'agitation_score', 'positive_response']

        for measure in score_measures:
            original_scores = self.data[self.data['condition_type'] == 'original'][measure]
            generated_scores = self.data[self.data['condition_type'] == 'generated'][measure]

            if len(original_scores) == 0 or len(generated_scores) == 0:
                continue

            test_result = {}

            if is_paired and len(original_scores) == len(generated_scores):
                # Paired analysis - Wilcoxon signed-rank test
                try:
                    statistic, p_value = wilcoxon(generated_scores, original_scores,
                                                alternative='two-sided')
                    test_result = {
                        'test_type': 'wilcoxon_signed_rank',
                        'statistic': statistic,
                        'p_value': p_value,
                        'significant': p_value < 0.05,
                        'n_pairs': len(original_scores)
                    }
                except ValueError as e:
                    print(f"Warning: Wilcoxon test failed for {measure}: {e}")
                    continue
            else:
                # Independent samples - Mann-Whitney U test
                try:
                    statistic, p_value = mannwhitneyu(generated_scores, original_scores,
                                                    alternative='two-sided')
                    test_result = {
                        'test_type': 'mann_whitney_u',
                        'statistic': statistic,
                        'p_value': p_value,
                        'significant': p_value < 0.05,
                        'n_original': len(original_scores),
                        'n_generated': len(generated_scores)
                    }
                except ValueError as e:
                    print(f"Warning: Mann-Whitney test failed for {measure}: {e}")
                    continue

            # Add descriptive statistics
            test_result.update({
                'original_median': np.median(original_scores),
                'generated_median': np.median(generated_scores),
                'original_mean': np.mean(original_scores),
                'generated_mean': np.mean(generated_scores),
                'original_std': np.std(original_scores, ddof=1),
                'generated_std': np.std(generated_scores, ddof=1)
            })

            tests[measure] = test_result

        self.results['statistical_tests'] = tests
        return tests

    def analyze_individual_patterns(self) -> Dict:
        """Analyze individual participant patterns."""

        patterns = {}

        for participant in self.data['participant_id'].unique():
            participant_data = self.data[self.data['participant_id'] == participant]

            # Calculate individual preferences
            original_scores = participant_data[participant_data['condition_type'] == 'original']
            generated_scores = participant_data[participant_data['condition_type'] == 'generated']

            pattern = {
                'total_sessions': participant_data['session_id'].nunique(),
                'total_tracks': len(participant_data),
                'original_tracks': len(original_scores),
                'generated_tracks': len(generated_scores)
            }

            if len(original_scores) > 0 and len(generated_scores) > 0:
                # Individual effect sizes
                pattern['individual_preference'] = {
                    'engagement_diff': generated_scores['engagement_score'].mean() - original_scores['engagement_score'].mean(),
                    'mood_diff': generated_scores['mood_response_score'].mean() - original_scores['mood_response_score'].mean(),
                    'agitation_diff': original_scores['agitation_score'].mean() - generated_scores['agitation_score'].mean(),  # Lower is better
                }

                # Preferred condition
                positive_response_orig = original_scores['positive_response'].mean()
                positive_response_gen = generated_scores['positive_response'].mean()
                pattern['preferred_condition'] = 'generated' if positive_response_gen > positive_response_orig else 'original'
                pattern['preference_strength'] = abs(positive_response_gen - positive_response_orig)

            # Favorite musical characteristics
            if len(participant_data) > 0:
                # Most engaging era/mood combinations
                era_engagement = participant_data.groupby('era')['engagement_score'].mean()
                mood_engagement = participant_data.groupby('mood')['engagement_score'].mean()

                pattern['favorite_era'] = era_engagement.idxmax() if len(era_engagement) > 0 else 'unknown'
                pattern['favorite_mood'] = mood_engagement.idxmax() if len(mood_engagement) > 0 else 'unknown'

            patterns[participant] = pattern

        self.results['individual_patterns'] = patterns
        return patterns

    def create_visualizations(self, save_path: str = "analysis_plots") -> Dict:
        """Create comprehensive visualizations for the analysis."""

        save_path = Path(save_path)
        save_path.mkdir(exist_ok=True)

        plots = {}

        # 1. Condition Comparison Plot
        fig_comparison = self._create_condition_comparison_plot()
        fig_comparison.write_html(save_path / "condition_comparison.html")
        plots['condition_comparison'] = str(save_path / "condition_comparison.html")

        # 2. Individual Trajectories
        fig_trajectories = self._create_individual_trajectories_plot()
        fig_trajectories.write_html(save_path / "individual_trajectories.html")
        plots['individual_trajectories'] = str(save_path / "individual_trajectories.html")

        # 3. Effect Sizes Visualization
        if 'effect_sizes' in self.results:
            fig_effects = self._create_effect_sizes_plot()
            fig_effects.write_html(save_path / "effect_sizes.html")
            plots['effect_sizes'] = str(save_path / "effect_sizes.html")

        # 4. Musical Characteristics Analysis
        fig_musical = self._create_musical_characteristics_plot()
        fig_musical.write_html(save_path / "musical_characteristics.html")
        plots['musical_characteristics'] = str(save_path / "musical_characteristics.html")

        # 5. Time Series Analysis
        if 'session_date' in self.data.columns:
            fig_timeseries = self._create_time_series_plot()
            fig_timeseries.write_html(save_path / "time_series.html")
            plots['time_series'] = str(save_path / "time_series.html")

        return plots

    def _create_condition_comparison_plot(self):
        """Create box plots comparing original vs generated conditions."""

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Engagement Score', 'Mood Response Score',
                          'Agitation Score', 'Overall Positive Response'),
            vertical_spacing=0.12
        )

        measures = [
            ('engagement_score', 'Engagement'),
            ('mood_response_score', 'Mood Response'),
            ('agitation_score', 'Agitation'),
            ('positive_response', 'Positive Response')
        ]

        positions = [(1,1), (1,2), (2,1), (2,2)]

        for (measure, title), (row, col) in zip(measures, positions):

            # Box plots for each condition
            original_data = self.data[self.data['condition_type'] == 'original'][measure]
            generated_data = self.data[self.data['condition_type'] == 'generated'][measure]

            fig.add_trace(
                go.Box(y=original_data, name='Original',
                      boxpoints='all', jitter=0.3, pointpos=-1.8,
                      marker_color='lightblue', showlegend=(row==1 and col==1)),
                row=row, col=col
            )

            fig.add_trace(
                go.Box(y=generated_data, name='AI Generated',
                      boxpoints='all', jitter=0.3, pointpos=1.8,
                      marker_color='lightcoral', showlegend=(row==1 and col==1)),
                row=row, col=col
            )

            # Add statistical test results if available
            if 'statistical_tests' in self.results and measure in self.results['statistical_tests']:
                test_result = self.results['statistical_tests'][measure]
                p_val = test_result['p_value']
                significance = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"

                fig.add_annotation(
                    x=0.5, y=max(original_data.max(), generated_data.max()) + 0.5,
                    text=f"p = {p_val:.3f} {significance}",
                    showarrow=False,
                    row=row, col=col
                )

        fig.update_layout(
            title="Comparison of Original vs AI-Generated Traditional Chinese Music",
            height=600,
            showlegend=True
        )

        return fig

    def _create_individual_trajectories_plot(self):
        """Create individual participant trajectory plots."""

        participants = self.data['participant_id'].unique()

        fig = make_subplots(
            rows=len(participants), cols=1,
            subplot_titles=[f"Participant {p}" for p in participants],
            vertical_spacing=0.1
        )

        for i, participant in enumerate(participants, 1):
            participant_data = self.data[self.data['participant_id'] == participant].copy()
            participant_data = participant_data.sort_values(['session_date', 'track_order'])

            # Create track index for x-axis
            participant_data['track_index'] = range(len(participant_data))

            # Plot engagement over time
            colors = ['blue' if cond == 'original' else 'red'
                     for cond in participant_data['condition_type']]

            fig.add_trace(
                go.Scatter(
                    x=participant_data['track_index'],
                    y=participant_data['engagement_score'],
                    mode='lines+markers',
                    name=f'{participant} Engagement',
                    line=dict(color='blue'),
                    marker=dict(color=colors, size=8),
                    showlegend=(i==1)
                ),
                row=i, col=1
            )

            # Add condition markers
            for j, (idx, row) in enumerate(participant_data.iterrows()):
                symbol = 'circle' if row['condition_type'] == 'original' else 'square'
                fig.add_trace(
                    go.Scatter(
                        x=[row['track_index']],
                        y=[row['engagement_score']],
                        mode='markers',
                        marker=dict(
                            symbol=symbol,
                            size=10,
                            color='blue' if row['condition_type'] == 'original' else 'red'
                        ),
                        name='Original' if row['condition_type'] == 'original' and i==1 and j==0 else 'Generated' if row['condition_type'] == 'generated' and i==1 and j==0 else '',
                        showlegend=(i==1 and j==0) or (i==1 and j==1)
                    ),
                    row=i, col=1
                )

        fig.update_layout(
            title="Individual Participant Trajectories Over Time",
            height=200 * len(participants),
            xaxis_title="Track Number"
        )

        return fig

    def _create_effect_sizes_plot(self):
        """Create effect sizes visualization."""

        if 'effect_sizes' not in self.results:
            return go.Figure()

        effects = self.results['effect_sizes']

        measures = list(effects.keys())
        cliffs_deltas = [effects[m]['cliffs_delta'] for m in measures]
        hedges_gs = [effects[m]['hedges_g'] for m in measures]
        interpretations = [effects[m]['interpretation'] for m in measures]

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Cliff's Delta (Robust)", "Hedges' g (Corrected)")
        )

        # Cliff's Delta
        colors = ['green' if d > 0 else 'red' for d in cliffs_deltas]
        fig.add_trace(
            go.Bar(x=measures, y=cliffs_deltas, name="Cliff's Delta",
                  marker_color=colors, showlegend=False),
            row=1, col=1
        )

        # Hedges' g
        colors = ['green' if g > 0 else 'red' for g in hedges_gs]
        fig.add_trace(
            go.Bar(x=measures, y=hedges_gs, name="Hedges' g",
                  marker_color=colors, showlegend=False),
            row=1, col=2
        )

        # Add interpretation annotations
        for i, (measure, interpretation) in enumerate(zip(measures, interpretations)):
            fig.add_annotation(
                x=i, y=hedges_gs[i] + 0.1,
                text=interpretation,
                showarrow=False,
                row=1, col=2
            )

        fig.update_layout(
            title="Effect Sizes: AI-Generated vs Original Music",
            height=400
        )

        return fig

    def _create_musical_characteristics_plot(self):
        """Analyze musical characteristics (era, mood, instruments) effects."""

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Engagement by Era', 'Engagement by Mood',
                          'Era Preferences by Condition', 'Mood Preferences by Condition')
        )

        # Engagement by Era
        if 'era' in self.data.columns:
            era_engagement = self.data.groupby('era')['engagement_score'].agg(['mean', 'std', 'count'])
            fig.add_trace(
                go.Bar(x=era_engagement.index, y=era_engagement['mean'],
                      error_y=dict(type='data', array=era_engagement['std']),
                      name='Era Engagement', showlegend=False),
                row=1, col=1
            )

        # Engagement by Mood
        if 'mood' in self.data.columns:
            mood_engagement = self.data.groupby('mood')['engagement_score'].agg(['mean', 'std', 'count'])
            fig.add_trace(
                go.Bar(x=mood_engagement.index, y=mood_engagement['mean'],
                      error_y=dict(type='data', array=mood_engagement['std']),
                      name='Mood Engagement', showlegend=False),
                row=1, col=2
            )

        # Era by Condition
        if 'era' in self.data.columns:
            era_condition = pd.crosstab(self.data['era'], self.data['condition_type'], normalize='index') * 100

            fig.add_trace(
                go.Bar(x=era_condition.index, y=era_condition.get('original', []),
                      name='Original', marker_color='lightblue'),
                row=2, col=1
            )
            fig.add_trace(
                go.Bar(x=era_condition.index, y=era_condition.get('generated', []),
                      name='Generated', marker_color='lightcoral'),
                row=2, col=1
            )

        # Mood by Condition
        if 'mood' in self.data.columns:
            mood_condition = pd.crosstab(self.data['mood'], self.data['condition_type'], normalize='index') * 100

            fig.add_trace(
                go.Bar(x=mood_condition.index, y=mood_condition.get('original', []),
                      name='Original', marker_color='lightblue', showlegend=False),
                row=2, col=2
            )
            fig.add_trace(
                go.Bar(x=mood_condition.index, y=mood_condition.get('generated', []),
                      name='Generated', marker_color='lightcoral', showlegend=False),
                row=2, col=2
            )

        fig.update_layout(
            title="Musical Characteristics Analysis",
            height=600
        )

        return fig

    def _create_time_series_plot(self):
        """Create time series analysis of responses."""

        # Convert session_date to datetime
        self.data['session_date'] = pd.to_datetime(self.data['session_date'])

        # Group by date and condition
        daily_stats = self.data.groupby(['session_date', 'condition_type']).agg({
            'engagement_score': ['mean', 'std'],
            'mood_response_score': ['mean', 'std'],
            'agitation_score': ['mean', 'std']
        }).reset_index()

        # Flatten column names
        daily_stats.columns = ['_'.join(col).strip() if col[1] else col[0] for col in daily_stats.columns]

        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Engagement Over Time', 'Mood Response Over Time', 'Agitation Over Time'),
            vertical_spacing=0.1
        )

        measures = [
            ('engagement_score_mean', 'engagement_score_std', 'Engagement'),
            ('mood_response_score_mean', 'mood_response_score_std', 'Mood Response'),
            ('agitation_score_mean', 'agitation_score_std', 'Agitation')
        ]

        for i, (mean_col, std_col, title) in enumerate(measures, 1):

            for condition in ['original', 'generated']:
                condition_data = daily_stats[daily_stats['condition_type_'] == condition]

                if len(condition_data) > 0:
                    fig.add_trace(
                        go.Scatter(
                            x=condition_data['session_date_'],
                            y=condition_data[mean_col],
                            error_y=dict(type='data', array=condition_data[std_col]),
                            mode='lines+markers',
                            name=f'{condition.capitalize()}',
                            showlegend=(i==1)
                        ),
                        row=i, col=1
                    )

        fig.update_layout(
            title="Response Trends Over Time",
            height=800,
            xaxis_title="Date"
        )

        return fig

    def generate_report(self, save_path: str = "analysis_report.html") -> str:
        """Generate a comprehensive HTML report."""

        # Perform all analyses
        effect_sizes = self.calculate_effect_sizes()
        statistical_tests = self.perform_statistical_tests()
        individual_patterns = self.analyze_individual_patterns()

        # Generate plots
        plots = self.create_visualizations()

        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Traditional Chinese Music Therapy Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 10px; }}
                .section {{ margin: 30px 0; }}
                .result {{ background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                .warning {{ background-color: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ff9800; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Traditional Chinese Music Therapy Analysis Report</h1>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Total Observations:</strong> {len(self.data)}</p>
                <p><strong>Participants:</strong> {self.data['participant_id'].nunique()}</p>
                <p><strong>Sessions:</strong> {self.data['session_id'].nunique()}</p>
            </div>
        """

        # Add statistical test results
        if statistical_tests:
            html_content += """
            <div class="section">
                <h2>Statistical Test Results</h2>
                <table>
                    <tr><th>Measure</th><th>Test</th><th>p-value</th><th>Significant</th><th>Original Mean</th><th>Generated Mean</th></tr>
            """

            for measure, result in statistical_tests.items():
                significance = "Yes" if result['significant'] else "No"
                html_content += f"""
                    <tr>
                        <td>{measure.replace('_', ' ').title()}</td>
                        <td>{result['test_type'].replace('_', ' ').title()}</td>
                        <td>{result['p_value']:.4f}</td>
                        <td>{significance}</td>
                        <td>{result['original_mean']:.2f}</td>
                        <td>{result['generated_mean']:.2f}</td>
                    </tr>
                """

            html_content += "</table></div>"

        # Add effect sizes
        if effect_sizes:
            html_content += """
            <div class="section">
                <h2>Effect Sizes</h2>
                <table>
                    <tr><th>Measure</th><th>Cliff's Delta</th><th>Hedges' g</th><th>Interpretation</th></tr>
            """

            for measure, result in effect_sizes.items():
                html_content += f"""
                    <tr>
                        <td>{measure.replace('_', ' ').title()}</td>
                        <td>{result['cliffs_delta']:.3f}</td>
                        <td>{result['hedges_g']:.3f}</td>
                        <td>{result['interpretation'].title()}</td>
                    </tr>
                """

            html_content += "</table></div>"

        # Add individual patterns summary
        if individual_patterns:
            html_content += """
            <div class="section">
                <h2>Individual Participant Patterns</h2>
            """

            for participant, pattern in individual_patterns.items():
                preference = pattern.get('preferred_condition', 'Unknown')
                strength = pattern.get('preference_strength', 0)

                html_content += f"""
                <div class="result">
                    <h3>Participant {participant}</h3>
                    <p><strong>Total Sessions:</strong> {pattern['total_sessions']}</p>
                    <p><strong>Total Tracks:</strong> {pattern['total_tracks']}</p>
                    <p><strong>Preferred Condition:</strong> {preference.title()} (strength: {strength:.2f})</p>
                    <p><strong>Favorite Era:</strong> {pattern.get('favorite_era', 'Unknown')}</p>
                    <p><strong>Favorite Mood:</strong> {pattern.get('favorite_mood', 'Unknown')}</p>
                </div>
                """

            html_content += "</div>"

        # Add interpretation and recommendations
        html_content += f"""
        <div class="section">
            <h2>Key Findings and Recommendations</h2>
            {self._generate_interpretation()}
        </div>

        <div class="section">
            <h2>Visualizations</h2>
            <p>Interactive plots have been saved to the following files:</p>
            <ul>
        """

        for plot_name, plot_path in plots.items():
            html_content += f"<li><a href='{plot_path}'>{plot_name.replace('_', ' ').title()}</a></li>"

        html_content += """
            </ul>
        </div>

        </body>
        </html>
        """

        # Save report
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Report saved to {save_path}")
        return save_path

    def _generate_interpretation(self) -> str:
        """Generate interpretation of results."""

        interpretation = []

        # Sample size considerations
        n_total = len(self.data)
        n_participants = self.data['participant_id'].nunique()

        if n_participants < 5:
            interpretation.append(f"""
            <div class="warning">
                <strong>Sample Size Note:</strong> This is a small pilot study with {n_participants} participants.
                Results should be interpreted as exploratory and preliminary. Larger samples would be needed
                for definitive conclusions.
            </div>
            """)

        # Effect size interpretation
        if 'effect_sizes' in self.results:
            engagement_effect = self.results['effect_sizes'].get('engagement', {})
            if engagement_effect:
                cliffs_d = engagement_effect['cliffs_delta']
                interpretation_text = engagement_effect['interpretation']

                if cliffs_d > 0.1:
                    interpretation.append(f"""
                    <div class="result">
                        <strong>Positive Finding:</strong> AI-generated music showed a {interpretation_text}
                        positive effect on engagement (Cliff's Δ = {cliffs_d:.3f}). This suggests that
                        culturally-tailored AI variations may enhance traditional music therapy.
                    </div>
                    """)
                elif cliffs_d < -0.1:
                    interpretation.append(f"""
                    <div class="warning">
                        <strong>Original Music Preference:</strong> Traditional original music showed better
                        engagement (Cliff's Δ = {cliffs_d:.3f}). This suggests authentic traditional music
                        may be preferred for this population.
                    </div>
                    """)

        # Individual differences
        if 'individual_patterns' in self.results:
            patterns = self.results['individual_patterns']
            generated_preferrers = sum(1 for p in patterns.values()
                                     if p.get('preferred_condition') == 'generated')
            total_with_preference = sum(1 for p in patterns.values()
                                      if 'preferred_condition' in p)

            if total_with_preference > 0:
                pct_generated = (generated_preferrers / total_with_preference) * 100
                interpretation.append(f"""
                <div class="result">
                    <strong>Individual Differences:</strong> {pct_generated:.1f}% of participants showed
                    preference for AI-generated variations. This highlights the importance of
                    personalized approaches in music therapy.
                </div>
                """)

        # Recommendations
        interpretation.append("""
        <div class="result">
            <strong>Recommendations for Future Research:</strong>
            <ul>
                <li>Increase sample size to 15-20 participants for more robust statistical power</li>
                <li>Conduct longer-term follow-up to assess sustained effects</li>
                <li>Explore individual factors that predict preference for AI vs. original music</li>
                <li>Investigate specific musical elements that drive engagement</li>
                <li>Consider cultural background and musical familiarity as covariates</li>
            </ul>
        </div>
        """)

        return ''.join(interpretation)

# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)

    sample_data = []
    participants = ['P001', 'P002', 'P003']

    for participant in participants:
        for session in range(3):
            for track in range(6):
                # Simulate data with some participant-specific preferences
                base_engagement = np.random.normal(6, 1.5)
                base_mood = np.random.normal(6, 1.5)
                base_agitation = np.random.normal(4, 1.2)

                condition = 'original' if track % 2 == 0 else 'generated'

                # Add condition effects (some participants prefer generated)
                if participant == 'P002' and condition == 'generated':
                    base_engagement += 1.5
                    base_mood += 1.2
                    base_agitation -= 0.8

                sample_data.append({
                    'participant_id': participant,
                    'session_id': f'{participant}_S{session+1}',
                    'session_date': f'2024-0{session+1}-15',
                    'track_id': f'track_{track+1}',
                    'track_title': f'Track {track+1}',
                    'condition_type': condition,
                    'era': np.random.choice(['1930s', '1940s', '1950s', '1960s']),
                    'mood': np.random.choice(['nostalgic', 'peaceful', 'joyful']),
                    'engagement_score': np.clip(base_engagement, 1, 10),
                    'mood_response_score': np.clip(base_mood, 1, 10),
                    'agitation_score': np.clip(base_agitation, 1, 10),
                    'caregiver_notes': 'Sample observation'
                })

    df = pd.DataFrame(sample_data)

    # Run analysis
    analyzer = SmallNAnalyzer(df)

    # Generate full report
    report_path = analyzer.generate_report("sample_analysis_report.html")
    print(f"Analysis complete! Report saved to: {report_path}")

    # Print key results
    print("\nKey Results:")
    print(f"Total observations: {len(df)}")
    print(f"Participants: {df['participant_id'].nunique()}")

    if 'statistical_tests' in analyzer.results:
        for measure, result in analyzer.results['statistical_tests'].items():
            print(f"{measure}: p = {result['p_value']:.4f}")