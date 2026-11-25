# PROJECT DOCUMENTATION
## Task Execution Agent
### Using Python, Ollama, and Streamlit

| Attribute | Details |
| :--- | :--- |
| **Project Type** | Artificial Intelligence / Autonomous Agent |
| **Interface** | Streamlit Web Application (`app.py`) |
| **Agent Backend** | Modular Python Agent (`main.py`) |
| **Model Runtime** | Local Ollama Runtime (Default: `qwen3:4b`) |
| **Built-in Tools** | `calculate`, `write_note`, `search_knowledge_base` |

*Prepared from the implemented `main.py` and `app.py` source files. Where features are not present in the current codebase, they are noted as implementation boundaries or future improvements.*

---

## Contents

1. Project Overview and Abstract
2. Objectives and Key Features
3. Technologies and Project Structure
4. System Architecture and Workflow
5. Installation, Configuration, and Execution
6. Application Module: `app.py`
7. Agent Pipeline Module: `main.py`
8. Data Handling, Tool Execution, and Context Passing
9. Testing Guidance and Troubleshooting
10. Current Implementation Notes and Limitations
11. GitHub Repository Guidance
12. Conclusion

---

## 1. Project Overview and Abstract

**Project Name:** Task Execution Agent using Python, Ollama, and Streamlit.

This project is an interactive AI application that accepts a high-level user goal, breaks it into a logical sequence of steps, and executes each step iteratively using a local language model and Python tools. The system is divided into two Python modules: `main.py` for planning, tool definitions, and step execution, and `app.py` for the Streamlit user interface.

### Abstract

Autonomous task execution agents combine structured planning with iterative tool use to complete multi-step goals. In this implementation, a user enters a task goal into a Streamlit web interface and selects an installed Ollama model. The backend (`LocalTaskExecutionAgent.generate_plan` in `main.py`) prompts the model in JSON mode to generate 2 to 4 actionable steps. Each step is then passed sequentially to `LocalTaskExecutionAgent.execute_step`, which runs a tool-calling loop with access to three local Python functions (`calculate`, `write_note`, and `search_knowledge_base`) while carrying forward accumulated summaries from prior steps. The Streamlit interface presents the generated plan and step-by-step summaries while keeping raw tool execution logs hidden from the end user.

---

## 2. Objectives and Key Features

### Project Objectives
- Implement a modular Task Execution Agent in Python without external orchestration frameworks.
- Decompose user goals into structured, sequential JSON steps using Ollama.
- Execute each step autonomously with access to local Python tools.
- Maintain inter-step context so later steps can use findings and outputs from earlier steps.
- Provide an intuitive Streamlit interface for model selection, goal input, progress status, and result display.
- Prevent duplicate tool calls in the agent loop and keep technical tool logs hidden in the UI.

### Implemented Features
- Automatic discovery of locally installed Ollama models via `ollama.list()`.
- Structured JSON plan generation (`{"steps": [...]}`) via `ollama.chat(..., format="json")`.
- Three built-in callable tools with type hints and docstrings: `calculate`, `write_note`, and `search_knowledge_base`.
- Up to 3 tool-calling iterations per step in `execute_step`.
- System prompt guardrails instructing the model not to repeat identical tool calls after a tool succeeds.
- Clean Streamlit presentation using `st.status`, `st.expander`, and `st.spinner` with tool call boxes omitted.

---

## 3. Technologies and Project Structure

| Technology / Component | Role in This Project |
| :--- | :--- |
| **Python** | Primary programming language for backend agent logic and frontend UI. |
| **Streamlit** | Renders the web application, sidebar settings, status indicators, and expandable step outputs. |
| **Ollama (`ollama` package)** | Connects Python to the local Ollama runtime for model listing and chat completions with tool calling. |
| **JSON (`json` module)** | Parses structured plan responses (`{"steps": [...]}`) from the model. |
| **File I/O (`open`)** | Writes UTF-8 output files to disk when the `write_note` tool is invoked. |

### Project Folder Structure

```text
Task-Execution-Agent/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
└── DOCUMENTATION.md
```

| File | Purpose |
| :--- | :--- |
| `main.py` | Contains tool definitions (`calculate`, `write_note`, `search_knowledge_base`), tool mappings, and `LocalTaskExecutionAgent`. |
| `app.py` | Contains the Streamlit frontend for model selection, task entry, plan rendering, and step execution display. |
| `requirements.txt` | Lists required third-party Python packages (`streamlit` and `ollama`). |
| `README.md` | Quick-start guide and code overview for repository visitors. |
| `DOCUMENTATION.md` | Complete technical documentation formatted for PDF export. |

