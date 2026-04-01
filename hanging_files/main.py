import pandas as pd
import traceback
from agents.csv_analyzer import CSVAnalysisAgent
from autogen import GroupChat, GroupChatManager
import os
import autogen


# ------------------------ Global declarations ------------------------ #
config_list = {
        'model': 'glm-4.7-flash',
        'base_url': 'http://localhost:11434/v1',
        'api_key': 'glm-4.7-flash',
        'api_type': 'openai',
}

llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
    "max_tokens": 2000,
}

config_list = {
        'model': 'minimax-m2.5:cloud',
        'base_url': 'http://localhost:11434/v1',
        'api_key': 'gemma3',
        'api_type': 'openai',
}

llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
    "max_tokens": 2000,
    
}

config_list_coding = {
        'model': 'minimax-m2.5:cloud',
        'base_url': 'http://localhost:11434/v1',
        'api_key': 'ollama',
        'api_type': 'openai',
}

llm_config_coding = {
    "config_list": config_list_coding,
    "temperature": 0.7,
    "max_tokens": 2000,
    
}



CSV_FILE = 'generated_code/Input/input.csv'
OUTPUT_DIR = 'generated_code'



os.makedirs(OUTPUT_DIR, exist_ok=True)



# ------------------------ CSV info execution ------------------------ #
try:
    agent = CSVAnalysisAgent()
    agent.load_csv(CSV_FILE)
    results = agent.analyze(detailed=True)
    report_path = agent.generate_report(output_path='s.md')
    print("\n[SUCCESS] Analysis completed successfully!")
    print(f"[OK] Report saved to: {report_path}")

except FileNotFoundError as e:
    print(f"[ERROR] File not found: {e}")
    print("Please check if the file path is correct.")
except Exception as e:
    print(f"[ERROR] An error occurred: {e}")
    print("\nFull traceback:")
    traceback.print_exc()


# ------------------------ Agents and utils ------------------------ #

def is_termination_msg(msg):
    if msg is None:
        return False
    content = msg.get("content", "")
    return "TERMINATE" in content or "APPROVED" in content



user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",  # IMPORTANT for automation
    max_consecutive_auto_reply=0,  
    is_termination_msg=is_termination_msg,
    code_execution_config={
        "work_dir": OUTPUT_DIR,
        "use_docker": False,
    },
    system_message="""
            Execute code when requested. Do not initiate conversations.
"""
)


def get_metadata_agent(metadata_text):
    meta_agent = autogen.AssistantAgent(
        name="MetaAgent",
        llm_config=llm_config,
        system_message=f""" You are a METADATA SPECIALIST.

    METADATA : {metadata_text}


    ROLE:
    - Answer questions asked by the Manager.
    - Identify column names, data types, and relationships
    - Provide concise, factual information

    RESPONSE FORMAT:
    When asked about columns or structure, respond with:
    - Exact column names (copy from metadata)
    - Data types
    - Any relevant notes about the data

    In the end respond - "METADATA_READY" along with the result

    Be direct and factual. Answer only what was asked.
    """

    )
    return meta_agent

coder_agent = autogen.AssistantAgent(
    name="Coder",
    llm_config=llm_config_coding,
    system_message="""
You are a PYTHON CODE SPECIALIST.

- Generate clean, executable Python code based on Manager's instructions
- Follow best practices
- Include error handling

CODE REQUIREMENTS:
- Target file: "main.py"
- Import pandas and other needed libraries
- Include comments for clarity
- Handle potential errors
- Print results or save to file as appropriate

STRICT RULES:
- Only generate code for the given task
- Do NOT add extra features
- Do NOT analyze beyond request
- Ensure code is executable

RESPONSE FORMAT:
Provide the complete code in a code block, then briefly explain what it does.

If you need any information then ask Manager AGENT for that.
TERMINATION:
- End response after code generation
"""
)

feedback_agent = autogen.AssistantAgent(
    name="FeedbackAgent",
    llm_config=llm_config,
    code_execution_config={
        "work_dir": OUTPUT_DIR,
        "use_docker": False,
    },

    system_message="""

You are a strict validator.

You are a CODE VALIDATOR.

ROLE:
- Review code for correctness
- Check if it solves the requested task
- Identify potential issues

VALIDATION CHECKLIST:
✓ Does code match the task requirements?
✓ Are imports correct?
✓ Will it run without errors?
✓ Is error handling adequate?


OUTPUT FORMAT:
- If valid: "APPROVED: [brief reason]"
- If issues: "REJECTED: [specific issues]"

""",
)

