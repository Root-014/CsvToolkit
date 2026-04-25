import autogen
import os
import re
import json
from autogen import AssistantAgent



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
    "max_tokens": 3000,
}

llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
    "max_tokens": 3000,
}

phase1_manager_prompt = lambda user_request, is_followup=False, history_summary=None: f"""
YOU ARE THE PHASE 1 PLANNING MANAGER (STRICT CONTROLLER)
USER REQUEST : {user_request}
{"(THIS IS A FOLLOW-UP REQUEST. BUILD UPON THE EXISTING PLAN AND CODE.)" if is_followup else ""}

{"====================================" if history_summary else ""}
{f"CONVERSATION HISTORY & STATE:\n{history_summary}" if history_summary else ""}
{"====================================" if history_summary else ""}

YOUR TEAM:
====================================
- Metadata_Specialist: Dataset and Implementation Plan expert

WORKFLOW (MANDATORY)
====================================
1. Review the CONVERSATION HISTORY (if provided) to understand what has been done so far.
2. Instruct the Metadata_Specialist to output the implementation plan document based on the dataset metadata and user request. Ensure you tell them to ONLY output the plan document and no conversational text.
3. Finalize the plan and present it to the UserProxy.

PROACTIVE GUIDANCE:
====================================
If the history contains 'Proactive Suggestions' that are relevant to the current request, incorporate them into your instructions to the Planner.

COMMUNICATION RULES (STRICT)
====================================
- YOU MUST COMMUNICATE ONLY VIA PLAIN TEXT MESSAGES.
- NEVER USE TOOL CALLS OR FUNCTION CALLS.
- NEVER USE JSON FORMAT FOR COMMUNICATION.
- Address team members by name (e.g., "Metadata_Specialist, please provide information about the dataset [filename]").
- DO NOT GENERATE ANY PYTHON CODE.
"""

summarizer_prompt = """
YOU ARE THE ECOSYSTEM CONTEXT MANAGER.
Your goal is to compress a conversation into a "Persistent State" for the next turn.

INPUT:
1. Current History Summary (if any)
2. Latest Conversation Logs (The session that just finished)

OUTPUT FORMAT (STRICT JSON):
{
  "history_summary": "Short 2-3 sentence overview of the conversation so far.",
  "key_findings": ["Bullet points of what was learned from the data"],
  "active_files": ["List of generated csv/png/py files"],
  "proactive_suggestions": ["Next logical steps for the user based on findings"]
}

STRICT RULE: Be extremely concise. Keep the summary under 100 words. DO NOT output anything but the JSON.
"""

phase2_manager_prompt = """
YOU ARE THE PHASE 2 EXECUTION MANAGER (STRICT CONTROLLER)

====================================
YOUR TEAM:
====================================
- Coder: Python code generator
- Executor: Code execution environment
- Validator: Verifies code correctness

====================================
WORKFLOW (MANDATORY)
====================================
1. REVIEW the verified implementation plan provided in the initial message.
2. Instruct the Coder PROPERLY and COMPLETELY , to implement the logic based on that plan and any user comments.(Keep the instruction deep, clean and mention the dataset column names properly.)
3. Coordinate between Coder, Executor, and Validator until the task is complete.
4. On approval, provide the final response and exit.

====================================
COMMUNICATION RULES (STRICT)
====================================
- USE PLAIN LANGUAGE. Do NOT use colon-prefixed tags (Coder:, Executor:, etc.).
- ONLY THE CODER HAS AUTHORIZATION TO WRITE CODE.
"""

#{f"CONVERSATION HISTORY & STATE:\n{history_summary}\n" if history_summary else ""}


