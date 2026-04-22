import pandas as pd
import traceback
import os
import autogen
import sys
import io
import subprocess
from agents.worker_agent.worker_agents import Agents
from agents.worker_agent.worker_agents import ExecutorAgent
from autogen import GroupChat, GroupChatManager

# Force UTF-8 output encoding to avoid UnicodeEncodeError on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ------------------------ Global Configuration ------------------------ #
MODEL = 'minimax-m2.5:cloud'
BASE_URL = 'http://localhost:11434/v1'
API_KEY = 'gemma3'
OUTPUT_DIR = '.'

def load_metadata():
    if os.path.exists("analysis.md"):
        with open("analysis.md", "r", encoding="utf-8") as f:
            return f.read()
    return "No metadata available. Please upload a CSV first."

SPEAKERS = []
def analyze_request_groupchat(request, metadata_text):
    print(f"\n[INFO] Initializing Agents from Worker Agents class...")
    try:
        os.environ["AUTOGEN_USE_DOCKER"] = "0"
        
        # Initialize the Agents factory
        agent_factory = Agents(
            model=MODEL,
            base_url=BASE_URL,
            api_key=API_KEY,
            OUTPUT_DIR=OUTPUT_DIR
        )

        # Initialize core agents for Phase 1
        user_proxy = agent_factory.userproxy_agent_init()
        phase1_manager = agent_factory.phase1_manager_init(request)
        meta_agent = agent_factory.metadata_agent_init(metadata_text)
        planner_agent = agent_factory.planner_agent_init(request)
        
        # Phase 1 GroupChat
        SPEAKERS_PHASE1 = []
        def custom_speaker_phase1(last_speaker, groupchat):
            messages = groupchat.messages
            SPEAKERS_PHASE1.append(last_speaker)
            
            if last_speaker == user_proxy:
                return phase1_manager
            
            last_msg = messages[-1]["content"]
            
            if "PLAN_GENERATED" in last_msg:
                agent_factory.extract_and_save_plan(last_msg)
                return None # End Phase 1
            
            if meta_agent not in SPEAKERS_PHASE1:
                if last_speaker == phase1_manager:
                    return meta_agent
            else:
                if last_speaker == meta_agent:
                    return planner_agent
                    
            return None

        groupchat1 = GroupChat(
            agents=[user_proxy, phase1_manager, meta_agent, planner_agent],
            messages=[],
            max_round=6,
            speaker_selection_method=custom_speaker_phase1
        )

        manager1 = GroupChatManager(
            groupchat=groupchat1,
            llm_config=agent_factory.llm_config,
            system_message="""
            PHASE 1 WORKFLOW
            1. MANAGER CALLS META AGENT FOR INFO ABOUT THE DATASET
            2. ONCE META AGENT RESPONDED SHOULD NOT BE CALLED AGAIN
            3. MANAGER CALLS PLANNER AGENT TO CREATE AN IMPLEMENTATION PLAN
            4. PLANNER GENERATES PLAN AND TASK CHECKLIST
            """
        )

        user_proxy.initiate_chat(
            manager1,
            message=f"User Request: {request}\nInitiate conversation with Manager to get metadata and then instruct Planner to plan the implementation."
        )

        # Forcefully extract the plan directly from message history
        plan_msg = next((m.get("content", "") for m in reversed(groupchat1.messages) if m.get("name") == "Planner"), None)
        if plan_msg:
            agent_factory.extract_and_save_plan(plan_msg)

        # CHECKPOINT
        print("[ACTION_REQUIRED: VERIFY PLAN]")
        # This will block until the frontend sends 'yes' or 'no' over the duplex websocket
        approval = input().strip().lower()
        if approval not in ['yes', 'y']:
            print("System (to UserProxy):\nPlan verification rejected by User. Terminating workflow.")
            return

        print("System (to UserProxy):\nPlan Approved. Beginning code generation phase.")

        # Read the generated plan
        plan_path = "implementation_plan.md"
        if os.path.exists(plan_path):
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_text = f.read()
        else:
            plan_text = "No plan found."

        # Initialize remaining agents for Phase 2
        phase2_manager = agent_factory.phase2_manager_init()
        coder_agent = agent_factory.coder_agent_init()
        feedback_agent = agent_factory.validate_agent(request)
        executor_agent = agent_factory.executor_agent_init()

        SPEAKERS_PHASE2 = [user_proxy]
        def custom_speaker_phase2(last_speaker, groupchat):
            messages = groupchat.messages
            SPEAKERS_PHASE2.append(last_speaker)
            
            if last_speaker == user_proxy:
                return phase2_manager
                
            last_msg_obj = messages[-1]
            last_msg = last_msg_obj.get("content", "")
            if last_speaker == coder_agent:
                agent_factory.extract_and_save_code(last_msg)
                
            # if last_msg_obj.get("tool_calls"):
            #     return executor_agent

            if last_speaker == phase2_manager:
                return coder_agent
            elif last_speaker == coder_agent:
                return executor_agent
            elif last_speaker == executor_agent:
                return feedback_agent
            elif last_speaker == feedback_agent:
                return phase2_manager
            return None

        groupchat2 = GroupChat(
            agents=[user_proxy, phase2_manager, coder_agent, executor_agent, feedback_agent],
            messages=[],
            max_round=10,
            
            speaker_selection_method=custom_speaker_phase2
        )

        manager2 = GroupChatManager(
            groupchat=groupchat2,
            llm_config=agent_factory.llm_config,
            is_termination_msg=agent_factory.is_termination_msg_v3,
            system_message="""
            PHASE 2 WORKFLOW
            1. MANAGER CALLS CODER TO EXECUTE THE VERIFIED PLAN
            2. THE CODER CODES AND CALLS EXECUTOR
            3. AFTER EXECUTOR, FEEDBACK AGENT VALIDATES
            4. ONCE APPROVED, MANAGER PROVIDES FINAL RESPONSE AND EXITS
            """
        )

        # Read the verified plan from disk before starting Phase 2
        plan_content = "No plan found."
        plan_path = "implementation_plan.md"
        if os.path.exists(plan_path):
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_content = f.read()

        # Start Phase 2
        user_proxy.initiate_chat(
            manager2,
            message=f"The user has reviewed and verified the implementation plan. \n\nVERIFIED PLAN CONTENT:\n{plan_content}\n\nManager, please coordinate with the Coder to implement this plan for user request: {request}"
        )

        # Final Local Execution mapping and formatting
        code_path = os.path.join("generated_code", "main.py")
        if os.path.exists(code_path):
            result = subprocess.run(
                ["python", code_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            # Interpret Result
            result_interpreter = agent_factory.result_agent_init(request, result.stdout)
            final_response = result_interpreter.generate_reply(
                messages=[{"role": "user", "content": "Generate the response for the user request based on the code output"}]
            )

            print("--------------------------------------------------------------------------------")
            print("Manager (to UserProxy):")
            if isinstance(final_response, dict):
                print(final_response["content"])
            else:
                print(final_response)

        print("Task completed")

    except Exception as e:
        print(f"[ERROR] {e}")
        traceback.print_exc()

if __name__ == "__main__":
    metadata = load_metadata()
    if len(sys.argv) > 1:
        req = sys.argv[1]
    else:
        abs_csv = os.path.abspath(os.path.join("generated_code", "Input", "input.csv")).replace("\\", "/")
        req = f"Summarize the dataset. STRICT INSTRUCTION: The absolute filepath is '{abs_csv}'."
    
    analyze_request_groupchat(req, metadata)
