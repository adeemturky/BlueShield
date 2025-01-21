import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.core import Root
import pandas as pd
import numpy as np
from typing import List
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from snowflake.snowpark import Session

connection_parameters = {
  "account":  "AQB01179.us-east-1",
  "user": "surya123",
  "password": "SuryaAdeem123@",
  "role": "ACCOUNTADMIN",
  "database": "SOC_DB",
  "schema": "SOC_SCHEMA",
  "warehouse": "COMPUTE_WH"
}
session = Session.builder.configs(connection_parameters).create()


# Set pandas display option
pd.set_option("max_colwidth", None)

# Default Values
NUM_CHUNKS = 5  # Number of chunks to retrieve as context

# Service parameters
CORTEX_SEARCH_DATABASE = "SOC_DB"
CORTEX_SEARCH_SCHEMA = "SOC_SCHEMA"
CORTEX_SEARCH_SERVICE = "SOC_SEARCH_SERVICE_CS"

# Initialize Snowflake session
# session = get_active_session()
root = Root(session)

# Initialize Cortex Search Service
svc = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]

# Define CortexSearchRetriever class
class CortexSearchRetriever:
    def __init__(self, snowpark_session, database: str, schema: str, service: str, limit_to_retrieve: int = 4):
        self._snowpark_session = snowpark_session
        self._database = database
        self._schema = schema
        self._service = service
        self._limit_to_retrieve = limit_to_retrieve

    def retrieve(self, query: str, category: str = None) -> List[str]:
        root = Root(self._snowpark_session)
        cortex_search_service = (
            root.databases[self._database]
                .schemas[self._schema]
                .cortex_search_services[self._service]
        )
        filter_obj = {"@eq": {"category": category}} if category and category != "ALL" else None
        try:
            response = cortex_search_service.search(
                query=query,
                columns=["DESCRIPTION"],
                filter=filter_obj,
                limit=self._limit_to_retrieve,
            )
            return [result["DESCRIPTION"] for result in response.results] if response.results else []
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return []

# Define RAGFromScratch class
class RAGFromScratch:
    def __init__(self, retriever: CortexSearchRetriever, model_name: str):
        self.retriever = retriever
        self.model_name = model_name

    def generate_completion(self, query: str, context_list: List[str]) -> str:
        context_str = " ".join(context_list)
        prompt = f"""
        You are an expert SOC Analyst extracting information from the provided NVD_CSV database.
        Answer the question based on the context. Provide a concise and accurate assessment, including:
        Severity:
        Impact:
        Recommended Actions:
        Do not hallucinate or provide speculative information.
        Be concise and do not hallucinate.
        If you don't have the information, just say so. ensure your answer should be formatted properly, like a report
        Context: {context_str}
        Question: {query}
        Answer:
        """
        cmd = "SELECT snowflake.cortex.complete(?, ?) AS response"
        df_response = session.sql(cmd, params=[self.model_name, prompt]).collect()
        return df_response[0]['RESPONSE'] if df_response else "No response generated."

    def query(self, query: str, category: str) -> str:
        context_list = self.retriever.retrieve(query, category)
        return self.generate_completion(query, context_list)

# Initialize session state
def initialize_session_state():
    if "rag" not in st.session_state:
        st.session_state["rag"] = False
    if "model_name" not in st.session_state:
        st.session_state["model_name"] = "mistral-large2"
    if "category_value" not in st.session_state:
        st.session_state["category_value"] = "ALL"

# Configure sidebar options
def config_options():
    st.sidebar.selectbox('Select your model:', ('mistral-large2',), key="model_name")

    categories = session.sql("SELECT DISTINCT CATEGORY FROM SOC_DB.SOC_SCHEMA.DOCS_CHUNKS_TABLE").to_pandas()["CATEGORY"].tolist()
    cat_list = ['ALL'] + categories
    selected_category = st.sidebar.selectbox('Select the log category:', cat_list, key="category_value")
    st.sidebar.expander("Session State").write(st.session_state)
    return selected_category

# Function for visualization
# def render_visualization(selected_category):
#     st.header("📊 Data Visualization Dashboard")

