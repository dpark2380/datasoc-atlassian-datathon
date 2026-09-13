import unittest
from pathlib import Path
from unittest.mock import patch

import plotly.graph_objects as go

from app_pages.chart_styling import apply_white_chart_background, render_plotly_chart


class ChartStylingTests(unittest.TestCase):
    def test_chart_canvas_and_plot_area_are_opaque_white(self):
        figure = go.Figure(go.Bar(x=["A"], y=[1]))
        figure.update_layout(
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
        )

        styled = apply_white_chart_background(figure)

        self.assertIs(styled, figure)
        self.assertEqual(styled.layout.paper_bgcolor, "#FFFFFF")
        self.assertEqual(styled.layout.plot_bgcolor, "#FFFFFF")

    @patch("app_pages.chart_styling.st.plotly_chart")
    def test_renderer_disables_streamlit_theme_override(self, plotly_chart):
        figure = go.Figure(go.Bar(x=["A"], y=[1]))

        render_plotly_chart(figure, width="stretch", key="example")

        rendered_figure = plotly_chart.call_args.args[0]
        self.assertEqual(rendered_figure.layout.paper_bgcolor, "#FFFFFF")
        self.assertEqual(rendered_figure.layout.plot_bgcolor, "#FFFFFF")
        self.assertIsNone(plotly_chart.call_args.kwargs["theme"])

    def test_every_chart_page_uses_the_shared_white_renderer(self):
        app_pages = Path(__file__).parent.parent / "app_pages"
        direct_renderers = []
        for page in app_pages.glob("*.py"):
            if page.name == "chart_styling.py":
                continue
            if "st.plotly_chart(" in page.read_text(encoding="utf-8"):
                direct_renderers.append(page.name)

        self.assertEqual(direct_renderers, [])


if __name__ == "__main__":
    unittest.main()
