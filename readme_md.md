# ⚙️ Task Execution Agent using Python, Ollama, and Streamlit

A local Artificial Intelligence application that implements an autonomous **Task Execution Agent**. Given a high-level user goal, the agent decomposes the objective into sequential actionable steps and executes each step using local Python tools and Ollama models.

## Abstract

Autonomous task execution agents break down complex user objectives into structured, multi-step workflows and execute them iteratively while preserving context across steps.

This project implements a Task Execution Agent with a modular backend (`main.py`) and an interactive Streamlit web frontend (`app.py`). When a user submits a goal, the agent generates a JSON-formatted step plan via Ollama, then runs each step through a tool-calling loop with access to local Python functions (`calculate`, `write_note`, and `search_knowledge_base`).

In the Streamlit interface, tool execution logs are kept hidden so the display focuses cleanly on step-by-step summaries and overall task completion, while the backend prevents redundant tool invocations once a tool succeeds.

## Project Objectives

- Build an autonomous Task Execution Agent in Python powered by Ollama.
- Decompose high-level user goals into a structured sequence of 2 to 4 actionable steps.
- Execute steps sequentially while passing accumulated context from earlier steps into subsequent steps.
- Provide local callable tools for arithmetic calculations, file generation, and internal knowledge-base lookups.
- Deliver a clean Streamlit web interface for model selection, goal input, plan tracking, and result summaries.
- Hide raw tool execution logs in the UI while preventing duplicate tool calls in the agent loop.

## Technologies Used

- **Python** — core programming language for the agent logic and web application.
- **Streamlit** — interactive web interface for model selection, task input, status tracking, and expandable step results.
- **Ollama** — local model runtime used to list installed models and execute chat completions with tool calling.
- **JSON (`json` standard library)** — parses structured execution plans (`{"steps": [...]}`) and tool arguments.

## Project Structure

```text
Task-Execution-Agent/
│
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

**File descriptions:**

| File | Purpose |
|---|---|
| `main.py` | Defines local tools (`calculate`, `write_note`, `search_knowledge_base`) and `LocalTaskExecutionAgent` (`generate_plan`, `execute_step`) |
| `app.py` | Streamlit application for selecting a local model, entering goals, displaying the execution plan, and rendering step summaries |
| `requirements.txt` | Python dependencies required for the project (`streamlit`, `ollama`) |
| `README.md` | Project overview, setup instructions, code walkthrough, and usage guide |

## How the Project Works

1. **Select Model & Enter Goal:** Users choose an installed Ollama model from the Streamlit sidebar (defaulting to `qwen3:4b` if none are detected) and enter a task goal in the main text area.
2. **Generate Execution Plan:** `LocalTaskExecutionAgent.generate_plan(goal)` in `main.py` prompts Ollama with `format="json"` to return 2 to 4 actionable steps and parses `data.get("steps", [])`.
3. **Display Plan Status:** `app.py` renders the planned steps inside an expandable `st.status` container and marks planning as complete.
4. **Execute Steps Sequentially:** For each step in the plan, `app.py` calls `agent.execute_step(goal, step, accumulated_context)`.
5. **Run Tool-Calling Loop:** Inside `execute_step`, the model runs up to 3 iterations with `ollama.chat(..., tools=TOOLS_LIST)`. If `tool_calls` are returned, the corresponding Python functions in `AVAILABLE_TOOLS` execute and append `role: "tool"` messages to the conversation.
6. **Accumulate Context & Display Results:** Each step's summary output is displayed inside a `st.expander` (with raw tool call logs hidden from the UI) and appended to `accumulated_context` for the next step.

## Installation and Setup

### 1. Install Python

Install Python 3.10 or later. Check your installation in PowerShell or terminal:

```powershell
py --version
```

### 2. Install Ollama

Download and install Ollama from:

https://ollama.com/

Ensure the Ollama background service is running.

### 3. Download a Tool-Capable Model

Open your terminal and pull a model that supports JSON formatting and tool calling, such as `qwen3:4b`:

```powershell
ollama pull qwen3:4b
```

### 4. Create and Activate a Virtual Environment

In your project directory on Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5. Create `requirements.txt` and Install Dependencies

Create a `requirements.txt` file with the following contents:

```text
streamlit
ollama
```

Install the dependencies:

```powershell
py -m pip install -r requirements.txt
```

## Run the Application

Ensure Ollama is running and your terminal is inside the folder containing both `main.py` and `app.py`. Launch the application with:

```powershell
py -m streamlit run app.py
```

Open the local URL displayed in the terminal, typically:

```text
http://localhost:8501
```

### How to Use the Application

1. Open the Task Execution Agent in your browser.
2. Go to the sidebar under **Model Settings** and select an installed Ollama model.
3. Review or edit the goal inside **Define Your Task / Goal**.
4. Click **Execute Task**.
5. View the generated steps in the planning status box.
6. Read the summary output for each step inside the expandable sections under **Execution Results**.

## `app.py` — Line-by-Line Code Guide

### 1. Import Libraries

```python
import streamlit as st
import ollama
from main import LocalTaskExecutionAgent
```

- `streamlit` builds the web interface.
- `ollama` queries locally installed models via `ollama.list()`.
- `LocalTaskExecutionAgent` imports the planning and execution agent class from `main.py`.

### 2. Configure the Streamlit Page

```python
st.set_page_config(page_title="Task Execution Agent", page_icon="⚙️", layout="centered")
```

Sets the browser tab title, icon, and centered page layout.

### 3. Discover Installed Local Models

```python
def get_local_models() -> list[str]:
    try:
        models_info = ollama.list()
        return [m.model for m in models_info.models]
    except Exception:
        return []