---

## 4. System Architecture and Workflow

### Architecture Diagram

```text
TASK PLANNING PHASE
-------------------
User enters high-level goal in Streamlit (app.py)
        |
        v
LocalTaskExecutionAgent.generate_plan(goal) [main.py]
        |
        v
ollama.chat(model, prompt, format="json")
        |
        v
Parsed list of 2 to 4 sequential steps


STEP EXECUTION PHASE (FOR EACH STEP)
------------------------------------
LocalTaskExecutionAgent.execute_step(goal, step, accumulated_context) [main.py]
        |
        v
ollama.chat(model, messages, tools=TOOLS_LIST)  [Up to 3 turns]
        |
        +---> Tool calls returned?
        |       |-- Yes --> Run function in AVAILABLE_TOOLS
        |       |           Append {"role": "tool", ...} to messages
        |       |           Repeat turn
        |       |
        |       +-- No  --> Return {"output": msg.content, "tools_used": tool_logs}
        |
        v
Streamlit renders step summary inside st.expander (tool logs hidden)
        |
        v
Append step output to accumulated_context for next step
```

### End-to-End Workflow
1. **Model Discovery:** `app.py` calls `get_local_models()` to populate the sidebar dropdown with installed Ollama models.
2. **Goal Submission:** The user reviews or modifies the goal text area and clicks **Execute Task**.
3. **Plan Generation:** `app.py` invokes `agent.generate_plan(goal)` inside a `st.status` container and displays each step.
4. **Iterative Execution:** `app.py` iterates through `plan_steps`, passing `goal`, `step`, and `accumulated_context` into `agent.execute_step(...)`.
5. **Tool Invocation:** When needed, Ollama invokes `search_knowledge_base`, `calculate`, or `write_note`, receives the tool output, and produces a natural-language step summary.
6. **Result Presentation:** Each step summary appears in its own `st.expander`, followed by a completion banner once all steps finish.

---

## 5. Installation, Configuration, and Execution

### Prerequisites
- Python 3.10 or later installed on the system.
- Ollama installed from `https://ollama.com/` and running locally.
- A tool-capable Ollama model downloaded locally (default: `qwen3:4b`).
- `main.py` and `app.py` saved in the same project folder.

### Step 1 — Install Ollama and Pull the Model

```bash
ollama pull qwen3:4b
```

### Step 2 — Create and Activate a Virtual Environment

```powershell
py -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

### Step 3 — Install Python Dependencies

Create `requirements.txt` with:

```text
streamlit
ollama
```

Install the packages:

```powershell
py -m pip install -r requirements.txt
```

### Step 4 — Run the Application

From the folder containing `app.py` and `main.py`, run:

```powershell
py -m streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 6. Application Module: `app.py`

`app.py` implements the Streamlit user interface, imports `LocalTaskExecutionAgent` from `main.py`, and coordinates the two execution phases.

### Page Configuration and Model Discovery

```python
from main import LocalTaskExecutionAgent

st.set_page_config(page_title="Task Execution Agent", page_icon="⚙️", layout="centered")
```

`get_local_models()` calls `ollama.list()` and returns `[m.model for m in models_info.models]`. If Ollama is unreachable or no models are installed, the sidebar displays a warning and provides a text input defaulting to `"qwen3:4b"`.

### Sidebar and Goal Input
The sidebar displays **Model Settings** and lists the three available tools (`search_knowledge_base`, `calculate`, `write_note`). The main area provides a `st.text_area` pre-populated with a sample multi-step goal and a full-width primary **Execute Task** button.

### Planning and Execution Rendering
1. **Input Validation:** Checks `if not goal.strip():` and stops execution with `st.warning` if blank.
2. **Planning Block:** Runs `agent.generate_plan(goal)` inside `st.status("Generating execution plan...", expanded=True)`. Raises a `ValueError` if an empty list is returned.
3. **Execution Loop:** Iterates over `plan_steps` with `enumerate(plan_steps, 1)`. Each step opens a `st.expander`, runs `agent.execute_step(goal, step, accumulated_context)` under `st.spinner`, displays `result_data["output"]` with `st.markdown`, and appends the step result to `accumulated_context`. Tool logs in `result_data["tools_used"]` are intentionally not rendered in the UI.

---

## 7. Agent Pipeline Module: `main.py`

`main.py` encapsulates the local tools and the `LocalTaskExecutionAgent` class.

