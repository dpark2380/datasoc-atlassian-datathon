"""
Entry point for deployment (Streamlit Community Cloud points here).

Run: .venv/bin/streamlit run streamlit_app.py

Combines the two pages into one app:
- Risk Scorer (app_pages/risk_scorer.py): single-customer lookup, live-demo tool.
- Dashboard (app_pages/dashboard.py): full analysis, exploration, and documentation.

analysis/customer_risk.csv and analysis/cleaned_tickets.csv are generated
output (gitignored) -- a fresh clone (e.g. Streamlit Community Cloud) won't
have them, so they're built once here before either page loads.
"""
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "analysis"))
import eda  # noqa: E402


@st.cache_resource
def ensure_pipeline_output() -> None:
    if not (ROOT / "analysis" / "customer_risk.csv").exists():
        eda.main()


st.set_page_config(page_title="Customer Risk & Playbook", layout="wide")
ensure_pipeline_output()

risk_scorer = st.Page("app_pages/risk_scorer.py", title="Risk Scorer", icon=":material/person_search:", default=True)
dashboard = st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:")

pg = st.navigation([risk_scorer, dashboard])
pg.run()
