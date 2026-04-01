import pandas as pd
import traceback
from agents.csv_analyzer import CSVAnalysisAgent
from autogen import GroupChat, GroupChatManager
import os
import autogen
import sys
import io

# Force UTF-8 output encoding to avoid UnicodeEncodeError (cp1252) on Windows terminals natively
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


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
        "price": [0.0, 0.0]
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
        "price": [0.0, 0.0]
}

llm_config_coding = {
    "config_list": config_list_coding,
    "temperature": 0.7,
    "max_tokens": 2000,
    
}



CSV_FILE = r'Input\input.csv'
OUTPUT_DIR = '.'



# os.makedirs(OUTPUT_DIR, exist_ok=True)



# CSV info execution disabled here, handled by API during upload
# ----------



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

import re

def extract_code_from_response(response: str) -> str:
    try:
        match = re.search(r"```python(.*?)```", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return "No Python code block found."
    except Exception as e:
        return f"Error extracting code: {str(e)}"



def extract_and_save_code(response: str, filename: str = r"generated_code\main.py") -> str:
    code = extract_code_from_response(response)
    
    if code.startswith("Error") or code == "No Python code block found.":
        return code

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Save file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)

        # Return full absolute path
        return f"Code extracted and saved to {os.path.abspath(filename)}"
    
    except Exception as e:
        return f"Error saving file: {str(e)}"



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
    - STRICTLY DON'T ASK ANY FOLLOW UP QUESTIONS

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
Provide the complete code in a code block 

eg : 
```python
# code here
```
STRICTLY CODE ONLY 

If you need any information then ask Manager AGENT for that.
TERMINATION:
- End response after code generation
"""
)

coder_agent.register_function(
    function_map={
        "extract_and_save_code": extract_and_save_code
    }
)

feedback_agent = autogen.AssistantAgent(
    name="FeedbackAgent",
    llm_config=llm_config,
    code_execution_config={
        "work_dir": OUTPUT_DIR,
        "use_docker": False,
    },

    system_message="""

You are a CODE VALIDATOR.

ROLE:
- Review code for correctness
- Check if it solves the requested task
- Identify potential issues if any

VALIDATION CHECKLIST:
* Does code match the task requirements?
* Are imports correct?
* Will it run without errors?
* Is error handling adequate?

CODE EXECUTION :
 - DO ONLY IF CODE IS VALIDATED CORRECTLY.


OUTPUT FORMAT:
- If valid: "APPROVED: [brief reason]"
- If issues: "REJECTED: [specific issues]"
- SEND THE RESULT TO THE MANAGER.

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
- MetaAgent: Dataset expert (ask about any info related to the dataset ONLY)
- Coder: Python code generator (request code generation ONLY)
- Validator: Code quality checker (request validation ONLY)
- DON'T USE METAAGENT ONCE IT IS CALLED.

COMMUNICATION PROTOCOL:
When you need information from an agent:
1. State what you need clearly
2. Ask your question or instruct directly
3. Wait for their response
4. Use their response to guide next steps

EXAMPLE:
"MetaAgent : I need to understand the input dataset. What is the exact column name for 'Fcst_BaselineFcst_Baseline' in the Final_Merge dataset?"
"Coder : generate code to read the CSV file from the specified path and filter for holidays in the year 2026"
"Validator : check the code for correctness and identify potential issues if any"

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


YOUR TEAM:
- MetaAgent: Dataset expert (ask about any info related to the dataset ONLY)
- Coder: Python code generator (request code generation ONLY)
- Validator: Code quality checker (request validation ONLY)
- DON'T USE METAAGENT ONCE IT IS CALLED.


EXAMPLE:
"MetaAgent : I need to understand the input dataset. What is the exact column name for 'Fcst_BaselineFcst_Baseline' in the Final_Merge dataset?"
"Coder : generate code to read the CSV file from the specified path and filter for holidays in the year 2026"
"Validator : check the code for correctness and identify potential issues if any"

NOTE : DON'T CALL THE SAME AGENT WHICH SPOKE JUST NOW.X

====================================
WORKFLOW (MANDATORY)
====================================

