import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO
import base64

st.set_page_config(page_title="Erick Chauke — CFY Evaluation", layout="wide")

# Apply background image if available (reads local `background.jpg` and embeds it)
def set_background_image(image_path: str):
    try:
        with open(image_path, "rb") as img_file:
            data = img_file.read()
        b64 = base64.b64encode(data).decode()
        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except Exception:
        # Fail silently if image not found or cannot be loaded
        pass

# Try to set the background from `background.jpg` in the app folder
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

st.title(f"{PROFILE['name']} — Researcher Profile")
col1, col2 = st.columns([2, 3])
with col1:
    st.subheader("Personal Profile")
    st.markdown(f"**Name:** {PROFILE['name']}  ")
    st.markdown(f"**Title:** {PROFILE['title']}  ")
    st.markdown(f"**Institution:** {PROFILE['institution']}  ")
    st.markdown(f"**Email:** {PROFILE['email']}  ")
    st.markdown(f"**Citizenship:** {PROFILE['citizenship']}  ")

with col2:
    st.subheader("Short Project Summary")
    st.markdown(
        "This project performs a longitudinal evaluation of the Common First Year (CFY) program at Wits FEBE. "
        "It compares pre-CFY cohorts (2016–2018) with CFY-era cohorts (2019–2021) to estimate impacts on pass rates, "
        "credit accumulation, exclusions, and distinctions using interrupted time-series and difference-in-differences designs."
    )

# ---------------------------
# Project details / objectives
# ---------------------------
st.header("Project: Longitudinal Evaluation of CFY Impact")
st.markdown("**Aim:** Quantify how the CFY program affected student academic outcomes and equity across cohorts.")
st.markdown("**Key objectives:** Build cohort panels, compute longitudinal outcomes, apply ITS and DiD models, and synthesize findings for policy.")

# ---------------------------
# Publications (upload)
# ---------------------------
st.subheader("Publications / Outputs")
pub_file = st.file_uploader("Upload a CSV of Publications (optional)", type=["csv"])
if pub_file is not None:
    try:
        pubs = pd.read_csv(pub_file)
        st.success("Publications loaded")
        st.dataframe(pubs)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
else:
    st.info("You can upload a publications CSV with columns like Title, Year, Authors.")

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
# Contact notes
# ---------------------------
st.sidebar.header("Contact")
st.sidebar.write(PROFILE['name'])
st.sidebar.write(PROFILE['email'])
st.sidebar.markdown("---")

# Done