#     # Fetch data directly from Snowflake table
#     if selected_category == "ALL":
#         query = "SELECT CATEGORY, BASE_SEVERITY, BASE_SCORE FROM SOC_DB.SOC_SCHEMA.DOCS_CHUNKS_TABLE"
#     else:
#         query = f"SELECT CATEGORY, BASE_SEVERITY, BASE_SCORE FROM SOC_DB.SOC_SCHEMA.DOCS_CHUNKS_TABLE WHERE CATEGORY = '{selected_category}'"

#     df = session.sql(query).to_pandas()

#     # Aggregate data for visualization
#     category_distribution = df["CATEGORY"].value_counts().reset_index()
#     category_distribution.columns = ["Category", "Count"]

#     severity_distribution = df["BASE_SEVERITY"].value_counts().reset_index()
#     severity_distribution.columns = ["Base Severity", "Count"]

#     avg_base_score = df.groupby("CATEGORY")["BASE_SCORE"].mean().reset_index()
#     avg_base_score.columns = ["Category", "Average Base Score"]

#     # Create subplots
#     fig = make_subplots(
#         rows=2, cols=2,
#         subplot_titles=(
#             "Category Distribution", 
#             "Base Severity Distribution", 
#             "Average Base Score"
#             # "Combined Metrics"
#         ),
#         specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "scatter"}, {"type": "scatter"}]]
#     )

#     # Panel 1: Bar chart for category distribution
#     fig.add_trace(
#         go.Bar(x=category_distribution["Category"], y=category_distribution["Count"], name="Category Distribution"),
#         row=1, col=1
#     )

#     # Panel 2: Bar chart for base severity distribution
#     fig.add_trace(
#         go.Bar(x=severity_distribution["Base Severity"], y=severity_distribution["Count"], name="Base Severity Distribution"),
#         row=1, col=2
#     )

#     # Panel 3: Scatter plot for average base score
#     fig.add_trace(
#         go.Scatter(x=avg_base_score["Category"], y=avg_base_score["Average Base Score"], mode="markers+lines", name="Average Base Score"),
#         row=2, col=1
#     )

#     # Panel 4: Combined metrics
#     # fig.add_trace(
#     #     go.Scatter(x=avg_base_score["Category"], y=avg_base_score["Average Base Score"], mode="lines", name="Combined Metrics"),
#     #     row=2, col=2
#     # )

#     # Update layout to mimic Grafana's dark theme
#     fig.update_layout(
#         template="plotly_dark",
#         title="Data Visualization Dashboard",  # Updated title
#         title_font_size=20,
#         showlegend=True,
#         height=700
#     )

#     st.plotly_chart(fig, use_container_width=True)

