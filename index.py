import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import pandas as pd
import numpy as np
from typing import List
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Set pandas display option
pd.set_option("max_colwidth", None)

# Default Values
NUM_CHUNKS = 5  # Number of chunks to retrieve as context

# Service parameters
CORTEX_SEARCH_DATABASE = "SOC_DB"
CORTEX_SEARCH_SCHEMA = "SOC_SCHEMA"
CORTEX_SEARCH_SERVICE = "SOC_SEARCH_SERVICE_CS"

# Snowflake connection parameters
connection_parameters = {
  "account":  "AQB01179.us-east-1",
  "user": "surya123",
  "password": "SuryaAdeem123@",
  "role": "ACCOUNTADMIN",
  "database": "SOC_DB",
  "schema": "SOC_SCHEMA",
  "warehouse": "COMPUTE_WH"
}

# Initialize Snowflake session
session = Session.builder.configs(connection_parameters).create()

# Define CortexSearchRetriever class
class CortexSearchRetriever:
    def __init__(self, snowpark_session, database: str, schema: str, service: str, limit_to_retrieve: int = 4):
        self._snowpark_session = snowpark_session
        self._database = database
        self._schema = schema
        self._service = service
        self._limit_to_retrieve = limit_to_retrieve

    def retrieve(self, query: str, category: str = None) -> List[str]:
        # Implement the retrieval logic here
        pass

# Define RAGFromScratch class
class RAGFromScratch:
    def __init__(self, retriever: CortexSearchRetriever, model_name: str):
        self.retriever = retriever
        self.model_name = model_name

    def generate_completion(self, query: str, context_list: List[str]) -> str:
        # Implement the completion generation logic here
        pass

    def query(self, query: str, category: str) -> str:
        context_list = self.retriever.retrieve(query, category)
        return self.generate_completion(query, context_list)

# Initialize session state
def initialize_session_state():
    if "rag" not in st.session_state:
        st.session_state["rag"] = False
    if "model_name" not in st.session_state:
        st.session_state["model_name"] = "mistral-large"
    if "category_value" not in st.session_state:
        st.session_state["category_value"] = "ALL"

# Configure sidebar options
def config_options():
    st.sidebar.selectbox('Select your model:', ('mistral-large',), key="model_name")

    categories = session.table("DOCS_CHUNKS_TABLE").select("CATEGORY").distinct().to_pandas()["CATEGORY"].tolist()
    cat_list = ['ALL'] + categories
    selected_category = st.sidebar.selectbox('Select the log category:', cat_list, key="category_value")
    st.sidebar.expander("Session State").write(st.session_state)
    return selected_category

# Function for visualization
def render_visualization(selected_category):
    st.header("📊 Data Visualization Dashboard")

    # Fetch data directly from Snowflake table
    if selected_category == "ALL":
        df = session.table("DOCS_CHUNKS_TABLE").select("CATEGORY", "BASE_SEVERITY", "BASE_SCORE").to_pandas()
    else:
        df = session.table("DOCS_CHUNKS_TABLE").filter(col("CATEGORY") == selected_category).select("CATEGORY", "BASE_SEVERITY", "BASE_SCORE").to_pandas()

    # Aggregate data for visualization
    category_distribution = df["CATEGORY"].value_counts().reset_index()
    category_distribution.columns = ["Category", "Count"]

    severity_distribution = df["BASE_SEVERITY"].value_counts().reset_index()
    severity_distribution.columns = ["Base Severity", "Count"]

    avg_base_score = df.groupby("CATEGORY")["BASE_SCORE"].mean().reset_index()
    avg_base_score.columns = ["Category", "Average Base Score"]

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Category Distribution", 
            "Base Severity Distribution", 
            "Average Base Score"
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "scatter"}, {"type": "scatter"}]]
    )

    # Panel 1: Bar chart for category distribution
    fig.add_trace(
        go.Bar(x=category_distribution["Category"], y=category_distribution["Count"], name="Category Distribution"),
        row=1, col=1
    )

    # Panel 2: Bar chart for base severity distribution
    fig.add_trace(
        go.Bar(x=severity_distribution["Base Severity"], y=severity_distribution["Count"], name="Base Severity Distribution"),
        row=1, col=2
    )

    # Panel 3: Scatter plot for average base score
    fig.add_trace(
        go.Scatter(x=avg_base_score["Category"], y=avg_base_score["Average Base Score"], mode="markers+lines", name="Average Base Score"),
        row=2, col=1
    )

    # Update layout to mimic Grafana's dark theme
    fig.update_layout(
        template="plotly_dark",
        title="Data Visualization Dashboard",
        title_font_size=20,
        showlegend=True,
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

# Main function to run the Streamlit app
def main():
    initialize_session_state()
    st.sidebar.title("CyberSOC Catalyst 🛡️")
    st.title("CyberSOC Catalyst 🛡️")
    st.write("This is the list of documents you already have and that will be used to answer your questions:")
    docs_available = session.sql("LS @docs").collect()

    selected_category = config_options()

    options = st.sidebar.radio("Choose a feature:", ["Query", "Visualization"])

    if options == "Query":
        question = st.text_input("Enter question", placeholder="Ask any questions regarding NVD_CVES dataset?", label_visibility="collapsed")

        if question:
            retriever = CortexSearchRetriever(
                snowpark_session
::contentReference[oaicite:0]{index=0}
 
