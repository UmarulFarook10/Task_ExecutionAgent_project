import streamlit as st
import ollama
from main import LocalTaskExecutionAgent

st.set_page_config(page_title="Task Execution Agent", page_icon="⚙️", layout="centered")

st.title("⚙️ Task Execution Agent")
st.markdown("Enter a high-level goal. The agent plans the steps, runs tools, and summarizes the results.")


def get_local_models() -> list[str]:
    try:
        models_info = ollama.list()
        return [m.model for m in models_info.models]
    except Exception:
        return []


# Sidebar Configuration
with st.sidebar:
    st.header("Model Settings")
    installed_models = get_local_models()

    if installed_models:
        model_choice = st.selectbox("Installed Model", installed_models)
    else:
        st.warning("Could not connect to the local runtime or no models found.")
        model_choice = st.text_input("Model Name", value="qwen3:4b")

    st.divider()
    st.subheader("Available Tools")
    st.markdown(
        """
    - `search_knowledge_base`: Queries internal metrics and project details.
    - `calculate`: Evaluates math expressions.
    - `write_note`: Saves text output to local files.
    """
    )

# Main Input Area
default_prompt = (
    "Find our Q3 revenue, calculate 15% of it for the team bonus pool, "
    "and write a summary report to bonus_report.txt."
)
goal = st.text_area("Define Your Task / Goal", value=default_prompt, height=100)

if st.button("Execute Task", type="primary", use_container_width=True):
    if not goal.strip():
        st.warning("Please enter a goal for the agent.")
        st.stop()

    agent = LocalTaskExecutionAgent(model=model_choice)

    # Phase 1: Planning
    with st.status("Generating execution plan...", expanded=True) as status:
        try:
            plan_steps = agent.generate_plan(goal)
            if not plan_steps:
                raise ValueError("Model returned an empty plan. Try another tool-capable model.")
            for idx, step in enumerate(plan_steps, 1):
                st.write(f"**Step {idx}:** {step}")
            status.update(label="Execution Plan Ready", state="complete")
        except Exception as e:
            status.update(label="Planning Failed", state="error")
            st.error(f"Error: {e}")
            st.stop()

    # Phase 2: Step-by-Step Execution
    st.subheader("Execution Results")
    accumulated_context = ""

    for idx, step in enumerate(plan_steps, 1):
        with st.expander(f"Step {idx}: {step}", expanded=True):
            with st.spinner("Executing step..."):
                result_data = agent.execute_step(goal, step, accumulated_context)

            st.markdown(result_data["output"])
            accumulated_context += f"\nStep {idx} ({step}): {result_data['output']}"

    st.success("All tasks executed successfully.")