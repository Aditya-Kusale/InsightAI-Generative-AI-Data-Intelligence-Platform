import os
import time
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from pygwalker.api.streamlit import StreamlitRenderer


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(page_title="InsightAI", layout="wide")


# -----------------------------
# Database connection
# -----------------------------
@st.cache_resource
def get_database():
    return SQLDatabase.from_uri("sqlite:///Chinook.db")


@st.cache_resource
def get_sqlite_connection():
    return sqlite3.connect("Chinook.db", check_same_thread=False)


db = get_database()
conn = get_sqlite_connection()


# -----------------------------
# API key configuration
# -----------------------------
def get_api_key():
    # Sidebar input takes priority. Streamlit secrets are a secure fallback.
    user_key = st.session_state.get("user_api_key_input", "").strip()
    if user_key:
        return user_key

    # Support both the old secret name and the standard OpenAI name.
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]

    if "openai_api_key" in st.secrets:
        return st.secrets["openai_api_key"]

    return ""


def get_llm(api_key, model, temperature, top_p):
    base_url = st.secrets.get("selected_base_url", "https://api.openai.com/v1")
    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        top_p=top_p,
    )


# -----------------------------
# Data Agent
# -----------------------------
def generate_dataframe(question, llm):
    examples = [
        {"input": "List all artists.", "query": "SELECT * FROM Artist;"},
        {
            "input": "Find all albums for the artist 'AC/DC'.",
            "query": "SELECT * FROM Album WHERE ArtistId = (SELECT ArtistId FROM Artist WHERE Name = 'AC/DC');",
        },
        {
            "input": "List all tracks in the 'Rock' genre.",
            "query": "SELECT * FROM Track WHERE GenreId = (SELECT GenreId FROM Genre WHERE Name = 'Rock');",
        },
        {
            "input": "Find the total duration of all tracks.",
            "query": "SELECT SUM(Milliseconds) AS TotalDuration FROM Track;",
        },
        {
            "input": "List all customers from Canada.",
            "query": "SELECT * FROM Customer WHERE Country = 'Canada';",
        },
    ]

    example_prompt = PromptTemplate.from_template(
        "User input: {input}\nSQL query: {query}"
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=(
            "You are a SQLite expert. Given an input question, create a syntactically "
            "correct SQLite query. Unless otherwise specified, do not return more than "
            "{top_k} rows.\n\nRelevant table information:\n{table_info}\n\n"
            "Examples:"
        ),
        suffix="User input: {input}\nSQL query:",
        input_variables=["input", "top_k", "table_info"],
    )

    sql_chain = create_sql_query_chain(llm, db, few_shot_prompt)

    validation_system = """You are a SQLite SQL validator.
Check the SQL query for common mistakes. Return ONLY a valid SQLite SQL query.
Do not include markdown, explanations, or comments.
If the query is already correct, return it unchanged."""

    validation_prompt = ChatPromptTemplate.from_messages(
        [("system", validation_system), ("human", "{query}")]
    )

    validation_chain = validation_prompt | llm | StrOutputParser()

    try:
        raw_query = sql_chain.invoke({"question": question})
        final_query = validation_chain.invoke({"query": raw_query}).strip()

        # Remove accidental markdown fences.
        final_query = final_query.replace("```sql", "").replace("```", "").strip()

        cursor = conn.cursor()
        cursor.execute(final_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        answer = pd.DataFrame(rows, columns=columns)
        st.session_state["df"] = answer

        st.success("Data generated successfully!", icon="✅")
        with st.expander("📑 Data Result", expanded=True):
            st.dataframe(answer, use_container_width=True)

        with st.expander("Generated SQL"):
            st.code(final_query, language="sql")

    except Exception as e:
        st.error(f"Unable to generate data: {e}")


# -----------------------------
# BI Wizard
# Replaces the deprecated VizroAI API
# -----------------------------
def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.02)


def generate_business_insights(df, prompt, llm):
    summary = df.head(20).to_csv(index=False)

    insight_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a business intelligence analyst. Analyze the supplied dataset
