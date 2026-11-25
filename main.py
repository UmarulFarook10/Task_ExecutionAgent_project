import json
import ollama


# ---------------------------------------------------------
# 1. Define Tools Available to the Agent
# ---------------------------------------------------------
def calculate(expression: str) -> str:
    """Evaluates a basic mathematical expression.

    Args:
        expression: Math expression to evaluate, e.g., '1450000 * 0.15'
    """
    try:
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression."
        return str(eval(expression))
    except Exception as e:
        return f"Calculation error: {str(e)}"


def write_note(filename: str, content: str) -> str:
    """Saves text content to a local file.

    Args:
        filename: Name of the file, e.g., 'report.txt'
        content: Text content to save inside the file
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote content to '{filename}'."
    except Exception as e:
        return f"File write error: {str(e)}"


def search_knowledge_base(query: str) -> str:
    """Search internal company knowledge base for metrics, statuses, or project details.

    Args:
        query: Search keywords such as 'q3 revenue' or 'project alpha'
    """
    mock_db = {
        "q3 revenue": "Q3 Revenue was $1.45M, up 12% from Q2.",
        "server status": "All production servers are operational (99.98% uptime).",
        "project alpha": "Project Alpha deadline is December 15. Lead: Sarah Jenkins.",
    }
    for key, val in mock_db.items():
        if key in query.lower():
            return val
    return "No specific internal records found. Proceed using general knowledge."


TOOLS_LIST = [calculate, write_note, search_knowledge_base]
AVAILABLE_TOOLS = {func.__name__: func for func in TOOLS_LIST}


# ---------------------------------------------------------
# 2. Task Execution Agent Class
# ---------------------------------------------------------
class LocalTaskExecutionAgent:
    def __init__(self, model: str = "qwen3:4b"):
        self.model = model

    def generate_plan(self, goal: str) -> list[str]:
        """Breaks the user's goal down into sequential executable steps."""
        prompt = (
            "You are a Task Planning module. Break the following goal down into a concise, "
            "logical list of 2 to 4 actionable steps. Return ONLY a JSON object with a 'steps' key "
            "containing a list of strings.\n\n"
            f"Goal: {goal}"
        )
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format="json",
        )
        data = json.loads(response.message.content)
        return data.get("steps", [])

    def execute_step(self, goal: str, step: str, context: str) -> dict:
        """Executes a single step, calling Python tools if required."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an autonomous Task Execution Agent. Execute the current step toward the main goal. "
                    "Use your available tools when necessary. Once a tool succeeds, do NOT call the same tool again "
                    "with the same arguments—immediately provide a clear, concise summary of what you did."
                ),
            },
            {
                "role": "user",
                "content": f"Overall Goal: {goal}\nPrevious Context:\n{context}\n\nCurrent Step to Execute: {step}",
            },
        ]

        tool_logs = []

        # Allow up to 3 tool-calling turns per step
        for _ in range(3):
            response = ollama.chat(
                model=self.model,
                messages=messages,
                tools=TOOLS_LIST,
            )
            msg = response.message
            messages.append(msg)

            if not msg.tool_calls:
                return {"output": msg.content, "tools_used": tool_logs}

            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                func_args = tool_call.function.arguments

                tool_func = AVAILABLE_TOOLS.get(func_name)
                result = tool_func(**func_args) if tool_func else "Tool not found."

                tool_logs.append(
                    {
                        "tool": func_name,
                        "args": func_args,
                        "result": result,
                    }
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": func_name,
                        "content": str(result),
                    }
                )

        return {"output": "Step completed successfully.", "tools_used": tool_logs}