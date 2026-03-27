import streamlit as st
import pandas as pd
import psycopg2
import logging

# ======================
# CONFIG
# ======================
DB_CONFIG = {
    "host": "localhost",
    "database": "jobs_db",
    "user": "postgres",
    "password": "postgre2302"  # move to env later
}

# ======================
# LOGGING
# ======================
logging.basicConfig(
    filename="dashboard.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ======================
# DB CONNECTION (SAFE)
# ======================
@st.cache_resource
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("DB connection successful")
        return conn
    except Exception as e:
        logging.error(f"DB connection failed: {e}")
        st.error("Database connection failed")
        return None

# ======================
# LOAD DATA (CACHED)
# ======================
@st.cache_data
def load_data():
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        df = pd.read_sql("SELECT * FROM jobs", conn)
        logging.info(f"Loaded {len(df)} rows")
        return df
    except Exception as e:
        logging.error(f"Data load error: {e}")
        return pd.DataFrame()

df = load_data()

# ======================
# UI CONFIG
# ======================
st.set_page_config(page_title="Job Analytics", layout="wide")
st.title("📊 Job Market Analytics Dashboard")

# ======================
# SIDEBAR FILTERS
# ======================
st.sidebar.header("🔍 Filters")

keyword = st.sidebar.text_input("Search Job Title")

company_filter = st.sidebar.selectbox(
    "Select Company", ["All"] + list(df['company'].dropna().unique())
)

location_filter = st.sidebar.selectbox(
    "Select Location", ["All"] + list(df['location'].dropna().unique())
)

# ======================
# FILTERING LOGIC (IMPROVED)
# ======================
filtered_df = df.copy()

if keyword:
    filtered_df = filtered_df[
        filtered_df['title'].str.contains(keyword, case=False, na=False) |
        filtered_df['tags'].str.contains(keyword, case=False, na=False)
    ]

if company_filter != "All":
    filtered_df = filtered_df[filtered_df['company'] == company_filter]

if location_filter != "All":
    filtered_df = filtered_df[filtered_df['location'] == location_filter]

# Handle empty case
if filtered_df.empty:
    st.warning("⚠️ No matching jobs found. Try adjusting filters.")

st.write(f"### Showing {len(filtered_df)} jobs")

# ======================
# INSIGHTS
# ======================
st.subheader("📈 Key Insights")

all_tags = " ".join(filtered_df['tags'].dropna()).split()
tags_series = pd.Series(all_tags)

top_skill = tags_series.value_counts().idxmax() if not tags_series.empty else "N/A"
top_company = filtered_df['company'].value_counts().idxmax() if not filtered_df.empty else "N/A"

col1, col2 = st.columns(2)
col1.metric("🔥 Most In-Demand Skill", top_skill)
col2.metric("🏢 Top Hiring Company", top_company)

# ======================
# ANALYTICS
# ======================
st.subheader("🏢 Top Hiring Companies")
st.bar_chart(filtered_df['company'].value_counts().head(10))

st.subheader("💻 Top Skills")
st.bar_chart(tags_series.value_counts().head(10))

st.subheader("📌 Job Roles")
st.bar_chart(filtered_df['title'].value_counts().head(10))

st.subheader("📍 Locations")
st.bar_chart(filtered_df['location'].value_counts().head(10))

# ======================
# REMOTE ANALYSIS (SAFE)
# ======================
st.subheader("🌍 Remote vs Onsite")

temp_df = filtered_df.copy()
temp_df['remote'] = temp_df['location'].str.contains("remote", case=False, na=False)

st.bar_chart(temp_df['remote'].value_counts())

# ======================
# SALARY
# ======================
st.subheader("💰 Salary Distribution")

salary_df = filtered_df[filtered_df['salary_max'] > 0]

if not salary_df.empty:
    st.bar_chart(salary_df['salary_max'])
else:
    st.info("No salary data available")

# ======================
# DOWNLOAD FEATURE (🔥 ADD THIS)
# ======================
st.subheader("⬇️ Download Data")

csv = filtered_df.to_csv(index=False)
st.download_button("Download CSV", csv, "jobs_data.csv")

# ======================
# RAW DATA
# ======================
st.subheader("📄 Raw Data")
st.dataframe(filtered_df)