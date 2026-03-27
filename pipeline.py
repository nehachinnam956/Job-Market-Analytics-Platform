import requests
import pandas as pd
import psycopg2

# ======================
# EXTRACT + TRANSFORM
# ======================

url = "https://remoteok.com/api"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
data = response.json()

jobs = []

for job in data[1:]:
    jobs.append({
        "title": job.get("position"),
        "company": job.get("company"),
        "location": job.get("location"),
        "tags": " ".join(job.get("tags", [])),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max")
    })

df = pd.DataFrame(jobs)

keywords = ["data", "analytics", "engineer", "ml", "ai", "python", "sql"]
pattern = "|".join(keywords)

df_filtered = df[
    df["title"].str.contains(pattern, case=False, na=False) |
    df["tags"].str.contains(pattern, case=False, na=False)
]

df_filtered = df_filtered.drop_duplicates(subset=["title", "company"])

print("Filtered jobs:", len(df_filtered))

# ======================
# LOAD TO DATABASE
# ======================

conn = psycopg2.connect(
    host="localhost",
    database="jobs_db",
    user="postgres",
    password="postgre2302"   # 🔴 change this
)

cursor = conn.cursor()

for _, row in df_filtered.iterrows():
    cursor.execute("""
        INSERT INTO jobs (title, company, location, tags, salary_min, salary_max)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        row['title'],
        row['company'],
        row['location'],
        row['tags'],
        int(row['salary_min'] or 0),
        int(row['salary_max'] or 0)
    ))

conn.commit()
cursor.close()
conn.close()

print("✅ Data inserted successfully")