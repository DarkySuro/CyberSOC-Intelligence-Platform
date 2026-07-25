
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
 
from db import run_query, run_write, call_procedure
from ai_helper import summarize_incident, ask_about_data
 
st.set_page_config(page_title="Security Operations Center", page_icon="🛡️", layout="wide")
 
# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("🛡️ SOC Dashboard")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Incidents", "Brute-Force Detection", "Assets", "Add Incident", "Ad-hoc Query", "AI Assistant"],
)
 
# ---------------------------------------------------------------------------
# Overview page
# ---------------------------------------------------------------------------
if page == "Overview":
    st.title("Overview")
 
    col1, col2, col3, col4 = st.columns(4)
 
    total_incidents = run_query("SELECT COUNT(*) AS n FROM Incidents")["n"][0]
    open_incidents = run_query(
        "SELECT COUNT(*) AS n FROM Incidents WHERE Status IN ('Open','Investigating')"
    )["n"][0]
    critical_assets = run_query(
        "SELECT COUNT(*) AS n FROM Assets WHERE Criticality = 'Critical'"
    )["n"][0]
    failed_today = run_query(
        "SELECT COUNT(*) AS n FROM AccessLogs WHERE Success = FALSE AND DATE(Timestamp) = CURDATE()"
    )["n"][0]
 
    col1.metric("Total Incidents", int(total_incidents))
    col2.metric("Open / Investigating", int(open_incidents))
    col3.metric("Critical Assets", int(critical_assets))
    col4.metric("Failed Logins Today", int(failed_today))
 
    st.divider()
 
    st.subheader("Incidents by Severity")
    sev_df = run_query(
        "SELECT Severity, COUNT(*) AS Count FROM Incidents GROUP BY Severity"
    )
    if not sev_df.empty:
        chart = (
            alt.Chart(sev_df)
            .mark_bar()
            .encode(
                x=alt.X("Severity", sort=["Low", "Medium", "High", "Critical"]),
                y="Count",
                color=alt.Color("Severity", scale=alt.Scale(scheme="redyellowgreen", reverse=True)),
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No incident data yet.")
 
# ---------------------------------------------------------------------------
# Incidents page
# ---------------------------------------------------------------------------
elif page == "Incidents":
    st.title("Incidents")
 
    col1, col2 = st.columns(2)
    severity_filter = col1.multiselect(
        "Severity", ["Low", "Medium", "High", "Critical"], default=[]
    )
    status_filter = col2.multiselect(
        "Status", ["Open", "Investigating", "Resolved", "Closed"], default=[]
    )
 
    sql = "SELECT * FROM Incidents WHERE 1=1"
    params = []
    if severity_filter:
        placeholders = ",".join(["%s"] * len(severity_filter))
        sql += f" AND Severity IN ({placeholders})"
        params.extend(severity_filter)
    if status_filter:
        placeholders = ",".join(["%s"] * len(status_filter))
        sql += f" AND Status IN ({placeholders})"
        params.extend(status_filter)
    sql += " ORDER BY DetectedAt DESC"
 
    df = run_query(sql, tuple(params))
    st.dataframe(df, use_container_width=True)
 
    st.divider()
    st.subheader("Suspicious Activity View")
    st.caption("Pulls from the `SuspiciousActivity` view defined in the schema.")
    try:
        st.dataframe(run_query("SELECT * FROM SuspiciousActivity"), use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load SuspiciousActivity view: {e}")
 
# ---------------------------------------------------------------------------
# Brute-Force Detection page
# ---------------------------------------------------------------------------
elif page == "Brute-Force Detection":
    st.title("Brute-Force Detection")
 
    threshold = st.slider("Failed-attempt threshold", min_value=1, max_value=10, value=3)
 
    df = run_query(
        """
        SELECT EmployeeID, AssetID, COUNT(*) AS FailedAttempts
        FROM AccessLogs
        WHERE Success = FALSE
        GROUP BY EmployeeID, AssetID
        HAVING COUNT(*) >= %s
        ORDER BY FailedAttempts DESC
        """,
        (threshold,),
    )
    st.dataframe(df, use_container_width=True)
 
    if not df.empty:
        chart = (
            alt.Chart(df)
            .mark_bar(color="#d62728")
            .encode(
                x=alt.X("EmployeeID:N", title="Employee ID"),
                y="FailedAttempts",
                tooltip=["EmployeeID", "AssetID", "FailedAttempts"],
            )
        )
        st.altair_chart(chart, use_container_width=True)
 
    st.divider()
    st.subheader("Check a specific employee")
    emp_id = st.number_input("Employee ID", min_value=1, step=1)
    check_threshold = st.number_input("Alert threshold", min_value=1, step=1, value=3)
    if st.button("Run LockAccountAfterNFailures"):
        try:
            results = call_procedure("LockAccountAfterNFailures", (emp_id, check_threshold))
            for r in results:
                st.dataframe(r)
        except Exception as e:
            st.error(f"Procedure call failed: {e}")
 
# ---------------------------------------------------------------------------
# Assets page
# ---------------------------------------------------------------------------
elif page == "Assets":
    st.title("Assets")
 
    df = run_query("SELECT * FROM Assets ORDER BY Criticality DESC")
    st.dataframe(df, use_container_width=True)
 
    if not df.empty:
        crit_counts = df["Criticality"].value_counts().reset_index()
        crit_counts.columns = ["Criticality", "Count"]
        pie = (
            alt.Chart(crit_counts)
            .mark_arc()
            .encode(theta="Count", color="Criticality", tooltip=["Criticality", "Count"])
        )
        st.altair_chart(pie, use_container_width=True)
 
# ---------------------------------------------------------------------------
# Add Incident page
# ---------------------------------------------------------------------------
elif page == "Add Incident":
    st.title("Add a New Incident")
 
    with st.form("add_incident_form"):
        title = st.text_input("Title")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
        detected_at = st.datetime_input("Detected At", value=datetime.now())
        asset_id = st.number_input("Linked Asset ID (optional, 0 to skip)", min_value=0, step=1)
 
        submitted = st.form_submit_button("Create Incident")
 
        if submitted:
            if not title:
                st.error("Title is required.")
            else:
                run_write(
                    """
                    INSERT INTO Incidents (Title, Status, Severity, DetectedAt)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (title, status, severity, detected_at),
                )
                new_id_df = run_query("SELECT LAST_INSERT_ID() AS id")
                new_id = int(new_id_df["id"][0])
 
                if asset_id:
                    run_write(
                        "INSERT INTO IncidentAssets (IncidentID, AssetID) VALUES (%s, %s)",
                        (new_id, asset_id),
                    )
 
                st.success(f"Incident #{new_id} created.")
 
# ---------------------------------------------------------------------------
# Ad-hoc Query page (read-only guard)
# ---------------------------------------------------------------------------
elif page == "Ad-hoc Query":
    st.title("Ad-hoc SELECT Query")
    st.caption("Only SELECT statements are allowed here — this box does not run writes.")
 
    query = st.text_area("SQL", value="SELECT * FROM Incidents LIMIT 20;", height=120)
 
    if st.button("Run"):
        cleaned = query.strip().rstrip(";")
        if not cleaned.lower().startswith("select"):
            st.error("Only SELECT statements are permitted in this panel.")
        else:
            try:
                st.dataframe(run_query(cleaned), use_container_width=True)
            except Exception as e:
                st.error(f"Query failed: {e}")
 
# ---------------------------------------------------------------------------
# AI Assistant page (Gemini)
# ---------------------------------------------------------------------------
elif page == "AI Assistant":
    st.title("AI Assistant")
 
    tab1, tab2 = st.tabs(["Summarize an Incident", "Ask About the Data"])
 
    with tab1:
        incidents_df = run_query("SELECT * FROM Incidents ORDER BY DetectedAt DESC")
        if incidents_df.empty:
            st.info("No incidents to summarize yet.")
        else:
            options = incidents_df["IncidentID"].tolist()
            chosen_id = st.selectbox("Choose an Incident ID", options)
            if st.button("Generate Summary"):
                row = incidents_df[incidents_df["IncidentID"] == chosen_id].iloc[0].to_dict()
                try:
                    with st.spinner("Asking Gemini..."):
                        summary = summarize_incident(row)
                    st.success(summary)
                except Exception as e:
                    st.error(f"AI call failed: {e}")
 
    with tab2:
        st.write("Ask a question about current incidents (answers are grounded in the live query results, not invented).")
        question = st.text_input("Your question", value="Which incidents are still open and what do they have in common?")
        if st.button("Ask"):
            context_df = run_query("SELECT * FROM Incidents")
            try:
                with st.spinner("Asking Gemini..."):
                    answer = ask_about_data(question, context_df)
                st.write(answer)
            except Exception as e:
                st.error(f"AI call failed: {e}")
 