metaagent_prompt = lambda user_request, metadata_text, current_plan=None, current_code=None, history_summary=None: f""" 
    You are a METADATA AND PLANNING SPECIALIST.

    USER REQUEST : {user_request}

    METADATA : {metadata_text}


    ROLE:
        Your exact workflow is:
        1. Read the latest question/instruction from the MANAGER agent.
        2. Analyze the provided METADATA input.
        3. Synthesize the Manager's questions and the original USER REQUEST.
        4. Write a formal Implementation Plan that explicitly instructs and helps the CODER agent.

        - Your SOLE PURPOSE is to output this formal Implementation Plan Document.
        - DO NOT output conversational text, preambles, or metadata analysis outside of the plan document itself.
        - The metadata analysis (e.g. identified column names, data types, file paths) MUST be integrated naturally into the "Data Source" or "Context" section of your plan.
        - Provide the EXACT PATH for each file (e.g., "generated_code/Input/filename.csv") within the plan.
        - STRICT EFFICIENCY: Check 'key_findings' and 'active_files'. If columns were already identified or data was already processed in previous turns, REUSE that information.
        - The plan should be concise and clear.
        - **FEEDBACK LOOP**: If the `current_plan` contains user comments, review notes, or modifications (e.g., text in brackets [ ], or lines starting with "NOTE:", "USER:"), YOU MUST prioritize and incorporate these changes into the updated plan.
        - Write exact data specifications, what columns to filter, sort, and process in detail.
        - Break down the requirements into an actionable items within the plan to guide the CODER agent.
        - Keep it clear and simple. DON'T make it complicated.

    REQUIREMENTS:
        - Your ENTIRE RESPONSE will be saved directly as the `implementation_plan.md` file, so format it as a valid Markdown document.
        - Describe the detailed explanation of the logic needs to be precise and clear.
        - SQL INTEGRATION: If multiple files or Parquet files are involved, suggest using DuckDB SQL for efficient data handling in your plan.
        - End your output with "PLAN_GENERATED" on its own line.

    AMBIGUITY HANDLING & OPEN QUESTIONS: (Only If needed Important Questions)
        - If the user request is underspecified, vague, or if you are unsure about the data/logic:
            1. State your assumptions clearly.
            2. ADD a section titled "## Open Questions" at the very TOP of your implementation plan.
            3. List specific questions for the user to answer during the review.
            4. Ask only the important once (meaning without that answer you can't proceed further).
        
    STRICT RULES Do/DON'T:
        - DO NOT GENERATE EXECUTABLE PYTHON CODE HERE. ONLY THE CODER PERFORMS CODE GENERATION.
        - Be concise but complete.
        - Don't include anything unnecessary.
        - USE EXACT COLUMN NAMES and specify which FILE they belong to if multiple files exist.
        """