PHASE 1: METADATA (RUN ONCE)
- Ask MetaAgent for ALL required dataset details in ONE message
- After receiving response:
    * Store the information
    * Respond: METADATA_READY
- NEVER call MetaAgent again

PHASE 2: CODE LOOP
- Ask Coder to generate code using metadata
- Send code to Validator

IF Validator says REJECTED:
    * Ask Coder to fix using feedback
    * Repeat loop

IF Validator says APPROVED:
    * Respond TERMINATE

DON'T CALL THE SAME AGENT AGAIN.

====================================
RULES (STRICT)
====================================

- ONLY YOU ARE AUTHORIZED TO CALL THE AGENTS.
- NO AGENTS SHOULD CALL OTHER AGENTS.
- Speak to ONLY ONE agent at a time
- ALWAYS prefix messages exactly as:
    MetaAgent:
    Coder:
    Validator:

- NEVER answer your own questions
- NEVER skip steps
- ALWAYS wait for agent response
- ONCE YOU GOT RESPONSE FROM THE METAAGENT NEVER ASK ANYTHING FROM THAT EVER AGAIN.
- EXPLAIN THE FINAL RESPONSE TO THE ASK OF THE USER REQUREST DIRECTLY IN THE END. FOLLOW THE FORMAT : 
            "REQUEST : <USER REQUEST> 
            "RESPONSE : <FINAL RESPONSE>" 

====================================
RESPONSE RULES
====================================

- Be concise (max 80 words)
- No explanations unless necessary
- No extra text outside instructions
- ONCE VALIDATOR RESULT MEETS THE ASK OF THE USER IMMEDIATELY TERMINATE DON'T GO BEYOND THAT.

====================================
FAILSAFE
====================================

If unsure or missing information:
 * Ask MetaAgent (only if METADATA phase not completed)

"""


manager_prompt1 = """
YOU ARE THE MANAGER (STRICT CONTROLLER)

====================================
YOUR TEAM:
===================================

- MetaAgent: Dataset expert (ask about any info related to the dataset ONLY)
- Coder: Python code generator (request only for code generation)
- Validator: Code quality checker (request only for validation)
- DON'T RUN METAAGENT AGAIN ONCE IT WAS CALLED EARLIER OR WHEN METADATA_READY IS RESPONDED.


EXAMPLE:
"MetaAgent : I need to understand the input dataset. What is the exact column name for 'Fcst_BaselineFcst_Baseline' in the Final_Merge dataset?"
"Coder : generate code to read the CSV file from the specified path and filter for holidays in the year 2026"
"Validator : check the code for correctness and identify potential issues if any"



====================================
WORKFLOW (MANDATORY)
====================================

1. Ask MetaAgent first for ALL required dataset details in ONE message
2. After receiving response:
    * Store the information
    * Respond: METADATA_READY
3. NEVER call MetaAgent again
4. Ask Coder to generate code using metadata and request 
5. Send code to Validator
6. IF Validator says REJECTED:
    * Ask Coder to fix using feedback
    * Repeat loop
7. IF Validator says APPROVED:
    * With final result you have to explain the final response to the ask of the user request directly in the end. FOLLOW THE FORMAT : 
            "REQUEST : <USER REQUEST> 
            "RESPONSE : <FINAL RESPONSE>" 
    * Respond TERMINATE

8. DON'T CALL THE SAME AGENT AGAIN.

NOTE : DON'T CALL THE SAME AGENT WHICH SPOKE JUST NOW.

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
- ONCE YOU GOT RESPONSE FROM THE METAAGENT NEVER ASK ANYTHING FROM THAT EVER AGAIN.
- EXPLAIN THE FINAL RESPONSE TO THE ASK OF THE USER REQUREST DIRECTLY IN THE END. FOLLOW THE FORMAT : 
            "REQUEST : <USER REQUEST> 
            "RESPONSE : <FINAL RESPONSE>" 

====================================
RESPONSE RULES
====================================

- Be concise (max 80 words)
- No explanations unless necessary
- No extra text outside instructions
- ONCE VALIDATOR RESULT MEETS THE ASK OF THE USER IMMEDIATELY TERMINATE DON'T GO BEYOND THAT.

====================================
FAILSAFE
====================================

