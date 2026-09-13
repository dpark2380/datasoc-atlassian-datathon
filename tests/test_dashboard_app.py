import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).parent.parent


class DashboardAppTests(unittest.TestCase):
    def test_eda_is_organised_into_three_slide_ready_dataset_summaries(self):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=60).run()

        self.assertFalse(app.exception)
        metrics = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(metrics["Customer records"], "8,320")
        self.assertEqual(metrics["Ticket records"], "8,469")
        self.assertEqual(metrics["Usable customer-written text"], "0 fields")
        self.assertEqual(metrics["Impossible event order"], "49.3%")
        self.assertEqual(metrics["Usage observations"], "42,210")
        self.assertEqual(metrics["Tracked months"], "5")
        self.assertEqual(metrics["Jan–May usage persistence"], "0.82")
        self.assertEqual(metrics["Enterprise vs. Free integrations"], "5.3×")

        card_headings = {markdown.value for markdown in app.markdown}
        self.assertTrue(
            {"#### customers.csv", "#### customer_support_tickets.csv", "#### product_usage.csv"}
            <= card_headings
        )

    def test_risk_definitions_include_an_action_for_every_category(self):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=60).run()

        self.assertFalse(app.exception)
        rendered = "\n".join(markdown.value for markdown in app.markdown)
        self.assertIn("**Monitor Only — recommended action:** No action, track only.", rendered)
        self.assertIn(
            "**New & Struggling — recommended action:** Milestone-tracked onboarding review",
            rendered,
        )
        self.assertIn(
            "**Established & Low Engagement — recommended action:** Automated feature-specific play",
            rendered,
        )
        self.assertIn(
            "**High-Value Disengaged — recommended action:** Executive Business Review",
            rendered,
        )


if __name__ == "__main__":
    unittest.main()
