---
name: CoAct
agent: CodeActAgent
require_env_var:
    SANDBOX_ENV_COACT_TOKEN: "Set up your CoAct environment by configuring SANDBOX_ENV_COACT_TOKEN with a valid token or key for interacting with the CoAct system."
---

# CoAct Workflow for Autonomous Agent Collaboration

## Overview

This document outlines the workflow implemented using the CoAct framework described in the paper:

**X. Hou, M. Yang, W. Jiao, X. Wang, Z. Tu, and W. X. Zhao, “CoAct: A Global-Local Hierarchy for Autonomous Agent Collaboration,” June 2024, arXiv:2406.13381 [cs]. [Online]. Available: [http://arxiv.org/abs/2406.13381](http://arxiv.org/abs/2406.13381)**

## Workflow Components

### 1. GlobalPlanningAgent

The `GlobalPlanningAgent` is responsible for the high-level planning of tasks. Its primary functions include:

- **Task Decomposition:** Breaking down a main task into manageable phases.
- **Task Assignment:** Assigning subtasks to a `LocalExecutionAgent`.
- **Progress Review:** Evaluating feedback from executed tasks and deciding whether replanning is necessary.
- **Guidance Provision:** Offering guidance to the `LocalExecutionAgent` based on feedback.

#### Key Methods:

- `decompose_task(task: str) -> list`: Decomposes the main task into phases.
- `assign_tasks(phases: list) -> dict`: Assigns subtasks to be executed by the `LocalExecutionAgent`.
- `review_progress(feedback: list) -> list or None`: Reviews feedback and triggers replanning if necessary.
- `provide_guidance(feedback: str) -> str`: Provides guidance to the `LocalExecutionAgent` based on feedback.

### 2. LocalExecutionAgent

The `LocalExecutionAgent` is responsible for executing the tasks assigned by the `GlobalPlanningAgent`. Its primary functions include:

- **Subtask Execution:** Carrying out the subtasks.
- **Feedback Collection:** Gathering feedback on the execution results.
- **Replanning:** Initiating replanning in collaboration with the `GlobalPlanningAgent` if errors are encountered.

#### Key Methods:

- `execute_subtask(subtask: str) -> str`: Executes a subtask and returns the result.
- `collect_feedback(result: str) -> str`: Collects and returns feedback based on the execution result.
- `replan_if_necessary(feedback: str, global_agent: GlobalPlanningAgent) -> dict or None`: Initiates replanning if feedback indicates errors.

## Simulated Workflow Example

The following steps simulate the collaboration between the `GlobalPlanningAgent` and the `LocalExecutionAgent`:

1. **Task Decomposition:**
   - The `GlobalPlanningAgent` decomposes the main task into multiple phases.

2. **Task Assignment:**
   - The `GlobalPlanningAgent` assigns subtasks to the `LocalExecutionAgent`.

3. **Task Execution:**
   - The `LocalExecutionAgent` executes each subtask and collects feedback.

4. **Guidance and Replanning:**
   - The `GlobalPlanningAgent` reviews feedback and provides guidance or triggers replanning if errors are encountered.

5. **Finalization:**
   - All tasks and subtasks are executed and feedback is collected.

### Example Code Snippet:

```python
# Initialize agents
global_agent = GlobalPlanningAgent()
local_agent = LocalExecutionAgent()

# Decompose the main task into phases
phases = global_agent.decompose_task("Main task")
tasks = global_agent.assign_tasks(phases)

# Execute tasks and collect feedback
for phase, subtasks in tasks.items():
    for subtask in subtasks:
        result = local_agent.execute_subtask(subtask)
        feedback = local_agent.collect_feedback(result)
        guidance = global_agent.provide_guidance(feedback)
        replanned_tasks = local_agent.replan_if_necessary(feedback, global_agent)
        if replanned_tasks:
            for replanned_phase, replanned_subtasks in replanned_tasks.items():
                for replanned_subtask in replanned_subtasks:
                    result = local_agent.execute_subtask(replanned_subtask)
                    feedback = local_agent.collect_feedback(result)
                    guidance = global_agent.provide_guidance(feedback)

# Final output
print("All tasks and subtasks executed and feedback collected.")
```

## Important Notes

- **Task Decomposition:** Ensure tasks are decomposed into meaningful phases to facilitate effective collaboration.
- **Error Handling:** The system includes error handling, where the `LocalExecutionAgent` can trigger replanning if an error is encountered.
- **Feedback Loop:** Continuous feedback between the `LocalExecutionAgent` and `GlobalPlanningAgent` ensures that guidance and adjustments are made throughout the process.