If unsure or missing information:
 * Ask MetaAgent (only if METADATA phase not completed)

"""


manager_agent = autogen.AssistantAgent(
    name="MANAGER",
    llm_config=llm_config,
    system_message=manager_prompt1
)

executor = autogen.UserProxyAgent(
    name="Executor",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "generated_code",
        "use_docker": False
    }
)

def result_agent(request):
    result_agent = autogen.AssistantAgent(
        name="ResultInterpreter",
        llm_config=llm_config,
        system_message=f"""
    You are a RESULT INTERPRETER.

    USER REQUEST : {request}

    - You receive execution output from Python code
    - Analyze the output
    - Generate a clear answer for the user

    RULES:
    - Use ONLY the execution result
    - Do NOT assume anything
    - Be concise and clear

    Output FORMAT : 
            REQUEST : <USER REQUEST> 
            "RESPONSE : <FINAL RESPONSE>"
    """
    )

    return result_agent

def load_metadata():
    import os

    if os.path.exists("analysis.md"):
        with open("analysis.md", "r") as f:
            return f.read()
    else:
        return "No metadata available. Please upload a CSV first."
    
metadata_text = load_metadata()



def analyze_request_groupchat(request, metadata_text):
    print(f"\n[INFO] Processing: {request}")
    print("-" * 60)

    try:  

        # Step 1: Create group chat

        meta_agent = get_metadata_agent(metadata_text)
        executor = autogen.UserProxyAgent(
                    name="Executor",
                    human_input_mode="NEVER",
                    code_execution_config={
                        "work_dir": "generated_code",
                        "use_docker": False
                    }
                )

        result_agent = autogen.AssistantAgent(
    name="ResultInterpreter",
    llm_config=llm_config,
    system_message="""
You are a RESULT INTERPRETER.

- You receive execution output from Python code
- Analyze the output
- Generate a clear answer for the user

RULES:
- Use ONLY the execution result
- Do NOT assume anything
- Be concise and clear
"""
)

        def custom_speaker(last_speaker, groupchat):
            messages = groupchat.messages

            if last_speaker == user_proxy:
                return manager_agent

            last_msg = messages[-1]["content"]

            if last_speaker == coder_agent:
                extract_and_save_code(last_msg)

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

            max_round=12,
            speaker_selection_method= 'auto'
        )

        manager = GroupChatManager(groupchat=groupchat,
            system_message="""
            ===========
            WORKFLOW
            ===========

            1. CALL MANAGER FIRST 
            2. THEN MANAGER CALLS META AGENT FOR INFO ABOUT THE DATASET
            3. ONCE META AGNET RESPONDED SHOULD NOT CALLED AGAIN
            4. THEN MANAGER CALLS CODER AGENT FOR CODE GENERATION
            5. THEN CODER AGENT CALLS FEEDBACK AGENT FOR CODE VALIDATION
            6. IF FEEDBACK AGENT SAYS REJECTED THEN CODER AGENT SHOULD FIX THE CODE
            7. IF FEEDBACK AGENT SAYS APPROVED THEN MANAGER SHOULD EXPLAIN THE FINAL RESPONSE TO THE ASK OF THE USER REQUEST DIRECTLY IN THE END.
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

            If you do this -> you are WRONG

"""
        )

        exec_result = executor.run_code(
        code=None,  # since file already exists
        filename="generated_code/main.py"
        )       
        output = exec_result.get("output", "")

        # Step 3: Send to result agent
        final_response = result_agent.generate_reply(
            messages=[{"role": "user", "content": output}]
        )

        print(final_response)


        print("[OK] Task completed")

    except Exception as e:
        print(f"[ERROR] {e}")

import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        request = sys.argv[1]
    else:
        import os
        abs_csv = os.path.abspath(os.path.join("generated_code", "Input", "input.csv")).replace("\\", "/")
        question = "Tell me which country has more holiday"
        request = f"{question}. STRICT INSTRUCTION: The absolute filepath for the input CSV is: '{abs_csv}'. YOU MUST USE THIS EXACT COMPLETE PATH IN ALL YOUR CODE."

    analyze_request_groupchat(request, metadata_text)


