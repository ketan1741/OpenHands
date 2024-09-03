import sys

sys.path.insert(
    1, '/Users/ketan/Ketan Files/CMU Study/OpenDevin/Contributions/OpenHands/'
)

from codeact_agent import CodeActAgent

from openhands.controller.state.state import State
from openhands.core.config import AgentConfig, LLMConfig
from openhands.core.schema import AgentState
from openhands.llm.llm import LLM


class GlobalPlanningAgent:
    def __init__(self, code_act_agent, state):
        self.code_act_agent = code_act_agent
        self.state = state

    def decompose_task(self, task):
        prompt = f"Decompose the task '{task}' into manageable phases."
        print(f'GlobalPlanningAgent: Decomposing task: {task}')

        # Update state with task and prompt
        self.state.inputs['task'] = task
        self.state.inputs['prompt'] = prompt
        self.state.iteration += 1

        # Pass the state to the code_act_agent
        action = self.code_act_agent.step(self.state)
        phases = action  # Assuming the action contains the decomposed phases

        # Store phases in state
        self.state.outputs['phases'] = phases
        return phases

    def assign_tasks(self, phases):
        prompt = f'Assign subtasks for the following phases: {phases}'
        print(f'GlobalPlanningAgent: Assigning tasks for phases: {phases}')

        # Update state with phases and prompt
        self.state.inputs['phases'] = phases
        self.state.inputs['prompt'] = prompt
        self.state.iteration += 1

        # Pass the state to the code_act_agent
        action = self.code_act_agent.step(self.state)
        tasks = action  # Assuming the action contains the assigned tasks

        # Store tasks in state
        self.state.outputs['tasks'] = tasks
        return tasks

    def review_progress(self, feedback):
        prompt = f'Review the progress based on the following feedback: {feedback}'
        print(f'GlobalPlanningAgent: Reviewing progress: {feedback}')

        # Update state with feedback and prompt
        self.state.inputs['feedback'] = feedback
        self.state.inputs['prompt'] = prompt
        self.state.iteration += 1

        # Pass the state to the code_act_agent
        action = self.code_act_agent.step(self.state)
        review_decision = action  # Assuming the action contains the review decision

        # Store review decision in state
        self.state.outputs['review_decision'] = review_decision
        return review_decision

    def provide_guidance(self, feedback):
        prompt = f'Provide guidance based on the following feedback: {feedback}'
        print(f'GlobalPlanningAgent: Providing guidance: {feedback}')

        # Update state with guidance feedback and prompt
        self.state.inputs['guidance_feedback'] = feedback
        self.state.inputs['prompt'] = prompt
        self.state.iteration += 1

        # Pass the state to the code_act_agent
        action = self.code_act_agent.step(self.state)
        guidance = action  # Assuming the action contains the guidance

        # Store guidance in state
        self.state.outputs['guidance'] = guidance
        return guidance


class LocalExecutionAgent:
    def __init__(self, code_act_agent, state):
        self.code_act_agent = code_act_agent
        self.state = state

    def execute_subtask(self, subtask):
        prompt = f'Execute the following subtask: {subtask}'
        print(f'LocalExecutionAgent: Executing subtask: {subtask}')

        # Update state with subtask and prompt
        self.state.inputs['subtask'] = subtask
        self.state.inputs['prompt'] = prompt
        self.state.local_iteration += 1

        # Pass the state to the code_act_agent
        action = self.code_act_agent.step(self.state)
        result = action  # Assuming the action contains the execution result

        # Store result in state
        self.state.outputs['result'] = result
        return result

    def collect_feedback(self, result):
        prompt = f'Collect feedback for the following result: {result}'
        print(f'LocalExecutionAgent: Collecting feedback for result: {result}')

        # Update state with result and prompt
        self.state.inputs['result'] = result
        self.state.inputs['prompt'] = prompt
        self.state.local_iteration += 1

        # Pass the state to the code_act_agent
        action = self.code_act_agent.step(self.state)
        feedback = action  # Assuming the action contains the feedback

        # Store feedback in state
        self.state.outputs['feedback'] = feedback
        return feedback

    def replan_if_necessary(self, feedback, guidance, global_agent):
        prompt = f'Replan if necessary based on the following feedback: {feedback} and Guidance: {guidance}'
        print(f'LocalExecutionAgent: Replanning if necessary: {feedback}')

        # Update state with feedback and prompt
        self.state.inputs['replan_feedback'] = feedback
        self.state.inputs['prompt'] = prompt
        self.state.local_iteration += 1

        # Pass the state to the code_act_agent
        if 'Error' in feedback:
            new_phases = global_agent.review_progress(feedback)
            if new_phases:
                # Update state with new phases and tasks
                tasks = global_agent.assign_tasks(new_phases)
                self.state.outputs['replan_tasks'] = tasks
                return tasks
        return None


class CoActManager:
    def __init__(self, global_agent, local_agent, code_act_agent, state):
        self.global_agent = global_agent
        self.local_agent = local_agent
        self.code_act_agent = code_act_agent
        self.state = state  # State is managed at the manager level

    def execute_workflow(self, main_task):
        # Step 1: Decompose the main task into phases using the GlobalPlanningAgent
        phases = self.global_agent.decompose_task(main_task)
        self.state.root_task = main_task  # Update state with the main task

        # Step 2: Assign tasks to each phase using the GlobalPlanningAgent
        tasks = self.global_agent.assign_tasks(phases)

        # Step 3: Execute tasks using the LocalExecutionAgent and collect feedback
        for phase, subtasks in tasks.items():
            for subtask in subtasks:
                # Update state with the current subtask
                self.state.local_iteration += 1

                # Execute the subtask using the CodeActAgent through the LocalExecutionAgent
                result = self.local_agent.execute_subtask(subtask, self.code_act_agent)
                self.state.outputs[subtask] = result

                # Collect feedback and update the state
                feedback = self.local_agent.collect_feedback(result)
                self.state.metrics.update(feedback)

                # Guidance and potential replanning
                guidance = self.global_agent.provide_guidance(feedback)

                # Step 4: Replan if necessary based on feedback
                replanned_tasks = self.local_agent.replan_if_necessary(
                    feedback, guidance, self.global_agent
                )
                if replanned_tasks:
                    for replanned_phase, replanned_subtasks in replanned_tasks.items():
                        for replanned_subtask in replanned_subtasks:
                            result = self.local_agent.execute_subtask(
                                replanned_subtask, self.code_act_agent
                            )
                            feedback = self.local_agent.collect_feedback(result)
                            self.state.metrics.update(feedback)

        print('All tasks and subtasks executed and feedback collected.')
        self.state.agent_state = AgentState.FINISHED  # Mark the workflow as finished


llm = LLM(config=LLMConfig())
config = AgentConfig()
state = State()  #

# Initialize CodeActAgent
code_act_agent = CodeActAgent(llm, config)

# Initialize GlobalPlanningAgent and LocalExecutionAgent
global_agent = GlobalPlanningAgent(code_act_agent, state)
local_agent = LocalExecutionAgent(code_act_agent, state)

# Initialize CoActManager with the Global, Local agents, CodeActAgent, and State
coact_manager = CoActManager(global_agent, local_agent, code_act_agent, state)

# Execute the workflow
prompt = 'Build a snake game'
coact_manager.execute_workflow(prompt)
