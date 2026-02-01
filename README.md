# css2026-<your-suffix>

This repository contains a Streamlit app demonstrating a researcher profile and a small simulated analysis for "Longitudinal Evaluation of Common First Year (CFY)". Update the app with your real, de-identified cohort and publications data before final analysis.

Quick start (Windows CMD):

1. python -m venv .venv
2. .venv\Scripts\activate
3. python -m pip install --upgrade pip
4. python -m pip install -r requirements.txt
5. streamlit run app.py

Deployment (Streamlit Cloud):

- Ensure the GitHub repository name starts with `css2026-` (e.g., `css2026-erick-cfy`).
- Push to GitHub and then connect the repo in https://share.streamlit.io to create a public app. Make sure the deployed app name or subdomain begins with `css2026-` to meet course requirements.

Privacy note: Do not upload personally identifiable student data to a public app. Use de-identified or synthetic datasets for demos.