```

Queries Ollama for locally available models and safely returns an empty list if the runtime is unreachable.

### 4. Sidebar Configuration

```python
with st.sidebar:
    st.header("Model Settings")
    installed_models = get_local_models()
```

Displays a dropdown of installed models (or a fallback text input defaulting to `"qwen3:4b"`) along with a summary of available tools.

### 5. Planning Phase

```python
with st.status("Generating execution plan...", expanded=True) as status:
    plan_steps = agent.generate_plan(goal)
```

Calls `agent.generate_plan(goal)`, validates that steps were returned, renders each step, and updates the status indicator.

### 6. Step-by-Step Execution Phase

```python
for idx, step in enumerate(plan_steps, 1):
    with st.expander(f"Step {idx}: {step}", expanded=True):
        with st.spinner("Executing step..."):
            result_data = agent.execute_step(goal, step, accumulated_context)

        st.markdown(result_data["output"])
        accumulated_context += f"\nStep {idx} ({step}): {result_data['output']}"
```

Executes each step sequentially, displays only the step summary (`result_data["output"]`) while hiding tool logs, and appends the output to `accumulated_context`.

## `main.py` — Line-by-Line Code Guide

### 1. Local Tool Definitions

```python
def calculate(expression: str) -> str:
def write_note(filename: str, content: str) -> str:
def search_knowledge_base(query: str) -> str:
```

- `calculate`: Validates allowed arithmetic characters (`0-9+-*/(). `) and evaluates math expressions.
- `write_note`: Writes UTF-8 text content to a local file.
- `search_knowledge_base`: Performs case-insensitive lookups against a built-in dictionary of sample company metrics and project records.

### 2. Tool Registry

```python
TOOLS_LIST = [calculate, write_note, search_knowledge_base]
AVAILABLE_TOOLS = {func.__name__: func for func in TOOLS_LIST}
```

Registers the Python functions so Ollama can inspect their type hints and docstrings for tool calling, and maps function names to callables for execution.

### 3. Plan Generation (`generate_plan`)

```python
response = ollama.chat(
    model=self.model,
    messages=[{"role": "user", "content": prompt}],
    format="json",
)
data = json.loads(response.message.content)
return data.get("steps", [])
```

Requests a JSON object containing a `"steps"` list of 2 to 4 actionable steps from the selected Ollama model.

### 4. Step Execution & Tool Loop (`execute_step`)

```python
for _ in range(3):
    response = ollama.chat(
        model=self.model,
        messages=messages,
        tools=TOOLS_LIST,
    )
```

Runs up to 3 tool-calling turns per step. When `msg.tool_calls` is returned, each tool function is executed with `**func_args`, logged in `tool_logs`, and fed back into `messages` with `"role": "tool"`. The system prompt instructs the model not to repeat identical tool calls after a tool succeeds.

## System Architecture

```text
             USER
               |
               v
       STREAMLIT APP (app.py)
               |
               v
     MODEL SELECTION & GOAL
               |
               v
   generate_plan(goal) [main.py]
       (Ollama JSON Mode)
               |
               v
      ORDERED STEP LIST
               |
               v
    FOR EACH STEP IN PLAN:
               |
               v
 execute_step(goal, step, context)
               |
               +---> Tool Call Required? ---> Execute Python Tool
               |        (Up to 3 Turns)       (calculate / write_note /
               |                               search_knowledge_base)
               v
     STEP SUMMARY OUTPUT
               |
               v
   APPEND TO ACCUMULATED CONTEXT
               |
               v
  DISPLAY RESULTS IN STREAMLIT UI
```

## Common Issues

- **`ModuleNotFoundError: No module named 'ollama'`:** Install dependencies into the exact Python environment running Streamlit (`py -m pip install ollama streamlit`).
- **`Python was not found` / Microsoft Store shortcut:** Use the `py` launcher (`py -m streamlit run app.py`) or disable Windows App Execution Aliases for `python.exe` and `python3.exe`.
- **`ModuleNotFoundError: No module named 'main'`:** Navigate (`cd`) into the directory containing both `main.py` and `app.py` before running `streamlit run app.py`.
- **`missing ScriptRunContext` warning:** Start the app with `streamlit run app.py`, not `python app.py`.
- **`File does not exist: app.py`:** Verify the filename is `app.py` (not `app.py.txt`) and that your terminal is in the project folder.
- **Empty plan returned:** Confirm Ollama is running and select a tool-capable model such as `qwen3:4b`.

## Future Improvements

- Replace `eval` in `calculate` with a safe AST-based math expression parser.
- Connect `search_knowledge_base` to a real database, document store, or web search tool.
- Add directory sandboxing for `write_note` so generated files are saved in a dedicated output folder.
- Add an optional UI toggle to inspect tool execution logs when debugging.
- Support saving and exporting full execution reports from the Streamlit interface.

## How to Upload the Project to GitHub

1. Create a `.gitignore` file in your project root:
   ```text
   .venv/
   __pycache__/
   *.py[cod]
   .env
   ```
2. Initialize Git and push your project files:
   ```bash
   git init
   git add main.py app.py requirements.txt README.md .gitignore
   git commit -m "Initial commit: Task Execution Agent"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/Task-Execution-Agent.git
   git push -u origin main
   ```

## Conclusion

This project demonstrates how to build a modular, local Task Execution Agent using Python, Ollama, and Streamlit. By separating structured task planning and tool execution (`main.py`) from the user interface (`app.py`), the application provides a clean, extensible foundation for multi-step AI automation.