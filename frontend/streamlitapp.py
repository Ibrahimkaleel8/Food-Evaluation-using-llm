import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import sys
import os

# To allow importing from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from backend.analytics import get_dataframe, compute_clusters
except ImportError:
    pass

st.set_page_config(page_title="NutriWise Pro", layout="wide", page_icon="🥗")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home (Query)", "Analytics Dashboard"])

api_stream = "http://localhost:3000/response/stream"

def parse_sse(response):
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith("data: "):
                data_str = decoded[6:]
                if data_str == "[DONE]":
                    break
                try:
                    data_json = json.loads(data_str)
                    if "token" in data_json:
                        yield data_json["token"]
                    elif "error" in data_json:
                        yield f"\n\n**Error:** {data_json['error']}"
                except json.JSONDecodeError:
                    pass

if page == "Home (Query)":
    st.title("NutriWise Pro 🍲")
    st.markdown("### Predicting nutrients and personalized health metrics with USDA-grounded RAG")

    with st.expander("User Profile (Optional)"):
        col1, col2, col3 = st.columns(3)
        age = col1.number_input("Age", min_value=1, max_value=120, value=30)
        weight = col2.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0)
        goal = col3.selectbox("Goal", ["general_health", "weight_loss", "muscle_gain"])
        conditions = st.multiselect("Health Conditions", ["diabetes", "hypertension", "high_cholesterol", "obesity"])
        
        use_profile = st.checkbox("Apply Personalized Scoring")

    with st.form("my_form"):
        text_input = st.text_input("Enter name of the food 👇", placeholder="e.g., raw broccoli, cooked salmon...")
        submitted = st.form_submit_button("Analyze (Stream)")

        if submitted and text_input:
            payload = {"food_name": text_input}
            if use_profile:
                payload["profile"] = {
                    "age": age,
                    "weight_kg": weight,
                    "goal": goal,
                    "conditions": conditions
                }

            st.write("---")
            st.subheader("LLM Reasoning (Streaming)")
            response_container = st.empty()
            
            with st.spinner("Connecting to Gemini and USDA RAG..."):
                try:
                    r = requests.post(api_stream, json=payload, stream=True)
                    r.raise_for_status()
                    
                    # Stream rendering
                    full_json_str = response_container.write_stream(parse_sse(r))
                    
                    st.success("Analysis complete!")
                    st.write("---")
                    
                    # Parse final JSON to render structured card
                    clean_json = full_json_str.strip("```json\n").strip("\n```").strip()
                    res = json.loads(clean_json)
                    
                    st.header("Nutrition Breakdown")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    col_a.metric("Calories", f"{res.get('calories', 0)} kcal")
                    col_b.metric("Protein", f"{res.get('protein_g', 0)} g")
                    col_c.metric("Carbs", f"{res.get('carbs_g', 0)} g")
                    col_d.metric("Fat", f"{res.get('fat_g', 0)} g")
                    
                    st.write(f"**Fiber:** {res.get('fiber_g', 0)} g")
                    st.write(f"**Key Vitamins:** {', '.join(res.get('key_vitamins', []))}")
                    
                    st.subheader("Health Scoring")
                    score_col1, score_col2 = st.columns(2)
                    score_col1.metric("Base Health Score", f"{res.get('health_score', 0)} / 100")
                    
                    # Compute personalized score client side for display if backend stream didn't inject it yet
                    # Actually backend doesn't stream the personalized score, it calculates it post-stream.
                    # We will just show the recommendation.
                    st.info(f"**Recommendation:** {res.get('recommendation', 'N/A')}")
                    
                    st.caption(f"Source: {res.get('retrieval_source', 'Unknown')} | Confidence: {res.get('confidence', 0.0)}")
                    
                except Exception as e:
                    st.error(f"Error fetching response: {e}")

elif page == "Analytics Dashboard":
    st.title("Nutrition Query Analytics 📊")
    st.write("Insights from your query history using K-Means clustering.")
    
    try:
        df = get_dataframe()
    except Exception as e:
        df = pd.DataFrame()
        st.warning("Database not initialized yet. Please make some queries first.")

    if not df.empty and len(df) >= 5:
        df_clustered = compute_clusters(df)
        
        # Metrics
        st.subheader("Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Queries", len(df))
        c2.metric("Unique Foods", df["food_name"].nunique())
        c3.metric("Avg Health Score", f"{df['health_score'].mean():.1f}")
        c4.metric("Avg Confidence", f"{df['confidence'].mean():.2f}")
        
        st.markdown("---")
        
        # Charts row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Nutrient Clusters (PCA)")
            fig1 = px.scatter(
                df_clustered, x="pca_x", y="pca_y", 
                color="cluster_label", 
                hover_data=["food_name", "calories", "protein_g"],
                title="Foods grouped by nutritional profile"
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            st.markdown("#### Top 10 Queried Foods")
            top_10 = df["food_name"].value_counts().head(10).reset_index()
            top_10.columns = ["Food", "Count"]
            fig2 = px.bar(top_10, x="Food", y="Count", color="Count", title="Most popular queries")
            st.plotly_chart(fig2, use_container_width=True)
            
        # Charts row 2
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("#### Health Score Distribution")
            fig3 = px.histogram(df, x="health_score", nbins=10, title="Distribution of Base Health Scores")
            st.plotly_chart(fig3, use_container_width=True)
            
        with col4:
            st.markdown("#### Query Volume Over Time")
            df["day"] = pd.to_datetime(df["timestamp"]).dt.date
            daily_vol = df.groupby("day").size().reset_index(name="Queries")
            fig4 = px.line(daily_vol, x="day", y="Queries", markers=True, title="Queries processed per day")
            st.plotly_chart(fig4, use_container_width=True)
            
    else:
        st.info("📉 Not enough data to compute analytics. Please perform at least 5 queries on the Home page.")
        if not df.empty:
            st.write(f"Current query count: {len(df)} / 5")
