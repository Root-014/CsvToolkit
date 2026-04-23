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
import json
import re

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
    metadata_dir = os.path.join("generated_code", "metadata")
    all_metadata = ""
    
    if os.path.exists(metadata_dir):
        files = [f for f in os.listdir(metadata_dir) if f.endswith(".md")]
        for f in files:
            path = os.path.join(metadata_dir, f)
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                # Sanitize: Remove absolute paths that might have been leaked in older reports
                content = re.sub(r'\*\*Source File\*\*: `.*?([^/\\]+\.csv)`', r'**Source File**: `\1`', content)
                all_metadata += f"### DATASET: {f.replace('_metadata.md', '.csv')}\n" + content + "\n\n"
    
    if not all_metadata and os.path.exists("analysis.md"):
        with open("analysis.md", "r", encoding="utf-8") as f:
            all_metadata = f.read()
            
    return all_metadata if all_metadata else "No metadata available. Please upload CSV files first."

SESSION_CONTEXT_FILE = "session_context.json"

def load_session_context():
    if os.path.exists(SESSION_CONTEXT_FILE):
        try:
            with open(SESSION_CONTEXT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "history_summary": "Initial turn.",
        "key_findings": [],
        "active_files": [],
        "proactive_suggestions": []
    }

def save_session_context(context):
    with open(SESSION_CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2)

