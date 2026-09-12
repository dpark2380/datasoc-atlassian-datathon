"""
Entry point for deployment (Streamlit Community Cloud points here).

Run: .venv/bin/streamlit run streamlit_app.py

Combines the two pages into one app:
- Risk Scorer (app_pages/risk_scorer.py): single-customer lookup, live-demo tool.
- Dashboard (app_pages/dashboard.py): full analysis, exploration, and documentation.
"""
import streamlit as st

st.set_page_config(page_title="Customer Risk & Playbook", layout="wide")

risk_scorer = st.Page("app_pages/risk_scorer.py", title="Risk Scorer", icon=":material/person_search:", default=True)
dashboard = st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:")

pg = st.navigation([risk_scorer, dashboard])
pg.run()
