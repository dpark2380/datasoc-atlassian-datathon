import unittest

import pandas as pd

from analysis.dashboard_metrics import build_eda_metrics


class DashboardMetricsTests(unittest.TestCase):
    def setUp(self):
        self.customers = pd.DataFrame(
            {
                "Customer ID": ["C1", "C2"],
                "Plan Type": ["Free", "Enterprise"],
            }
        )
        self.tickets = pd.DataFrame(
            {
                "Ticket ID": [1, 2, 3],
                "First Response Time": [
                    "2023-06-01 10:00:00",
                    "2023-06-01 10:00:00",
                    "2023-06-01 10:00:00",
                ],
                "Time to Resolution": [
                    "2023-06-01 09:00:00",
                    "2023-06-01 12:00:00",
                    None,
                ],
            }
        )
        self.usage = pd.DataFrame(
            {
                "Customer ID": ["C1", "C1", "C2", "C2"],
                "Product": ["Loom", "Loom", "Jira", "Jira"],
                "Month": ["2023-01", "2023-05", "2023-01", "2023-05"],
                "Active Days": [2.0, 4.0, 8.0, 10.0],
                "Integrations Used": [1.0, 1.0, 5.0, 7.0],
            }
        )

    def test_eda_metrics_capture_pitch_evidence(self):
        metrics = build_eda_metrics(self.customers, self.tickets, self.usage)

        self.assertEqual(metrics["month_count"], 2)
        self.assertEqual(metrics["resolved_ticket_count"], 2)
        self.assertAlmostEqual(metrics["impossible_order_rate"], 0.5)
        self.assertAlmostEqual(metrics["integration_tier_ratio"], 6.0)
        self.assertAlmostEqual(metrics["active_days_persistence"], 1.0)

    def test_eda_metrics_exposes_ordered_plan_and_product_signals(self):
        metrics = build_eda_metrics(self.customers, self.tickets, self.usage)

        self.assertEqual(metrics["usage_by_plan"]["Plan Type"].tolist(), ["Free", "Enterprise"])
        self.assertEqual(metrics["usage_by_product"]["Product"].tolist(), ["Loom", "Jira"])
        self.assertEqual(metrics["usage_by_plan"]["Active Days"].tolist(), [3.0, 9.0])
        self.assertEqual(metrics["usage_by_product"]["Active Days"].tolist(), [3.0, 9.0])


if __name__ == "__main__":
    unittest.main()