SPEAKERS = []
def run_agent_workflow(initial_request, metadata_text):
    print(f"\n[INFO] Initializing Agentic Session...")
    try:
        os.environ["AUTOGEN_USE_DOCKER"] = "0"
        
        # Initialize the Agents factory
        agent_factory = Agents(
            model=MODEL,
            base_url=BASE_URL,
            api_key=API_KEY,
            OUTPUT_DIR=OUTPUT_DIR,
            metadata=metadata_text
        )

        current_request = initial_request
        is_first_turn = True
        session_context = load_session_context()

        while True:
            # Read current context
            current_plan = agent_factory.read_verified_plan()
            current_code = agent_factory.read_current_code()
            
            # Format history for Manager
            history_str = json.dumps(session_context, indent=2) if not is_first_turn else None
            
            # Initialize core agents for Phase 1
            user_proxy = agent_factory.userproxy_agent_init()
            phase1_manager = agent_factory.phase1_manager_init(current_request, is_followup=not is_first_turn, history_summary=history_str)
            metadata_specialist = agent_factory.metadata_agent_init(metadata_text)
            planner_agent = agent_factory.planner_agent_init(current_request, current_plan=current_plan, current_code=current_code, history_summary=history_str)
            
            # Phase 1 GroupChat
            def custom_speaker_phase1(last_speaker, groupchat):
                messages = groupchat.messages
                if not messages: return phase1_manager
                last_msg = messages[-1].get("content", "")

                if last_speaker == user_proxy:
                    return phase1_manager
                if last_speaker == phase1_manager:
                    return metadata_specialist
                if last_speaker == metadata_specialist:
                    return planner_agent
                
                if last_speaker == planner_agent:
                    if "PLAN_GENERATED" in last_msg:
                        return None # End Phase 1
                    return metadata_specialist
                return None

            groupchat1 = GroupChat(
                agents=[user_proxy, phase1_manager, metadata_specialist, planner_agent],
                messages=[],
                max_round=10,
                speaker_selection_method=custom_speaker_phase1
            )

            manager1 = GroupChatManager(
                groupchat=groupchat1,
                llm_config=agent_factory.get_llm_config(temperature=0),
                system_message="PHASE 1: Planning and Metadata gathering."
            )

            user_proxy.initiate_chat(
                manager1,
                message=f"User Request: {current_request}\nInitiate conversation with Manager."
            )

            # Extract the plan from the last Planner message
            planner_msgs = [m for m in groupchat1.messages if m.get("name") == "Planner"]
            if planner_msgs:
                plan_text = planner_msgs[-1].get("content", "")
                agent_factory.extract_and_save_plan(plan_text)

            # CHECKPOINT: PLAN APPROVAL
            import sys
            print("\n[ACTION_REQUIRED: VERIFY PLAN]", flush=True)
            approval = sys.stdin.readline().strip().lower()
            
            if approval not in ['yes', 'y']:
                print("[SYSTEM] Plan verification rejected or session terminated.", flush=True)
                break

            print("[SYSTEM] Plan Approved. Beginning execution phase.", flush=True)

            # Phase 2: Execution
            phase2_manager = agent_factory.phase2_manager_init()
            coder_agent = agent_factory.coder_agent_init()
            feedback_agent = agent_factory.validate_agent(current_request)
            executor_agent = agent_factory.executor_agent_init()

            def custom_speaker_phase2(last_speaker, groupchat):
                messages = groupchat.messages
                if last_speaker == user_proxy:
                    return phase2_manager
                last_msg = messages[-1].get("content", "")
                if last_speaker == coder_agent:
                    agent_factory.extract_and_save_code(last_msg)
                
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
                max_round=12,
                speaker_selection_method=custom_speaker_phase2
            )

            manager2 = GroupChatManager(
                groupchat=groupchat2,
                llm_config=agent_factory.get_llm_config(temperature=0),
                is_termination_msg=agent_factory.is_termination_msg_v3,
                system_message="PHASE 2: Implementation and Validation."
            )

            plan_content = agent_factory.read_verified_plan()
            user_proxy.initiate_chat(
                manager2,
                message=f"PLAN:\n{plan_content}\n\nExecute the plan for request: {current_request}"
            )

            # Final response generation
            code_path = os.path.join("generated_code", "main.py")
            if os.path.exists(code_path):
                result = subprocess.run(["python", code_path], capture_output=True, text=True, encoding='utf-8', errors='replace')
                result_interpreter = agent_factory.result_agent_init(current_request, result.stdout, history_summary=history_str)
                final_response = result_interpreter.generate_reply(messages=[{"role": "user", "content": "Generate final response"}])
                
                print("--------------------------------------------------------------------------------")
                print("ResultInterpreter (to UserProxy):")
                print(final_response["content"] if isinstance(final_response, dict) else final_response)
                print("--------------------------------------------------------------------------------")

            # --- CONTEXT SUMMARIZATION (Asynchronous in flow) ---
            print("[INFO] Updating session memory...")
            try:
                # Collect logs from this turn
                turn_logs = []
                for msg in groupchat1.messages:
                    turn_logs.append(f"{msg.get('name', 'Agent')}: {msg.get('content', '')}")
                for msg in groupchat2.messages:
                    turn_logs.append(f"{msg.get('name', 'Agent')}: {msg.get('content', '')}")
                
                logs_text = "\n".join(turn_logs)
                
                summarizer = agent_factory.context_manager_init()
                summary_prompt = f"CURRENT CONTEXT: {json.dumps(session_context)}\n\nNEW LOGS FROM THIS TURN:\n{logs_text}"
                summary_res = summarizer.generate_reply(messages=[{"role": "user", "content": summary_prompt}])
                summary_content = summary_res["content"] if isinstance(summary_res, dict) else summary_res
                
                # Extract JSON
                json_match = re.search(r'\{.*\}', summary_content, re.DOTALL)
                if json_match:
                    session_context = json.loads(json_match.group(0))
                    save_session_context(session_context)
                    print(f"[DEBUG] Session memory updated. Proactive suggestions: {len(session_context.get('proactive_suggestions', []))}")
            except Exception as e:
                print(f"[DEBUG] Memory update failed: {e}")

            print("[WAITING_FOR_INPUT] Ready for follow-up questions.")
            next_input = sys.stdin.readline().strip()
            if not next_input or next_input.lower() in ['exit', 'quit', 'terminate']:
                print("[SYSTEM] Session terminated.")
                break
            
            current_request = next_input
            is_first_turn = False

    except Exception as e:
        print(f"[ERROR] {e}")
        traceback.print_exc()

if __name__ == "__main__":
    metadata = load_metadata()
    if len(sys.argv) > 1:
        req = sys.argv[1]
    else:
        req = "Summarize the dataset."
    
    run_agent_workflow(req, metadata)
