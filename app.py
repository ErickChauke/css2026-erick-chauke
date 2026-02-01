import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO
import base64
from pypdf import PdfReader
import re
import os

st.set_page_config(page_title="Erick Chauke — CFY Evaluation", layout="wide")

# Background and overlay utilities (embed local `background.jpg` and optional overlay)
def set_background_image(image_path: str, size_mode: str = "cover"):
    try:
        with open(image_path, "rb") as img_file:
            data = img_file.read()
        b64 = base64.b64encode(data).decode()
        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64}");
            background-size: {size_mode};
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center center;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except Exception:
        pass


def set_overlay(opacity: float = 0.45, color: str = "0,0,0"):
    # Adds a dark overlay over the background for readability
    try:
        css = f"""
        <style>
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba({color},{opacity});
            z-index: 0;
            pointer-events: none;
        }}
        /* Ensure main content is above overlay */
        .css-1lcbmhc {{ z-index: 1; }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except Exception:
        pass

# Apply background (attempt to load local image)
set_background_image("background.jpg")

# ---------------------------
# Profile (provided data)
# ---------------------------
PROFILE = {
    "title": "Mr",
    "initials": "EM",
    "name": "Erick Chauke",
    "email": "erickchauke0217@gmail.com",
    "citizenship": "South African citizen",
    "institution": "University of the Witwatersrand",
} 

# Allow applying parsed profile (keeps changes in session state)
if "profile" not in st.session_state:
    st.session_state["profile"] = PROFILE
current_profile = st.session_state["profile"]

st.title(f"{current_profile['name']} — Researcher Profile")
col1, col2 = st.columns([2, 3])
with col1:
    st.subheader("Personal Profile")
    st.markdown(f"**Name:** {current_profile['name']}  ")
    st.markdown(f"**Title:** {current_profile['title']}  ")
    st.markdown(f"**Institution:** {current_profile['institution']}  ")
    st.markdown(f"**Email:** {current_profile['email']}  ")
    st.markdown(f"**Citizenship:** {current_profile['citizenship']}  ")

with col2:
    st.subheader("Short Project Summary")
    st.markdown(
        "This project performs a longitudinal evaluation of the Common First Year (CFY) program at Wits FEBE. "
        "It compares pre-CFY cohorts (2016–2018) with CFY-era cohorts (2019–2021) to estimate impacts on pass rates, "
        "credit accumulation, exclusions, and distinctions using interrupted time-series and difference-in-differences designs."
    )

    # CV download & import (if CV exists in repo root)
    import os
    cv_path = "Erick_Chauke_CV.pdf"
    if os.path.exists(cv_path):
        with open(cv_path, "rb") as _f:
            cv_bytes = _f.read()
        st.download_button("Download CV (PDF)", data=cv_bytes, file_name="Erick_Chauke_CV.pdf")
        if st.button("Import profile from CV"):
            parsed = parse_cv_from_path(cv_path)
            if parsed.get("error"):
                st.error(f"Could not parse CV: {parsed['error']}")
            else:
                with st.expander("Parsed CV summary"):
                    st.write(parsed)
                if st.button("Apply parsed profile"):
                    # Apply parsed fields where available
                    if parsed.get("name"):
                        st.session_state["profile"]["name"] = parsed["name"]
                    if parsed.get("email"):
                        st.session_state["profile"]["email"] = parsed["email"]
                    st.success("Applied parsed profile. Refresh the page to see updates.")
    else:
        st.info("No CV found in repository root (save your CV as 'Erick_Chauke_CV.pdf' to enable import).")

# ---------------------------
# Project details / objectives
# ---------------------------
st.header("Project: Longitudinal Evaluation of CFY Impact")
st.markdown("**Aim:** Quantify how the CFY program affected student academic outcomes and equity across cohorts.")
st.markdown("**Key objectives:** Build cohort panels, compute longitudinal outcomes, apply ITS and DiD models, and synthesize findings for policy.")

# ---------------------------
# CV parsing utilities & Projects
# ---------------------------

def parse_cv_from_path(path: str) -> dict:
    """Extracts simple fields from a CV PDF (email, candidate name, and project mentions)."""
    out = {"email": None, "name": None, "projects": [], "raw_snippet": None}
    try:
        reader = PdfReader(path)
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        out["raw_snippet"] = text[:1200]
        m = re.search(r"[\w\.-]+@[\w\.-]+", text)
        if m:
            out["email"] = m.group(0)
        # Try to find name near the top (first lines)
        first_lines = text.strip().splitlines()[:20]
        for line in first_lines:
            if len(line.strip().split()) <= 5 and any(ch.isalpha() for ch in line):
                # crude name heuristic: line with letters and not too long
                out["name"] = line.strip()
                break
        # project-like extractions (search for known keywords and capitalized phrases)
        project_keywords = ["Autism", "mvelaphi", "family tree", "Stock", "management", "AI", "Web", "Three.js", "React"]
        found = set()
        for kw in project_keywords:
            if re.search(kw, text, re.I):
                found.add(kw)
        out["projects"] = list(found)
    except Exception as e:
        out["error"] = str(e)
    return out

# Small 'Projects' area — will include notable projects (editable later)
st.subheader("Selected projects")
projects_list = [
    ("AI Autism Tutoring Platform", "Web-based eye contact training system for children with autism using AI and MediaPipe."),
    ("mvelaphi — African Family Tree Platform", "MERN-based platform for preserving African family heritage and kinship structures."),
    ("Stock Management System", "Enterprise stock management system with RBAC and MSAL authentication."),
]
for title, descr in projects_list:
    st.markdown(f"**{title}** — {descr}")


# ---------------------------
# Publications (upload + validation)
# ---------------------------
st.subheader("Publications / Outputs")

def validate_publications(df: pd.DataFrame):
    required = {"Title", "Year", "Authors"}
    if not required <= set(df.columns):
        raise ValueError("CSV must contain columns: Title, Year, Authors")
    # Detect obvious PII-ish columns
    pii_indicators = ["id", "passport", "identity", "ssn", "phone", "address", "surname", "firstname"]
    pii_cols = [c for c in df.columns if any(p in c.lower() for p in pii_indicators)]
    if pii_cols:
        raise ValueError(f"Remove PII columns before uploading: {', '.join(pii_cols)}")
    return True

pub_file = st.file_uploader("Upload a CSV of Publications (optional)", type=["csv"])
if pub_file is not None:
    try:
        pubs = pd.read_csv(pub_file)
        try:
            validate_publications(pubs)
            st.success("Publications loaded and validated")
            st.dataframe(pubs)
        except ValueError as ve:
            st.error(str(ve))
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
else:
    st.info("You can upload a publications CSV with columns: Title, Year, Authors.")

# Provide a sample CSV to download
sample_csv = "Title,Year,Authors\nAn investigation of CFY effects,2024,Erick Chauke; A. Coauthor\nCurriculum reform outcomes,2023,Erick Chauke"
st.download_button(label="Download sample publications CSV", data=sample_csv, file_name="sample_publications.csv")

# ---------------------------
# Illustrative analysis
# ---------------------------
st.header("Illustrative analysis")
st.markdown("This section shows an illustrative analysis using simulated data for demonstration purposes.")

@st.cache_data
def make_simulated_data(seed=42):
    np.random.seed(seed)
    years = list(range(2016, 2022))  # 2016-2021
    rows = []
    for year in years:
        for i in range(200):  # 200 students per intake (small demo)
            is_cfy = 1 if year >= 2019 else 0
            # baseline pass probability by year + CFY effect
            base = 0.7 - 0.02 * (year - 2016) + np.random.normal(0, 0.02)
            cfy_shift = 0.03 * is_cfy  # small positive or negative effect to simulate
            pass_prob = np.clip(base + cfy_shift + np.random.normal(0, 0.05), 0, 1)
            rows.append({
                "year": year,
                "cfy": is_cfy,
                "pass": np.random.binomial(1, pass_prob),
                "wam": np.clip(60 + (pass_prob - 0.7) * 40 + np.random.normal(0, 8), 0, 100),
                "gender": np.random.choice(["Male", "Female"], p=[0.6, 0.4]),
                "race": np.random.choice(["African", "White", "Coloured", "Indian"], p=[0.6, 0.2, 0.1, 0.1])
            })
    df = pd.DataFrame(rows)
    return df

sim_df = make_simulated_data()

# Controls
colA, colB = st.columns(2)
with colA:
    group = st.selectbox("Group to stratify by", options=["All", "Male", "Female"], index=0)
with colB:
    metric = st.selectbox("Metric", options=["Pass Rate", "Mean WAM"], index=0)

if group != "All":
    plot_df = sim_df[sim_df["gender"] == group]
else:
    plot_df = sim_df.copy()

agg = None
if metric == "Pass Rate":
    agg = plot_df.groupby("year").agg(pass_rate=("pass", "mean")).reset_index()
    fig = px.line(agg, x="year", y="pass_rate", markers=True, title=f"Pass Rate by Year ({group})", labels={"pass_rate": "Pass rate"})
else:
    agg = plot_df.groupby("year").agg(mean_wam=("wam", "mean")).reset_index()
    fig = px.line(agg, x="year", y="mean_wam", markers=True, title=f"Mean WAM by Year ({group})", labels={"mean_wam": "Mean WAM"})

st.plotly_chart(fig, use_container_width=True)

# Simple DiD-style estimate (year-level mean before/after)
st.subheader("Simple pre/post comparison (illustrative)")
pre = agg[agg["year"] < 2019]
post = agg[agg["year"] >= 2019]
pre_mean = pre.iloc[-1, 1] if not pre.empty else np.nan
post_mean = post.iloc[0, 1] if not post.empty else np.nan
st.write(f"Pre (last pre-CFY year) mean: **{pre_mean:.3f}**, Post (first CFY year) mean: **{post_mean:.3f}**")
st.markdown("**Note:** This is a simple illustrative comparison. Formal DiD and ITS analyses require cohort-level panel construction and modelling.")

# ---------------------------
# Sidebar: Contact & Appearance
# ---------------------------
st.sidebar.header("Contact")
st.sidebar.write(st.session_state["profile"]["name"])
st.sidebar.write(st.session_state["profile"]["email"])
st.sidebar.markdown("---")

st.sidebar.subheader("Appearance")
overlay_enabled = st.sidebar.checkbox("Enable dark overlay", value=True)
overlay_opacity = st.sidebar.slider("Overlay darkness", min_value=0.0, max_value=0.8, value=0.45, step=0.05)
bg_mode = st.sidebar.selectbox("Background mode", options=["cover", "contain"], index=0)

# Apply background and overlay according to sidebar settings
set_background_image("background.jpg", size_mode=bg_mode)
if overlay_enabled:
    set_overlay(opacity=overlay_opacity)

st.sidebar.markdown("---")
st.sidebar.caption("Note: background image and overlay control are for presentation only.")

# Done