manager_prompt = """
You are the MANAGER - the leader of a hierarchical team.

YOU ALWAYS INITIATE conversation as the Manager Agent in the group chat.

ROLE:
- Receive user requests and break them into subtasks
- Directly communicate with specialized agents
- Make decisions on workflow and next steps
- Aggregate results and ensure quality

YOUR TEAM:
- MetaAgent: Dataset structure expert (ask about any info related to the dataset)
- Coder: Python code generator (request code generation)
- Validator: Code quality checker (request validation)

COMMUNICATION PROTOCOL:
When you need information from an agent:
1. State what you need clearly
2. Ask your question directly
3. Wait for their response
4. Use their response to guide next steps

EXAMPLE:
"MetaAgent, I need to understand the input dataset. What is the exact column name for 'Fcst_BaselineFcst_Baseline' in the Final_Merge dataset?"

WORKFLOW:
1. Understand the user request
2. Ask MetaAgent for dataset information ask question to it.
3. Based on MetaAgent's response, instruct Coder to generate code
4. Ask Validator to check the code
5. If issues found, work with Coder to fix
6. When satisfied, respond with: TERMINATE

PHASE 1: METADATA (ONLY ONCE)
- Ask MetaAgent for ALL required dataset details in ONE message
- After MetaAgent responds, store the information
- DO NOT call MetaAgent again
- When metadata is collected, respond with: METADATA_READY

IMPORTANT:
- Always wait for responses before proceeding
- Make decisions based on team feedback
- Be specific in your requests to agents
"""

manager_prompt1 = """
YOU ARE THE MANAGER (STRICT CONTROLLER)

You control a team of agents:
- MetaAgent (metadata)
- Coder (code generation)
- Validator (validation)

====================================
WORKFLOW (MANDATORY)
====================================

PHASE 1: METADATA (RUN ONCE)
- Ask MetaAgent for ALL required dataset details in ONE message
- After receiving response:
    → Store the information
    → Respond: METADATA_READY
- NEVER call MetaAgent again

PHASE 2: CODE LOOP
- Ask Coder to generate code using metadata
- Send code to Validator

IF Validator says REJECTED:
    → Ask Coder to fix using feedback
    → Repeat loop

IF Validator says APPROVED:
    → Respond TERMINATE

====================================
COMMUNICATION RULES (STRICT)
====================================

- Speak to ONLY ONE agent at a time
- ALWAYS prefix messages exactly as:
    MetaAgent:
    Coder:
    Validator:

- NEVER answer your own questions
- NEVER skip steps
- ALWAYS wait for agent response

====================================
RESPONSE RULES
====================================

- Be concise (max 80 words)
- No explanations unless necessary
- No extra text outside instructions

====================================
FAILSAFE
====================================

If unsure or missing information:
→ Ask MetaAgent (only if METADATA phase not completed)
"""
manager_agent = autogen.AssistantAgent(
    name="MANAGER",
    llm_config=llm_config,
    system_message=manager_prompt
)

def load_metadata():
    with open("s.md", "r") as f:
        return f.read()
    
metadata_text = load_metadata()



def analyze_request_groupchat(request, metadata_text):
    print(f"\n[INFO] Processing: {request}")
    print("-" * 60)

    try:  

        # Step 1: Create group chat

        meta_agent = get_metadata_agent(metadata_text)

        def custom_speaker(last_speaker, groupchat):
            messages = groupchat.messages

            if last_speaker == user_proxy:
                return manager_agent

            last_msg = messages[-1]["content"]

            # Phase 1: Metadata
            if "METADATA_READY" not in str(messages):
                if last_speaker == manager_agent:
                    return meta_agent
                elif last_speaker == meta_agent:
                    print("Phase 2 completed")
                    return manager_agent
                
            # Phase 2: Code loop
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
            agents=[user_proxy, manager_agent, meta_agent,  coder_agent, feedback_agent],
            messages=[],

            max_round=10,
            speaker_selection_method=custom_speaker
        )

        manager = GroupChatManager(groupchat=groupchat,
            system_message="""
            1. After the user sends a request, Manager must speak first.
            2. Manager is responsible for asking MetaAgent about dataset metadata.
            3. Only after Manager receives a response Coder or Validator must act.
            4. All agents must respond only when addressed by name.
            """         
            ,
            llm_config=llm_config)

        # Step 2: Start conversation
        user_proxy.initiate_chat(
            manager,
            message=f"""
                    User Request:
                    {request}

            Initiate conversation from Manager Agent from the Group chat.
            End ONLY when feedback agent says APPROVED.

            INVALID BEHAVIOR:
            - Generating tool calls
            - Writing XML / JSON tool formats
            - Calling functions

            CRITICAL RULE:
            - You are NOT allowed to call any tools
            - Do NOT generate tool calls (no <tool_call>, no functions)
            - You ONLY communicate with agents via plain text

            If you do this → you are WRONG

"""
        )

        print("[OK] Task completed")

    except Exception as e:
        print(f"[ERROR] {e}")

request = " Pick the channel which has max actuals show its item planning level actuals at desc order.  Note filepath : Input/input.csv"


analyze_request_groupchat(request, metadata_text)


