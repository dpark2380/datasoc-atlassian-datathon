"""
Entry point for deployment (Streamlit Community Cloud points here).

Run: .venv/bin/streamlit run streamlit_app.py

Combines three pages into one app:
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


@st.cache_resource
def ensure_pipeline_output() -> None:
    """Regenerate the pipeline output whenever eda.py has changed since it was
    last generated.

    Keying on the hash of eda.py rather than on a specific column name catches
    changes to the *values* as well as the schema. A previous version of this
    check looked for a column in the header, which missed a rename of the risk
    category labels: the schema was unchanged, so a stale file produced by an
    older pipeline was kept and the app then crashed looking up a label that
    no longer existed in it.
    """
    risk_csv = ROOT / "analysis" / "customer_risk.csv"
    stamp_file = ROOT / "analysis" / ".pipeline_stamp"
    current = hashlib.sha256(Path(eda.__file__).read_bytes()).hexdigest()

    previous = stamp_file.read_text(encoding="utf-8").strip() if stamp_file.exists() else None
    if risk_csv.exists() and previous == current:
        return

    eda.main()
    stamp_file.write_text(current, encoding="utf-8")


st.set_page_config(page_title="Customer Risk & Playbook", layout="wide")
ensure_pipeline_output()

dashboard = st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)
risk_scorer = st.Page("app_pages/risk_scorer.py", title="Risk Scorer", icon=":material/person_search:")
business_context = st.Page(
    "app_pages/business_context.py", title="Business Context", icon=":material/account_balance:"
)

pg = st.navigation([dashboard, risk_scorer, business_context])
pg.run()