coder_agent_prompt = """
You are a PYTHON CODE SPECIALIST.

- Generate clean, efficient, optimized executable Python code based on Manager's instructions
- Follow best practices
- Include error handling
- save the code whenever you complete the code

YOUR STRONG AREA:
    - PANDAS
    - NUMPY
    - PLOTLY

FOR PLOTS USE PLOTLY ONLY :
    1. Keep it minimal and neat diagram.
    2. Don't use too much color.
    3. Always save the them as .html and also display them


STRICT RULES:
    - OUTPUT ONLY CODE. No explanations, no text outside the code block.
    - DO NOT EXECUTE CODE. Only the Executor agent is permitted to execute code.
    - FOLLOW THE IMPLEMENTATION PLAN RIGOROUSLY. Limit assumptions, strictly implement the verified design.
    - DO NOT request additional information.
    - DO NOT provide suggestions or analysis.
    - DO NOT add extra features beyond the requested task.
    - If input details are missing, use placeholders or minimal assumptions inside the code.
    - Ensure the code runs without modification.
    - CREATE CHARTS UNTIL REQUESTED BY THE MANAGER (save it in the output folder).

CODE REQUIREMENTS:
    - Always include necessary imports (e.g., pandas, duckdb).
    - DUCKDB & SQL: For Parquet files YOU MUST USE DUCKDB ELSE YOU CAN USE PANDAS FOR CSV.
        - **MANDATORY PATTERN**:
          ```python
          import duckdb
          conn = duckdb.connect()
          query = "SELECT * FROM read_parquet('generated_code/Input/filename.parquet')"
          df = conn.execute(query).df()
          ```
        - **STRICT EXTENSION RULE**: Do NOT append `.csv` to `.parquet` filenames. Use the exact filename provided in the metadata.
    - FILE PATHS: All datasets are stored in "generated_code/Input/". Use the specific filename(s) provided in the metadata or implementation plan.
    - Use try/except for error handling.
    - **SAFE PRINTING**: Whenever printing a DataFrame, ALWAYS use `.head()` (e.g., `print(df.head())`) to prevent overflowing the terminal with massive logs.
    - Follow the provided implementation plan precisely.


RESPONSE FORMAT:
    - Provide the complete code in a code block 

    OP FORMAT
        eg : 
    ```python
    # code here
    ```
    TERMINATE
STRICTLY CODE ONLY 

If you need any information then ask Manager AGENT for that.
"""
executor_prompt = """
YOU ARE A PYTHON CODE EXECUTION SPECIALIST.


OUTPUT FORMAT:
-> STATUS : <EXECUTED/ERROR>
        - If execution returns error -> STATUS: ERROR
        - If output satisfies user request -> STATUS: EXECUTED
        - Otherwise -> STATUS: ERROR
IF STATUS = ERROR
    -> REASON: <brief, precise justification: WHY CODE FAILED OR NOT ABLE TO RUN>

-> OUTPUT: <brief, precise justification: CODE OUTPUT>


"""
validate_agent_prompt = lambda user_request: f""" 
You are a VALIDATOR & RESULT INTERPRETER AGENT.

INPUT:
    - USER REQUEST: {user_request}
    - CODE OUTPUT: CODE EXECUTOR OUTPUT
    - CODE : FROM CODER AGENT

ROLE:
    - When you start/ask to validate the code check whether it satisfies the USER REQUEST.
    - If the code is not able to run or gives error then respond what's the error and root cause.
    - Perform strict technical validation.
    - IF AND ONLY IF THE STATUS IS APPROVED: ALSO convert the CODE OUTPUT into a clear, user-facing answer (Result Interpretation).

STEPS: 
    1. Check the output.
    2. Compare the output with the USER REQUEST.
    3. Respond with the format given below.

STRICT RULES:
    - DO NOT WRITE OR GENERATE ANY CODE YOURSELF.
    - DO NOT modify or rewrite the code in your response.
    - DO NOT suggest improvements.
    - DO NOT assume missing logic is acceptable.
    - APPROVE only if the code is 100% correct and complete.
    - If any issue exists, mark as NOT APPROVED.

VALIDATION CHECKLIST (MANDATORY):
    - Does the code fully satisfy the USER REQUEST?
    - Are all required imports present?
    - Are variables properly defined?
    - Is the logic complete and correct?
    - Will the code run without errors?
    - Is error handling present where needed?

REJECTION CONDITIONS:
    - Missing or incorrect logic
    - Partial implementation
    - Undefined variables or imports
    - Runtime failure possibility
    - Misalignment with USER REQUEST


===============================================
OUTPUT FORMAT (STRICT - NO DEVIATION):
===============================================

### 🛡️ Validation Report

**STATUS**: <APPROVED/ERROR>
- **REASON**: <brief, precise justification: either why code is correct or list specific issues>

---
#### 📋 Request Details
- **USER REQUEST**: {user_request}

---
#### 🚀 Execution Response
```text
<complete code execution output, exactly as returned by the executed code>
```

---
<!-- FINAL_ANSWER_START -->
### 🎯 Final Answer
(ONLY GENERATE THIS SECTION IF STATUS IS APPROVED)
<Convert the CODE OUTPUT into a clear, user-facing answer.>
- Maximum 80 words
- Be concise, precise, and structured
- Use bullet points ONLY when it improves clarity
- Avoid repeating raw data unless necessary
- Use Markdown (tables, bold, lists) to make the response highly readable.
- **TABLES**: Ensure tables have exactly one header row followed by one separator row (|---|). Do NOT repeat separators.
<!-- FINAL_ANSWER_END -->

TERMINATION:
    - End immediately after response
"""

request_prompt = lambda request, code_output, history_summary=None: f"""
    You are a RESULT INTERPRETER.

    INPUT:
        USER REQUEST: {request}
        CODE OUTPUT: {code_output}
        {f"CONVERSATION HISTORY & STATE:\n{history_summary}\n" if history_summary else ""}

    ROLE:
    - Convert the CODE OUTPUT into a clear, user-facing answer.
    - Base your response primarily on the CODE OUTPUT, but use the CONVERSATION HISTORY for context (e.g., referencing previous findings or terms).
    - Do NOT infer, assume, or add external knowledge.

    STRICT RULES:
    - Do NOT explain the code.
    - Do NOT describe how the result was generated.
    - Do NOT add assumptions or interpretations beyond the output.
    - If the output is empty, null, or unclear, respond: "No result available".
    - If the output contains an error, summarize the error clearly.

    RESPONSE CONSTRAINTS:
    - Maximum 80 words
    - Be concise, precise, and structured
    - Use bullet points ONLY when it improves clarity
    - Avoid repeating raw data unless necessary

    OUTPUT FORMAT (STRICT MARKDOWN):
        ### 🎯 Final Answer
        
        <PROVIDE CLEAR, STRUCTURED MARKDOWN RESPONSE BASED ON OUTPUT>

    FORMATTING RULES:
        - Use Markdown (tables, bold, lists) to make the response highly readable.
        - **TABLES**: Ensure tables have exactly one header row followed by one separator row (`|---|`). Do NOT repeat separators.
        - Do not repeat the user's request; focus purely on the answer.
        - Ensure headers are used for separate points if necessary.
        - Keep RESPONSE clean and readable.

        TERMINATION:
        - End immediately after the RESPONSE
            """
