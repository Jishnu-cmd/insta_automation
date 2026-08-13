from reelforge.agents.base import BaseAgent
from reelforge.models import JobState
from reelforge.sandbox.runner import SandboxRunner

class CodeAgent(BaseAgent):
    """
    F6 - Code Generation & Execution Agent
    Executes Python code in an isolated sandbox and generates terminal display assets.
    """
    
    def __init__(self):
        super().__init__("CodeAgent")
        self.runner = SandboxRunner(timeout_seconds=5.0)

    def execute(self, state: JobState) -> JobState:
        if not state.script or not state.script.demo_code:
            self.log(state, "No demo code found in script. Generating default code snippet...")
            code_to_run = (
                "import time\n"
                "print('🤖 Flow Tech AI Pipeline Initialized')\n"
                "for i in range(1, 4):\n"
                "    print(f' -> Step {i}: Processing AI Agent Task...')\n"
                "    time.sleep(0.1)\n"
                "print('✅ Execution Finished Successfully!')"
            )
        else:
            code_to_run = state.script.demo_code

        self.log(state, "Executing code snippet in safe isolated sandbox...")
        
        result = self.runner.execute_python_code(code_to_run)
        state.code_result = result

        if result.executed:
            self.log(state, f"Code executed cleanly in {result.execution_time_ms}ms. Terminal card created at: {result.output_image_path}")
        else:
            self.log(state, f"Code execution finished with exit code {result.exit_code}: {result.stderr}")

        if result.output_image_path:
            state.visual_paths.append(result.output_image_path)

        return state
