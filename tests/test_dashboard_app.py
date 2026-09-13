import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).parent.parent


class DashboardAppTests(unittest.TestCase):
    def test_eda_surfaces_the_pitch_evidence(self):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=60).run()

        self.assertFalse(app.exception)
        metrics = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(metrics["Usable customer-written text"], "0 fields")
        self.assertEqual(metrics["Impossible event order"], "49.3%")
        self.assertEqual(metrics["Jan–May usage persistence"], "0.82")
        self.assertEqual(metrics["Enterprise vs. Free integrations"], "5.3×")

        file_summary = app.dataframe[0].value
        self.assertEqual(
            file_summary["File"].tolist(),
            ["customers.csv", "customer_support_tickets.csv", "product_usage.csv"],
        )


if __name__ == "__main__":
    unittest.main()
