"""Shared rendering rules for Plotly charts in the Streamlit app."""

from typing import Any

import streamlit as st


def apply_white_chart_background(figure: Any) -> Any:
    """Give both layers of a Plotly figure an opaque white background."""
    figure.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
    return figure


def render_plotly_chart(figure: Any, **kwargs: Any) -> Any:
    """Render a white Plotly figure without Streamlit's transparent override."""
    return st.plotly_chart(
        apply_white_chart_background(figure),
        theme=None,
        **kwargs,
    )
