import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).parent.parent


class DeckOutlineAppTests(unittest.TestCase):
    def _load_deck_page(self):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=60).run()
        app.switch_page("app_pages/deck_outline.py").run()
        self.assertFalse(app.exception)
        return app

    def test_deck_follows_the_sample_fifteen_slide_story_arc(self):
        app = self._load_deck_page()

        slides = [expander for expander in app.expander if expander.label[0].isdigit()]
        slide_titles = [expander.label.split("  ·  ")[0] for expander in slides]
        self.assertEqual(
            slide_titles,
            [
                "1. From Noise to Next Best Action",
                "2. Problem Statement",
                "3. Why Should Atlassian Care?",
                "4. The Finding That Changed Our Approach",
                "5. What Each Dataset Can Tell Us",
                "6. Why the Ticket File Cannot Measure Sentiment",
                "7. The Real Signal: Product Usage",
                "8. How We Define Risk",
                "9. Results: Who Needs Action?",
                "10. Validation: Can We Trust the Result?",
                "11. Customer Scenarios: Score to Action",
                "12. Method Selection",
                "13. Strategies for Retention",
                "14. Strategies for Value Protection and Expansion",
                "15. Introducing the Customer Risk Playbook",
            ],
        )

        deck_doc = (ROOT / "docs" / "deck-outline.md").read_text(encoding="utf-8")
        for slide, title in zip(slides, slide_titles):
            self.assertIn(f"## Slide {title}", deck_doc)
            self.assertIn("**Figure to add**", [markdown.value for markdown in slide.markdown])
            self.assertIn("Figure to add:", deck_doc.split(f"## Slide {title}", 1)[1])

    def test_business_stakes_are_plain_language_and_outcome_focused(self):
        app = self._load_deck_page()

        stake_slide = next(
            expander for expander in app.expander if expander.label.startswith("3.")
        )
        rendered = "\n".join(markdown.value for markdown in stake_slide.markdown)
        self.assertIn("Protect recurring revenue", rendered)
        self.assertIn("Increase realised customer value", rendered)
        self.assertIn("Scale Customer Success", rendered)
        self.assertIn("8,320 accounts", rendered)
        self.assertIn("2,072", rendered)
        self.assertNotIn("MCP", rendered)
        self.assertNotIn("Rovo", rendered)
        self.assertNotIn("$56.2M", rendered)

        deck_doc = (ROOT / "docs" / "deck-outline.md").read_text(encoding="utf-8")
        normalised_deck_doc = " ".join(deck_doc.split())
        self.assertIn("## Slide 3. Why Should Atlassian Care?", deck_doc)
        self.assertIn("Protect recurring revenue", normalised_deck_doc)
        self.assertIn("Increase realised customer value", normalised_deck_doc)
        self.assertIn("Scale Customer Success", normalised_deck_doc)

    def test_method_slide_distinguishes_usage_forecasting_from_churn_prediction(self):
        app = self._load_deck_page()

        method_slide = next(
            expander for expander in app.expander if expander.label.startswith("12.")
        )
        rendered = "\n".join(markdown.value for markdown in method_slide.markdown)
        self.assertIn("Supervised churn model—rejected", rendered)
        self.assertIn("Month-5 usage forecaster—selected", rendered)
        self.assertIn("0.921", rendered)

        deck_doc = (ROOT / "docs" / "deck-outline.md").read_text(encoding="utf-8")
        self.assertIn("Supervised churn model | Rejected", deck_doc)
        self.assertIn("Month-5 usage forecaster | Selected", deck_doc)


if __name__ == "__main__":
    unittest.main()
