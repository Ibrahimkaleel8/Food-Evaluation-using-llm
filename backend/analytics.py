import sqlite3
import os
import json
import pandas as pd
from datetime import datetime
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
except ImportError:
    KMeans = None
    StandardScaler = None
    PCA = None

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "query_log.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            food_name TEXT,
            calories REAL,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL,
            fiber_g REAL,
            health_score REAL,
            personalized_score REAL,
            confidence REAL,
            retrieval_source TEXT,
            latency_ms REAL
        )
    """)
    conn.commit()
    conn.close()

def log_query(data: dict):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO queries (timestamp, food_name, calories, protein_g, carbs_g,
                             fat_g, fiber_g, health_score, personalized_score,
                             confidence, retrieval_source, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        data.get("food_name", ""),
        data.get("calories", 0.0),
        data.get("protein_g", 0.0),
        data.get("carbs_g", 0.0),
        data.get("fat_g", 0.0),
        data.get("fiber_g", 0.0),
        data.get("health_score", 0.0),
        data.get("personalized_score", 0.0),
        data.get("confidence", 0.0),
        data.get("retrieval_source", ""),
        data.get("latency_ms", 0.0)
    ))
    conn.commit()
    conn.close()

def get_all_queries() -> list[dict]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM queries ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_dataframe() -> pd.DataFrame:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM queries", conn)
    conn.close()
    return df

def compute_clusters(df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    if df.empty or len(df) < n_clusters or KMeans is None:
        if not df.empty:
            df["cluster"] = 0
            df["pca_x"] = 0
            df["pca_y"] = 0
            df["cluster_label"] = "Insufficient Data"
        return df

    features = ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"]
    X = df[features].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    df["cluster"] = clusters
    df["pca_x"] = X_pca[:, 0]
    df["pca_y"] = X_pca[:, 1]
    
    # Assign human-readable cluster labels based on dominant nutrient profile
    cluster_labels = {}
    for i in range(n_clusters):
        center = kmeans.cluster_centers_[i]
        # De-scale to interpret
        true_center = scaler.inverse_transform([center])[0]
        # simple heuristic mapping
        cal, prot, carb, fat, fib = true_center
        if prot > carb and prot > fat:
            label = "High protein"
        elif carb > prot and carb > fat:
            label = "High carb"
        elif fat > prot and fat > carb:
            label = "High fat"
        elif cal < 100:
            label = "Low calorie"
        else:
            label = "Balanced"
        cluster_labels[i] = label

    df["cluster_label"] = df["cluster"].map(cluster_labels)
    return df