and answer the user's request with concise, useful insights. Mention notable trends,
patterns, comparisons, and caveats when relevant. Do not invent data.""",
            ),
            (
                "human",
                "User request: {prompt}\n\nDataset sample:\n{data}",
            ),
        ]
    )

    chain = insight_prompt | llm | StrOutputParser()
    return chain.invoke({"prompt": prompt, "data": summary})


def build_chart(df, chart_type, x_col, y_col):
    if df.empty:
        return None

    if chart_type == "Bar":
        return px.bar(df, x=x_col, y=y_col)
    if chart_type == "Line":
        return px.line(df, x=x_col, y=y_col)
    if chart_type == "Scatter":
        return px.scatter(df, x=x_col, y=y_col)
    if chart_type == "Pie":
        return px.pie(df, names=x_col, values=y_col)
    if chart_type == "Histogram":
        return px.histogram(df, x=x_col)

    return px.bar(df, x=x_col, y=y_col)


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("InsightAI ✨")

    st.text_input(
        "OpenAI API Key (optional if configured in Secrets)",
        type="password",
        placeholder="sk-...",
        key="user_api_key_input",
    )

    api_key = get_api_key()

    if api_key:
        st.success("API key configured", icon="✅")
    else:
        st.info("Add an API key in Streamlit Secrets or enter one above.")

    st.subheader("Model Settings")

    selected_model = st.selectbox(
        "Choose a model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
        index=0,
    )
    selected_temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.1, 0.05
    )
    selected_top_p = st.slider(
        "Top P", 0.1, 1.0, 0.9, 0.05
    )

    st.markdown("---")
    st.header("About")
    st.write(
        "Transforming natural-language questions into structured data analysis "
        "and interactive visualizations."
    )

    st.markdown("---")
    st.caption("InsightAI — Generative AI Data Intelligence Platform")


llm = None
if api_key:
    try:
        llm = get_llm(
            api_key,
            selected_model,
            selected_temperature,
            selected_top_p,
        )
    except Exception as e:
        st.sidebar.error(f"LLM configuration error: {e}")


# -----------------------------
# Main UI
# -----------------------------
tab1, tab2, tab3 = st.tabs(
    ["Data Agent", "Visual Analyzer", "BI Wizard"]
)


with tab1:
    st.markdown("### Data Agent 📂")
    st.write("Ask questions about the Chinook SQLite database in natural language.")

    with st.form("data_agent"):
        question = st.text_area(
            "Enter your question",
            "Who are the top 5 customers by total purchase?",
        )
        submitted = st.form_submit_button("Generate")

    if submitted:
        if not api_key or llm is None:
            st.error("Please configure an OpenAI API key first.")
        elif question.strip():
            with st.spinner("Generating SQL and querying data..."):
                generate_dataframe(question, llm)


with tab2:
    st.markdown("### Visual Analyzer 📊")

    uploaded_file = st.file_uploader(
        "Upload a CSV file or use data generated by the Data Agent",
        type=["csv"],
    )

    df_for_visualization = None

    if "df" in st.session_state and st.session_state["df"] is not None:
        df_for_visualization = st.session_state["df"]
        st.success("Using dataset generated by Data Agent.", icon="✅")

    if uploaded_file is not None:
        try:
            df_for_visualization = pd.read_csv(uploaded_file)
            st.session_state["df2"] = df_for_visualization
            st.success("CSV uploaded successfully!", icon="✅")
        except Exception as e:
            st.error(f"Unable to read CSV: {e}")

    if df_for_visualization is not None:
        st.dataframe(df_for_visualization.head(20), use_container_width=True)

        try:
            pyg_app = StreamlitRenderer(df_for_visualization)
            pyg_app.explorer()
        except Exception as e:
            st.warning(
                "PygWalker could not start. Basic visualization is still available."
            )
            st.caption(str(e))

        st.subheader("Quick Chart")
        columns = df_for_visualization.columns.tolist()

        if columns:
            x_col = st.selectbox("X-axis", columns, key="quick_x")
            numeric_cols = df_for_visualization.select_dtypes(
                include="number"
            ).columns.tolist()
            y_options = numeric_cols if numeric_cols else columns
            y_col = st.selectbox("Y-axis", y_options, key="quick_y")
            chart_type = st.selectbox(
                "Chart type",
                ["Bar", "Line", "Scatter", "Histogram", "Pie"],
                key="quick_chart",
            )

            try:
                fig = build_chart(
                    df_for_visualization,
                    chart_type,
                    x_col,
                    y_col,
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Unable to create chart: {e}")


with tab3:
    st.markdown("### BI Wizard 🔮")

    if "df" in st.session_state:
        df = st.session_state["df"]
    elif "df2" in st.session_state:
        df = st.session_state["df2"]
    else:
        df = None

    if df is None:
        st.warning(
            "Generate data in Data Agent or upload a CSV in Visual Analyzer first.",
            icon="⚠️",
        )
    else:
        with st.expander("🔎 Dataset Preview"):
            st.dataframe(df.head(10), use_container_width=True)

        prompt = st.text_area(
            "What insights or visualization would you like?",
            "Summarize the most important trends in this dataset.",
        )

        if st.button("Generate BI Insights"):
            if not api_key or llm is None:
                st.error("Please configure an OpenAI API key first.")
            elif prompt.strip():
                with st.spinner("Generating insights..."):
                    try:
                        insights = generate_business_insights(df, prompt, llm)
                        st.subheader("Business Insights")
                        st.write_stream(stream_text(insights))
                    except Exception as e:
                        st.error(f"Unable to generate insights: {e}")
