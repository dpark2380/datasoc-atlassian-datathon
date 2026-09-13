import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).parent.parent


class DeckOutlineAppTests(unittest.TestCase):
    def test_business_stakes_focuses_on_adoption_and_expansion(self):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=60).run()
        app.switch_page("app_pages/deck_outline.py").run()

        self.assertFalse(app.exception)
        rendered = "\n".join(markdown.value for markdown in app.markdown)
        self.assertIn("MCP adopters grow ARR 2× faster", rendered)
        self.assertIn("Rovo adopters grow ARR more than 2× faster", rendered)
        self.assertIn("20% more Jira work items", rendered)
        self.assertIn("25% more Confluence pages", rendered)
        self.assertIn("FY26 revenue grew 26% while cost of revenues grew 11%", rendered)
        self.assertIn("$56.2M", rendered)

        deck_doc = (ROOT / "docs" / "deck-outline.md").read_text(encoding="utf-8")
        normalised_deck_doc = " ".join(deck_doc.split())
        self.assertIn("## Slide 2. Business Stakes: Adoption Drives Expansion", deck_doc)
        self.assertIn("MCP adopters grow ARR 2x faster", normalised_deck_doc)
        self.assertIn("20% more Jira work items", normalised_deck_doc)
        self.assertIn("25% more Confluence pages", normalised_deck_doc)
        self.assertIn(
            "FY26 revenue grew 26% while cost of revenues grew 11%", normalised_deck_doc
        )
        self.assertIn("$56.2M", normalised_deck_doc)


if __name__ == "__main__":
    unittest.main()