def render_visualization(selected_category):
    st.header("📊 Enhanced Data Visualization Dashboard")

    # Fetch data from Snowflake table
    if selected_category == "ALL":
        query = "SELECT CATEGORY, BASE_SEVERITY, BASE_SCORE FROM SOC_DB.SOC_SCHEMA.DOCS_CHUNKS_TABLE"
    else:
        query = f"SELECT CATEGORY, BASE_SEVERITY, BASE_SCORE FROM SOC_DB.SOC_SCHEMA.DOCS_CHUNKS_TABLE WHERE CATEGORY = '{selected_category}'"

    df = session.sql(query).to_pandas()

    # Aggregations
    category_distribution = df["CATEGORY"].value_counts().reset_index()
    category_distribution.columns = ["Category", "Count"]

    severity_distribution = df["BASE_SEVERITY"].value_counts().reset_index()
    severity_distribution.columns = ["Base Severity", "Count"]

    avg_base_score = df.groupby("CATEGORY")["BASE_SCORE"].mean().reset_index()
    avg_base_score.columns = ["Category", "Average Base Score"]

    severity_vs_category = pd.crosstab(df["BASE_SEVERITY"], df["CATEGORY"])

    # Create Pie Chart for Category Distribution
    pie_chart = go.Figure(data=[go.Pie(
        labels=category_distribution["Category"],
        values=category_distribution["Count"],
        hole=0.4
    )])
    pie_chart.update_layout(title_text="Category Distribution (Pie Chart)")

    # Create Heatmap for Severity vs. Categories
    heatmap = go.Figure(data=go.Heatmap(
        z=severity_vs_category.values,
        x=severity_vs_category.columns,
        y=severity_vs_category.index,
        colorscale='Viridis'
    ))
    heatmap.update_layout(title_text="Severity vs. Category Heatmap")

    # Create Bar Chart for Base Severity Distribution with Gradient
    bar_chart = go.Figure(data=[go.Bar(
        x=severity_distribution["Base Severity"],
        y=severity_distribution["Count"],
        marker=dict(color=severity_distribution["Count"], colorscale='Bluered'),
    )])
    bar_chart.update_layout(title_text="Base Severity Distribution")

    # Create Radar Chart for Average Base Score
    radar_chart = go.Figure(data=[go.Scatterpolar(
        r=avg_base_score["Average Base Score"],
        theta=avg_base_score["Category"],
        fill='toself'
    )])
    radar_chart.update_layout(polar=dict(radialaxis=dict(visible=True)), title_text="Average Base Score (Radar Chart)")

    # Render Plots
    st.plotly_chart(pie_chart, use_container_width=True)
    st.plotly_chart(heatmap, use_container_width=True)
    st.plotly_chart(bar_chart, use_container_width=True)
    st.plotly_chart(radar_chart, use_container_width=True)



# Main function to run the Streamlit app
def main():
    initialize_session_state()
    st.sidebar.title("BLUSHIELD 🛡️")  # Sidebar title
    st.title("BLUSHIELD 🛡️")  # Main title
    st.write("This model has been fine-tuned on the National Vulnerability Dataset. Ask any query regarding that.")

    # Sample queries expander
    with st.expander("Sample Queries"):
        sample_queries = [
             "Explain how privilege escalation can occur on legacy systems and recommend defensive strategies.",
              "How can I identify exploitation attempts for CVEs related to operating systems released after 1999?",
              "Suggest methods to sandbox legacy systems to minimize the impact of exploitation.",
              
              "What are the legal and compliance considerations for operating legacy servers in a production environment?",
              
              "Generate a list of tools commonly used to attack outdated Apache servers, and suggest countermeasures."
        ]
        for i, query in enumerate(sample_queries):
            if st.button(f"Query {i + 1}: {query}"):
                st.session_state["user_query"] = query  # Set session state when a query is clicked

    selected_category = config_options()

    options = st.sidebar.radio("Choose a feature:", ["Query", "Visualization"])

    if options == "Query":
        # Prepopulate the question input field with the selected sample query
        user_query = st.session_state.get("user_query", "")  # Get from session state or default to empty
        question = st.text_input("Enter question", value=user_query, placeholder="Ask any questions regarding NVD_CVES dataset?")

        if question:
            # Initialize the retriever and RAG model
            retriever = CortexSearchRetriever(
                snowpark_session=session,
                database=CORTEX_SEARCH_DATABASE,
                schema=CORTEX_SEARCH_SCHEMA,
                service=CORTEX_SEARCH_SERVICE,
                limit_to_retrieve=NUM_CHUNKS
            )
            rag = RAGFromScratch(retriever=retriever, model_name=st.session_state.model_name)

            # Query and display the response
            response = rag.query(question, st.session_state.category_value)
            st.markdown(response)

            # Related documents sidebar
            if st.session_state.rag:
                with st.sidebar.expander("Related Documents"):
                    context_list = retriever.retrieve(question, st.session_state.category_value)
                    for context in context_list:
                        cmd2 = f"SELECT GET_PRESIGNED_URL(@docs, '{context}', 360) AS URL_LINK FROM directory(@docs)"
                        df_url_link = session.sql(cmd2).to_pandas()
                        url_link = df_url_link.at[0, 'URL_LINK']
                        display_url = f"Doc: [{context}]({url_link})"
                        st.sidebar.markdown(display_url)

    elif options == "Visualization":
        render_visualization(selected_category)

if __name__ == "__main__":
    main()

