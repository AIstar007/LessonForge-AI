import streamlit as st
import pandas as pd
from service import run_agent
from memory import MemoryStore

st.set_page_config(page_title="Self-Evaluating Lesson Agent", page_icon="🤖", layout="wide")

st.title("🤖 Self-Evaluating Lesson Content Generator")
st.caption("Generate → Evaluate → Learn → Regenerate")

with st.sidebar:
    st.header("Workflow")
    st.code("""Topic
  ↓
Generate
  ↓
Evaluate
  ├── PASS → Ship
  └── FAIL → Memory → Retry
                    ↓
                 Max 2 retries""")
    inject_error = st.checkbox("Inject deliberate error for demo")

topic = st.text_input("Lesson topic", value="Introduction to RAG")

if st.button("Generate and Evaluate", type="primary"):
    if not topic.strip():
        st.error("Please enter a topic.")
    else:
        with st.spinner("Running agentic workflow..."):
            try:
                result = run_agent(topic, inject_error)
            except Exception as exc:
                st.exception(exc)
                st.stop()

        c1, c2, c3 = st.columns(3)
        c1.metric("Status", result["status"])
        c2.metric("Attempts", result["attempts_used"])
        c3.metric("Failed Attempts", len(result["rejection_log"]))

        st.subheader("📚 Final Lesson")
        st.markdown(result["lesson"])

        st.subheader("🧪 Quality Gate")
        evaluation = result["evaluation"]
        rows = []
        for name, item in evaluation["checks"].items():
            rows.append({
                "Checkpoint": name,
                "Result": "PASS" if item["passed"] else "FAIL",
                "Reason": item["reason"],
                "Recommended Fix": item["fix"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.subheader("🔁 Rejection Log")
        if result["rejection_log"]:
            for entry in result["rejection_log"]:
                with st.expander(f"Attempt {entry['attempt']} rejected"):
                    for check, reason, fix in zip(
                        entry["failed_checks"],
                        entry["reasons"],
                        entry["changes_requested"]
                    ):
                        st.error(f"{check}: {reason}")
                        st.info(f"Fix applied on retry: {fix}")
        else:
            st.success("First attempt passed every hard checkpoint.")

        st.subheader("🧠 Memory Used")
        for pattern in result["learned_patterns_used"]:
            st.write("•", pattern)

st.divider()
st.subheader("📊 Recent Runs")
runs = MemoryStore().recent_runs()
if runs:
    df = pd.DataFrame(runs, columns=["Run ID", "Topic", "Status", "Attempts", "Created At"])
    st.dataframe(df, use_container_width=True)
else:
    st.caption("No previous runs yet.")
