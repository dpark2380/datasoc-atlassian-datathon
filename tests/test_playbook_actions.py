import unittest

from analysis.eda import recommended_action


PRODUCTS = ["Jira", "Confluence", "Trello", "Bitbucket", "Loom"]
CATEGORIES = [
    "Monitor Only",
    "New & Struggling",
    "Established & Low Engagement",
    "High-Value Disengaged",
]


class PlaybookActionTests(unittest.TestCase):
    def test_each_category_has_a_distinct_action_for_every_product(self):
        for category in CATEGORIES:
            actions = {
                product: recommended_action(category, product) for product in PRODUCTS
            }

            self.assertEqual(len(set(actions.values())), len(PRODUCTS))
            for product, action in actions.items():
                self.assertIn(product, action)

    def test_actions_name_concrete_product_workflows(self):
        self.assertIn("production project", recommended_action("New & Struggling", "Jira"))
        self.assertIn(
            "team space", recommended_action("New & Struggling", "Confluence")
        )
        self.assertIn(
            "Butler automation",
            recommended_action("Established & Low Engagement", "Trello"),
        )
        self.assertIn(
            "pull-request throughput",
            recommended_action("High-Value Disengaged", "Bitbucket"),
        )
        self.assertIn(
            "async update",
            recommended_action("Established & Low Engagement", "Loom"),
        )

    def test_unknown_product_or_category_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, "Unknown product"):
            recommended_action("Monitor Only", "Unknown")
        with self.assertRaisesRegex(ValueError, "Unknown risk category"):
            recommended_action("Unknown", "Jira")


if __name__ == "__main__":
    unittest.main()