### Built-in Tools
- **`calculate(expression: str) -> str`:** Checks that all characters in `expression` belong to `"0123456789+-*/(). "` and evaluates the string with `eval(expression)`. Returns the string result or an error description.
- **`write_note(filename: str, content: str) -> str`:** Opens `filename` in write mode (`encoding="utf-8"`), writes `content`, and returns a confirmation message.
- **`search_knowledge_base(query: str) -> str`:** Searches a mock dictionary containing entries for `"q3 revenue"`, `"server status"`, and `"project alpha"`. Returns matching data or a fallback message instructing the agent to proceed with general knowledge.

### `LocalTaskExecutionAgent` Class
- **`__init__(self, model: str = "qwen3:4b")`:** Stores the target Ollama model name.
- **`generate_plan(self, goal: str) -> list[str]`:** Sends a planning prompt to `ollama.chat` with `format="json"`, parses the JSON string with `json.loads`, and returns `data.get("steps", [])`.
- **`execute_step(self, goal: str, step: str, context: str) -> dict`:** Initializes a system prompt and user prompt containing the overall goal, previous context, and current step. Loops up to 3 times calling `ollama.chat(model=self.model, messages=messages, tools=TOOLS_LIST)`. When `msg.tool_calls` is present, it executes each matching function in `AVAILABLE_TOOLS`, records the call in `tool_logs`, and appends a `"role": "tool"` message. Once the model finishes without further tool calls, it returns `{"output": msg.content, "tools_used": tool_logs}`.

---

## 8. Data Handling, Tool Execution, and Context Passing

- **Structured JSON Planning:** Using `format="json"` ensures the planning step returns parseable JSON containing a `"steps"` array rather than unstructured prose.
- **Sequential Context Accumulation:** `app.py` concatenates each step's summary into `accumulated_context` (`f"\nStep {idx} ({step}): {result_data['output']}"`), enabling multi-step workflows such as retrieving a figure in Step 1, computing a percentage in Step 2, and writing a summary report in Step 3.
- **Local File Side Effects:** Invoking `write_note` creates or overwrites files directly in the working directory where Streamlit was launched.

---

## 9. Testing Guidance and Troubleshooting

### Manual Verification Checklist

| Check | Expected Behavior |
| :--- | :--- |
| Launch via `py -m streamlit run app.py` | Application opens in the browser without `ScriptRunContext` warnings. |
| Empty goal submission | Clicking **Execute Task** with whitespace or empty text displays a warning and halts. |
| Multi-step goal execution | Plan steps appear under **Execution Plan Ready**, followed by step summaries and a success banner. |
| File creation via `write_note` | Target `.txt` file is created in the project directory with the generated report content. |

### Common Troubleshooting
- **`ModuleNotFoundError: No module named 'ollama'`:** Install `ollama` and `streamlit` into the exact Python interpreter used to run Streamlit (`py -m pip install ollama streamlit`).
- **`Python was not found`:** Use the Windows Python launcher (`py`) or disable Windows App Execution Aliases for `python.exe` and `python3.exe`.
- **`ModuleNotFoundError: No module named 'main'` or `File does not exist: app.py`:** Change directory (`cd`) into the folder containing both `main.py` and `app.py` before running Streamlit.
- **`missing ScriptRunContext` warning:** Always run `streamlit run app.py` instead of `python app.py`.

---

## 10. Current Implementation Notes and Limitations

- **Restricted `eval` in `calculate`:** Input characters are filtered to numbers and basic math operators, though a dedicated AST parser would be safer for untrusted inputs.
- **Static Mock Knowledge Base:** `search_knowledge_base` uses a hardcoded Python dictionary rather than an external database or document index.
- **Unrestricted Working-Directory Writes:** `write_note` writes directly to the current working directory without path sandboxing.
- **Three-Turn Step Limit:** `execute_step` caps tool-calling iterations at 3 turns per step and returns `"Step completed successfully."` if no final assistant message is emitted after the third turn.
- **UI Tool Logs Hidden:** `app.py` omits `result_data["tools_used"]` from the UI by design.

---

## 11. GitHub Repository Guidance

### Recommended `.gitignore`

```text
.venv/
__pycache__/
*.py[cod]
.env
```

### Git Commands

```bash
git init
git add main.py app.py requirements.txt README.md DOCUMENTATION.md .gitignore
git commit -m "Add Task Execution Agent project and documentation"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/Task-Execution-Agent.git
git push -u origin main
```

---

## 12. Conclusion

The Task Execution Agent demonstrates an end-to-end local agent workflow using Python, Ollama, and Streamlit. By combining JSON-based task decomposition in `main.py`, local Python tool execution, and sequential context passing behind a clean Streamlit interface in `app.py`, the project serves as a clear foundation for building more advanced autonomous workflows.