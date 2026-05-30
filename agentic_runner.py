import pandas as pd
import traceback
import os
import autogen
import sys
import io
import subprocess
import threading
from agents.worker_agent.worker_agents import Agents
from agents.worker_agent.worker_agents import ExecutorAgent
from autogen import GroupChat, GroupChatManager
import json
import re
from datetime import datetime

def log_phase_time(phase_name, start_time, end_time):
    duration = (end_time - start_time).total_seconds()
    with open("phase_timings.txt", "a", encoding="utf-8") as f:
        f.write(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Phase: {phase_name} | Duration: {duration:.2f}s\n")

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
                all_metadata += f"### DATASET: {f.replace('_metadata.md', '')}\n" + content + "\n\n"
    
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
            metadata_specialist = agent_factory.metadata_agent_init(current_request, metadata_text, current_plan=current_plan, current_code=current_code, history_summary=history_str)
            
            # Phase 1 GroupChat
            phase1_start = datetime.now()
            def custom_speaker_phase1(last_speaker, groupchat):
                messages = groupchat.messages
                if not messages: return phase1_manager
                last_msg = messages[-1].get("content", "")

                if last_speaker == user_proxy:
                    return phase1_manager
                if last_speaker == phase1_manager:
                    return metadata_specialist
                if last_speaker == metadata_specialist:
                    if "PLAN_GENERATED" in last_msg:
                        return None # End Phase 1
                    return phase1_manager
                return None

            groupchat1 = GroupChat(
                agents=[user_proxy, phase1_manager, metadata_specialist],
                messages=[],
                max_round=10,
                speaker_selection_method=custom_speaker_phase1
            )

            manager1 = GroupChatManager(
                groupchat=groupchat1,
                llm_config=agent_factory.get_llm_config(temperature=0.5),
                system_message="PHASE 1: Planning and Metadata gathering."
            )

            user_proxy.initiate_chat(
                manager1,
                message=f"User Request: {current_request}\nInitiate conversation with Manager."
            )
            phase1_end = datetime.now()
            log_phase_time("Phase 1: Planning", phase1_start, phase1_end)

            # Extract the plan from the last Metadata_Specialist message
            meta_msgs = [m for m in groupchat1.messages if m.get("name") == "Metadata_Specialist"]
            if meta_msgs:
                plan_text = meta_msgs[-1].get("content", "")
                agent_factory.extract_and_save_plan(plan_text)

            # CHECKPOINT: PLAN APPROVAL
            import sys
            print("\n[ACTION_REQUIRED: VERIFY PLAN]", flush=True)
            verify_start = datetime.now()
            approval = sys.stdin.readline().strip().lower()
            verify_end = datetime.now()
            log_phase_time("Plan Verification", verify_start, verify_end)
            
            if approval not in ['yes', 'y']:
                print("[SYSTEM] Plan verification rejected or session terminated.", flush=True)
                break

            print("[SYSTEM] Plan Approved. Beginning execution phase.", flush=True)

            # Phase 2: Execution
            phase2_start = datetime.now()
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
                llm_config=agent_factory.get_llm_config(temperature=0.5),
                is_termination_msg=agent_factory.is_termination_msg_v3,
                system_message="PHASE 2: Implementation and Validation."
            )

            plan_content = agent_factory.read_verified_plan()
            print(f"****************\n {plan_content} \n *****************")
            user_proxy.initiate_chat(
                manager2,
                message=f"PLAN:\n{plan_content}\n\nExecute the plan for request: {current_request}"
            )
            phase2_end = datetime.now()
            log_phase_time("Phase 2: Execution", phase2_start, phase2_end)

            # Final response generation
            res_gen_start = datetime.now()
            
            # Find the last message from FeedbackAgent
            feedback_msgs = [m for m in groupchat2.messages if m.get("name") == "FeedbackAgent"]
            if feedback_msgs:
                last_msg_content = feedback_msgs[-1].get("content", "")
                
                if "<!-- FINAL_ANSWER_START -->" in last_msg_content:
                    # Extract the section between the hidden tags
                    final_answer = last_msg_content.split("<!-- FINAL_ANSWER_START -->")[-1].split("<!-- FINAL_ANSWER_END -->")[0].strip()
                    
                    print("--------------------------------------------------------------------------------", flush=True)
                    print("ResultInterpreter (to UserProxy):", flush=True)
                    print(final_answer, flush=True)
                    print("--------------------------------------------------------------------------------", flush=True)
                else:
                    # Fallback or display report if it was an error
                    print("--------------------------------------------------------------------------------", flush=True)
                    print("Validator (Report):", flush=True)
                    print(last_msg_content, flush=True)
                    print("--------------------------------------------------------------------------------", flush=True)
            
            res_gen_end = datetime.now()
            log_phase_time("Result Generation", res_gen_start, res_gen_end)

            # --- CONTEXT SUMMARIZATION (Background thread) ---
            mem_start = datetime.now()
            mem_result = [session_context]  # mutable container for thread result

            def _update_memory():
                try:
                    turn_logs = []
                    for msg in groupchat1.messages:
                        turn_logs.append(f"{msg.get('name', 'Agent')}: {msg.get('content', '')}")
                    for msg in groupchat2.messages:
                        turn_logs.append(f"{msg.get('name', 'Agent')}: {msg.get('content', '')}")
                    logs_text = "\n".join(turn_logs)
                    summarizer = agent_factory.context_manager_init()
                    summary_prompt = f"CURRENT CONTEXT: {json.dumps(mem_result[0])}\n\nNEW LOGS FROM THIS TURN:\n{logs_text}"
                    summary_res = summarizer.generate_reply(messages=[{"role": "user", "content": summary_prompt}])
                    summary_content = summary_res["content"] if isinstance(summary_res, dict) else summary_res
                    json_match = re.search(r'\{.*\}', summary_content, re.DOTALL)
                    if json_match:
                        mem_result[0] = json.loads(json_match.group(0))
                        save_session_context(mem_result[0])
                except Exception as e:
                    print(f"[DEBUG] Memory update failed: {e}", flush=True)

            mem_thread = threading.Thread(target=_update_memory, daemon=True)
            mem_thread.start()

            print("[WAITING_FOR_INPUT] Ready for follow-up questions.", flush=True)
            next_input = sys.stdin.readline().strip()

            # Wait for memory thread before next turn (30s max)
            mem_thread.join(timeout=30)
            mem_end = datetime.now()
            log_phase_time("Memory Update", mem_start, mem_end)
            session_context = mem_result[0]

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
