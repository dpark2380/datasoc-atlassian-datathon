"""
Entry point for deployment (Streamlit Community Cloud points here).

Run: .venv/bin/streamlit run streamlit_app.py

Combines four pages into one app:
- Dashboard (app_pages/dashboard.py): full analysis, exploration, and documentation.
- Risk Scorer (app_pages/risk_scorer.py): single-customer lookup, live-demo tool.
- Business Context (app_pages/business_context.py): the case for this work, from
  Atlassian's SEC filings. Deliberately separate from the other two, since none
  of it comes from the datathon dataset.

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


try:
    from analysis import predict_disengagement  # noqa: E402
except ImportError:
    import predict_disengagement  # noqa: E402


@st.cache_resource
def ensure_pipeline_output(code_version: str) -> None:
    """Regenerate both pipeline outputs whenever eda.py or
    predict_disengagement.py actually change.

    st.cache_resource caches by this function's arguments, so a distinct
    code_version hash is a guaranteed cache miss, meaning this body only
    ever runs once per distinct code version. That is why it is safe (and
    necessary) to regenerate unconditionally here rather than checking
    whether the output files already exist: a stale file left over from a
    previous code version, on a long-lived deployed process that never
    restarted, is exactly the bug this replaces (a KeyError from a CSV
    missing a column added since that file was last generated).
    """
    eda.main()
    predict_disengagement.main()


st.set_page_config(page_title="Customer Risk & Playbook", layout="wide")
_code_version = hashlib.sha256(
    Path(eda.__file__).read_bytes() + Path(predict_disengagement.__file__).read_bytes()
).hexdigest()
ensure_pipeline_output(_code_version)

dashboard = st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)
risk_scorer = st.Page("app_pages/risk_scorer.py", title="Risk Scorer", icon=":material/person_search:")
business_context = st.Page(
    "app_pages/business_context.py", title="Business Context", icon=":material/account_balance:"
)

pg = st.navigation([dashboard, risk_scorer, business_context])
pg.run()
