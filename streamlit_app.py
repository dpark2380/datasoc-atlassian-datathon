"""
Entry point for deployment (Streamlit Community Cloud points here).

Run: .venv/bin/streamlit run streamlit_app.py

Combines four pages into one app:
- Dashboard (app_pages/dashboard.py): full analysis, exploration, and documentation.
- Risk Scorer (app_pages/risk_scorer.py): single-customer lookup, live-demo tool.
- Business Context (app_pages/business_context.py): the case for this work, from
  Atlassian's SEC filings. Deliberately separate from the other two, since none
  of it comes from the datathon dataset.
- Deck Outline (app_pages/deck_outline.py): the presentation plan, kept in sync
  with docs/deck-outline.md.

analysis/customer_risk.csv and analysis/cleaned_tickets.csv are generated
output (gitignored) -- a fresh clone (e.g. Streamlit Community Cloud) won't
have them, so they're built once here before either page loads.
"""
import hashlib
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "analysis"))
try:
    from analysis import eda  # noqa: E402
except ImportError:
    import eda  # noqa: E402


@st.cache_resource
def ensure_pipeline_output() -> None:
    risk_csv = ROOT / "analysis" / "customer_risk.csv"
    stamp_file = ROOT / "analysis" / ".pipeline_stamp"
    current = hashlib.sha256(Path(eda.__file__).read_bytes()).hexdigest()

    previous = stamp_file.read_text(encoding="utf-8").strip() if stamp_file.exists() else None
    if not risk_csv.exists() or previous != current:
        eda.main()
        stamp_file.write_text(current, encoding="utf-8")

    ml_json = ROOT / "analysis" / "ml_results.json"
    if not ml_json.exists():
        try:
            from analysis import predict_disengagement  # noqa: E402
        except ImportError:
            import predict_disengagement  # noqa: E402
        predict_disengagement.main()


st.set_page_config(page_title="Customer Risk & Playbook", layout="wide")
ensure_pipeline_output()

dashboard = st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)
risk_scorer = st.Page("app_pages/risk_scorer.py", title="Risk Scorer", icon=":material/person_search:")
business_context = st.Page(
    "app_pages/business_context.py", title="Business Context", icon=":material/account_balance:"
)
deck_outline = st.Page("app_pages/deck_outline.py", title="Deck Outline", icon=":material/slideshow:")

pg = st.navigation([dashboard, risk_scorer, business_context, deck_outline])
pg.run()
