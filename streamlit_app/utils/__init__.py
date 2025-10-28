"""
Utility modules for the Gender in Video Games Streamlit app
"""

from .data_loader import (
    load_data,
    get_data_summary,
    filter_data_by_year,
    filter_data_by_gender,
    get_character_stats,
    get_game_stats
)

from .viz_utils import (
    create_gender_bar_chart,
    create_temporal_line_chart,
    create_distribution_histogram,
    create_box_plot,
    create_scatter_plot,
    create_pie_chart,
    create_heatmap,
    create_grouped_bar_chart,
    create_stacked_bar_chart,
    create_percentage_stacked_bar,
    format_percentage,
    format_count,
    display_metric_card,
    display_insight_box,
    create_correlation_matrix,
    COLORS
)

__all__ = [
    # Data loading
    'load_data',
    'get_data_summary',
    'filter_data_by_year',
    'filter_data_by_gender',
    'get_character_stats',
    'get_game_stats',
    
    # Visualizations
    'create_gender_bar_chart',
    'create_temporal_line_chart',
    'create_distribution_histogram',
    'create_box_plot',
    'create_scatter_plot',
    'create_pie_chart',
    'create_heatmap',
    'create_grouped_bar_chart',
    'create_stacked_bar_chart',
    'create_percentage_stacked_bar',
    'format_percentage',
    'format_count',
    'display_metric_card',
    'display_insight_box',
    'create_correlation_matrix',
    'COLORS'
]
