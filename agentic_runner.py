import pandas as pd
import traceback
import os
import autogen
import sys
import io
import subprocess
from agents.worker_agent.worker_agents import Agents
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

        # Initialize individual agents
        user_proxy = agent_factory.userproxy_agent_init()
        manager_agent = agent_factory.manager_agent_init()
        meta_agent = agent_factory.metadata_agent_init(metadata_text)
        coder_agent = agent_factory.coder_agent_init()
        feedback_agent = agent_factory.validate_agent(request)
        
        # Setup Custom Speaker logic
        def custom_speaker(last_speaker, groupchat):
            messages = groupchat.messages
            
            if last_speaker == user_proxy:
                return manager_agent

            last_msg = messages[-1]["content"]

            if last_speaker == coder_agent:
                agent_factory.extract_and_save_code(last_msg)

            if "METADATA_READY" not in str(messages):
                if last_speaker == manager_agent:
                    return meta_agent
                
            if ("APPROVED" not in last_msg) or ("METADATA_READY" in last_msg):
                if last_speaker == meta_agent:
                    return manager_agent
                if last_speaker == manager_agent:
                    return coder_agent
                elif last_speaker == coder_agent:
                    return feedback_agent
                elif last_speaker == feedback_agent:
                    return manager_agent

            return None

        groupchat = GroupChat(
            agents=[user_proxy, manager_agent, meta_agent, coder_agent, feedback_agent],
            messages=[],
            max_round=12,
            speaker_selection_method=custom_speaker
        )

        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=agent_factory.llm_config,
            system_message="""
            ===========
            WORKFLOW
            ===========
            1. CALL MANAGER FIRST 
            2. THEN MANAGER CALLS META AGENT FOR INFO ABOUT THE DATASET
            3. ONCE META AGENT RESPONDED SHOULD NOT CALLED AGAIN
            4. THEN MANAGER CALLS CODER AGENT FOR CODE GENERATION
            5. THEN CODER AGENT CALLS FEEDBACK AGENT FOR CODE VALIDATION
            6. IF FEEDBACK AGENT SAYS REJECTED THEN CODER AGENT SHOULD FIX THE CODE
            7. IF FEEDBACK AGENT SAYS APPROVED THEN MANAGER SHOULD EXPLAIN THE FINAL RESPONSE TO THE ASK OF THE USER REQUEST DIRECTLY IN THE END.
            """
        )

        user_proxy.initiate_chat(
            manager,
            message=f"""
                User Request: {request}

                Initiate conversation from Manager Agent from the Group chat.
                End ONLY when feedback agent says approved in capital.

                INVALID BEHAVIOR:
                
                - Writing XML / JSON tool formats
                - Calling functions

                CRITICAL RULE:
                - You are NOT allowed to call any tools
                - Do NOT generate tool calls
                - You ONLY communicate with agents via plain text
            """
        )

        # Step 2: Execute code
        code_path = os.path.join("generated_code", "main.py")
        result = subprocess.run(
            ["python", code_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # Step 3: Interpret Result
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