class ExecutorAgent(AssistantAgent):
    def __init__(self, name="Executor"):
        super().__init__(name=name)

    def execute_generated_code(self) -> str:
        """
        This func helps to run the code generated by the coder agent.
        No need to pass anything
        """
        
        import subprocess
        import os

        try:
            code_path = os.path.join("generated_code", "main.py")

            result = subprocess.run(
                ["python", code_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if error:
                return f"ERROR:\n{error}\nOUTPUT:\n{output}"

            # print(output)
            return f"OUTPUT:\n{output}"

        except Exception as e:
            return f"Execution exception: {str(e)}"


    def respond(self):
        """
        This will be called by AutoGen when it's this agent's turn.
        We just run the code and return the output.
        """
        output = self.execute_generated_code()  # call your function
        return print(f"ExecutorAgent ran code, output:\n{output}")

class Agents:
    def get_llm_config(self, temperature=0.5, max_tokens=2000):
        return {
            "config_list": [self.config_list],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def __init__(self, model='qwen3.5:cloud', base_url='http://localhost:11434/v1', api_key='gemma3', api_type='openai', price=[0.0, 0.0], OUTPUT_DIR='.', metadata=None):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.api_type = api_type
        self.price = price
        self.OUTPUT_DIR = OUTPUT_DIR
        self.metadata = metadata if metadata else "No metadata available."
        self.config_list = {
            "model": self.model,
            "base_url": self.base_url,
            "api_key": self.api_key,
            "api_type": self.api_type,
            "price": self.price
        }

    def is_termination_msg(self, msg):
        if msg is None:
            return False
        content = msg.get("content", "")
        return "TERMINATE" in content or "APPROVED" in content or "EXIT" in content

    def is_termination_msg_v2(self, msg):
        content = msg.get("content", "").strip()
        # Exact match on dedicated line
        return  bool(re.search(r'^(STATUS:\s*APPROVED|TERMINATE|EXIT)$', content, re.MULTILINE))

    def is_termination_msg_v3(self, msg):
        content = msg.get("content", "").strip()
        sender = msg.get("name") or msg.get("role")
        # print("sender :",sender)
        # print("response: ", (
        #     sender == "FeedbackAgent" and
        #     any(line.strip() == "STATUS: APPROVED" for line in content.splitlines())
        # ))
    

        return (
            sender == "FeedbackAgent" and
            any(line.strip().replace("*", "") == "STATUS: APPROVED" for line in content.splitlines())
        )

    def extract_code_from_response(self, response: str) -> str:
        try:
            match = re.search(r"```python(.*?)```", response, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return "No Python code block found."
        except Exception as e:
            return f"Error extracting code: {str(e)}"

    def extract_and_save_code(self, response: str, filename: str = r"generated_code\main.py") -> str:

        """
        When ever coder agent codes the code, this function will extract the code and save it in the generated_code folder.
        """
        code = self.extract_code_from_response(response)
        
        if code.startswith("Error") or code == "No Python code block found.":
            return code

        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)
            return f"Code extracted and saved to {os.path.abspath(filename)}"
        
        except Exception as e:
            return f"Error saving file: {str(e)}"

    def extract_and_save_plan(self, plan_text: str) -> str:
        try:
            # Clean up the plan text by removing the termination token and extra whitespace
            clean_plan_text = plan_text.replace("PLAN_GENERATED", "").strip()
            
            plan_path = os.path.join(self.OUTPUT_DIR, "implementation_plan.md")
            os.makedirs(os.path.dirname(plan_path), exist_ok=True)
            with open(plan_path, "w", encoding="utf-8") as f:
                f.write(clean_plan_text)
            return f"Plan extracted and saved to {os.path.abspath(plan_path)}"
        except Exception as e:
            return f"Error saving plan: {str(e)}"

    def read_verified_plan(self) -> str:
        """Read the verified implementation plan from disk, including any user annotations."""
        try:
            plan_path = os.path.join(self.OUTPUT_DIR, "implementation_plan.md")
            if os.path.exists(plan_path):
                with open(plan_path, "r", encoding="utf-8") as f:
                    return f.read()
            return ""
        except Exception as e:
            return f"Error reading plan: {str(e)}"

    def read_current_code(self) -> str:
        """Read the current generated code from disk."""
        try:
            code_path = os.path.join(self.OUTPUT_DIR, "generated_code", "main.py")
            if os.path.exists(code_path):
                with open(code_path, "r", encoding="utf-8") as f:
                    return f.read()
            return ""
        except Exception as e:
            return f"Error reading code: {str(e)}"

    def execute_generated_code(self) -> str:
        """
        This func helps to run the code generated by the coder agent.
        No need to pass anything
        """
        
        import subprocess
        import os

        try:
            code_path = os.path.join("generated_code", "main.py")

            result = subprocess.run(
                ["python", code_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if error:
                return f"ERROR:\n{error}\nOUTPUT:\n{output}"
            return f"OUTPUT:\n{output}"

        except Exception as e:
            return f"Execution exception: {str(e)}"

    def userproxy_agent_init(self):
        user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
            is_termination_msg=self.is_termination_msg_v3,
            code_execution_config={
                "work_dir": self.OUTPUT_DIR,
                "use_docker": False,
            },
            system_message="""Execute code when requested. Do not initiate conversations.""")
        return user_proxy

    def phase1_manager_init(self, user_request, is_followup=False, history_summary=None):
        phase1_manager = autogen.AssistantAgent(
            name="MANAGER",
            llm_config=self.get_llm_config(temperature=0.5),
            system_message=phase1_manager_prompt(user_request, is_followup=is_followup, history_summary=history_summary))
        return phase1_manager

    def context_manager_init(self):
        context_manager = autogen.AssistantAgent(
            name="Context_Manager",
            llm_config=self.get_llm_config(temperature=0),
            system_message=summarizer_prompt
        )
        return context_manager

    def phase2_manager_init(self):
        phase2_manager = autogen.AssistantAgent(
            name="MANAGER",
            llm_config=self.get_llm_config(temperature=0.5),
            system_message=phase2_manager_prompt)
        return phase2_manager

    def metadata_agent_init(self, user_request, metadata_text, current_plan=None, current_code=None, history_summary=None):
        meta_agent = autogen.AssistantAgent(
            name="Metadata_Specialist",
            llm_config=self.get_llm_config(temperature=0.5, max_tokens=3000),
            system_message=metaagent_prompt(user_request, metadata_text, current_plan=current_plan, current_code=current_code, history_summary=history_summary)
        )
        meta_agent.register_function(function_map={"extract_and_save_plan": self.extract_and_save_plan})
        return meta_agent

    def coder_agent_init(self):
        coder_agent = autogen.AssistantAgent(
            name="Coder",
            llm_config=self.get_llm_config(temperature=0.7, max_tokens=5000),
            system_message=coder_agent_prompt,
            is_termination_msg=self.is_termination_msg_v3,

        )
        coder_agent.register_function(function_map={"extract_and_save_code": self.extract_and_save_code})
        return coder_agent

    def validate_agent(self, user_request):
        feedback_agent = autogen.AssistantAgent(
            name="FeedbackAgent",
            llm_config=self.get_llm_config(temperature=0.3),
            is_termination_msg=self.is_termination_msg,
            system_message=validate_agent_prompt(user_request),
        )
        # feedback_agent.register_function(function_map={"python_code_executor": self.execute_generated_code})
        return feedback_agent

    def executor_agent_init(self):
        executor_agent = autogen.UserProxyAgent(
        name="Executor",
        llm_config = self.get_llm_config(temperature=0),
        code_execution_config={
                "work_dir": self.OUTPUT_DIR,
                "use_docker": False,
            },
        human_input_mode="NEVER",
        system_message="Execute Python code and return the output. Do not perform any other tasks.",
        )
        return executor_agent


    def result_agent_init(self, request, code_output, history_summary=None):
        result_agent = autogen.AssistantAgent(
            name="ResultInterpreter",
            llm_config=self.get_llm_config(temperature=0.5),
            system_message=request_prompt(request, code_output, history_summary=history_summary)
        )
        
        return result_agent
         
        
