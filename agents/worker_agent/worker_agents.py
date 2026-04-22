import autogen
import os
import re
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

phase1_manager_prompt = lambda user_request, :"""
YOU ARE THE PHASE 1 PLANNING MANAGER (STRICT CONTROLLER)
USER REQUEST : {user_request}

====================================
YOUR TEAM:
====================================
- MetaAgent: Dataset expert (ask about any info related to the dataset ONLY)
- Planner: Implementation Plan Specialist

====================================
WORKFLOW (MANDATORY)
====================================
1. Immediately ask MetaAgent about any info related to the dataset ONLY which are cam be related to user request.
    example : "I need to understand the input dataset. What is the exact column name for 'Fcst_BaselineFcst_Baseline' in the Final_Merge dataset?"
2. Once the MetaAgent provides the metadata:
    * Do not ask the MetaAgent for more info unless absolutely necessary.
    * Signal ready status by responding: METADATA_READY
3. Instruct the Planner to generate an implementation plan based on the metadata and user request.
4. Finalize the plan and present it to the UserProxy.

Note: NO TOOL AVAILABLE

====================================
COMMUNICATION RULES (STRICT)
====================================
- Speak to ONLY ONE agent at a time.
- USE PLAIN LANGUAGE. Do NOT use colon-prefixed tags like "MetaAgent:" or "Planner:". Simply address them in your message (e.g., "MetaAgent, please provide the schema").
- NEVER ask Coder (Coder does not exist yet).
- DO NOT GENERATE ANY PYTHON CODE.
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
2. Instruct the Coder to implement the logic based on that plan and any user comments.(Keep the instruction deep, clean and mention the dataset column names properly.)
3. Coordinate between Coder, Executor, and Validator until the task is complete.
4. On approval, provide the final response and exit.

====================================
COMMUNICATION RULES (STRICT)
====================================
- USE PLAIN LANGUAGE. Do NOT use colon-prefixed tags (Coder:, Executor:, etc.).
- ONLY THE CODER HAS AUTHORIZATION TO WRITE CODE.
"""

metaagent_prompt = lambda metadata_text: f""" 
    
    You are a METADATA SPECIALIST.

    METADATA : {metadata_text}

    ROLE:
        - Answer only to questions asked by the Manager.
        - Identify column names, data types, and relationships if needed.
        - Provide concise, factual information. Be direct.

    DO/DON'T:
        - DON'T GIVE ANY SUGGESTION JUST RESPOND FOR WHAT WAS ASKED.
        - DON'T WRITE ANY CODE OR PLAN.
        - STRICTLY DON'T ASK ANY FOLLOW UP QUESTIONS
        - SHOULD NOT GIVE ANY INFORMATION THAT WAS NOT REQUESTED.

    RESPONSE FORMAT:
        - When asked about columns or structure, respond with:
            - Exact column names (copy from metadata)
            - Data types
            - Any relevant notes about the data
            - Force consistent bullet format
            - Explicit section headers

    ALLOWED OUTPUT:
        - Column names
        - Data types
        - Schema-related notes (keys, constraints, relationships if explicitly present)
    
    FINAL LINE:
        METADATA_READY
        """

planner_prompt  =  lambda user_request: f"""
You are a PLANNER SPECIALIST.

USER REQUEST : {user_request}

ROLE:
    - Based on the user's request  and the metadata provided by the MetaAgent, construct a clear implementation plan.
    - Write exact data specifications, what columns to filter, sort, and process.
    - Break down the requirements into an actionable checklist.
    - Keep it clear and simple. DON'T make it complicated.
    
REQUIREMENTS:
    - Describe the detailed explanation of the logic needs to be precise and clear.
    - Provide a markdown checklist (e.g., `- [ ] Load data`)
    - Call the function extract_and_save_plan with your final planning document to save it to disk.
    - End your output with "PLAN_GENERATED"
    
STRICT RULES Do/DON'T:
    - DO NOT GENERATE EXECUTABLE PYTHON CODE HERE. ONLY THE CODER PERFORMS CODE GENERATION.
    - Be concise but complete.
    - Don't include anything unnecessary.
    - DO NOT WRITE ANY CODE.
    - USE EXACT COLUMN NAMES.
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
    - Always include necessary imports (e.g., pandas and others if required).
    - Include inline comments for clarity.
    - Use try/except for error handling.
    - Print results or save outputs as appropriate to the task.

RESPONSE FORMAT:
    - Provide the complete code in a code block 

    eg : 
```python
# code here
```
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
You are a VALIDATOR AGENT.

INPUT:
    - USER REQUEST: {user_request}
    - CODE OUTPUT: CODE EXECUTOR OUTPUT
    - CODE : FROM CODER AGENT
ROLE:
    - When you start/ask to validate the code check whether it satisfies the USER REQUEST.
    - If the code is not able to run or gives error then respond what's the error and root cause.
    - Perform strict technical validation.

STEPS: 
    1. Check the output.
    2. Compare the output with the USER REQUEST.
    3. Respond the response with the format given.

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
OUTPUT FORMAT AFTER CODE EXECCUTION (STRICT - NO DEVIATION):
===============================================

STATUS: <APPROVED/ERROR>
        - If execution returns error -> STATUS: ERROR
        - If output satisfies user request -> STATUS: APPROVED
        - Otherwise -> STATUS: ERROR
REASON: <brief, precise justification: either why code is correct or list specific issues>

REQUEST: <USER REQUEST>

RESPONSE:
<complete code execution output, exactly as returned by the executed code>

TERMINATION:
    - End immediately after output
        """

request_prompt = lambda request, code_output: f"""
    You are a RESULT INTERPRETER.

    INPUT:
        USER REQUEST: {request}
        CODE OUTPUT: {code_output}

    ROLE:
    - Convert the CODE OUTPUT into a clear, user-facing answer.
    - Base your response STRICTLY on the provided CODE OUTPUT.
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

    OUTPUT FORMAT (STRICT):
        REQUEST: <USER REQUEST>
        RESPONSE: <FINAL ANSWER BASED ONLY ON OUTPUT>

    FORMATTING RULES:
        - Do not add extra headings or text unless it was needed.
        - Do not modify the REQUEST text.
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
    def __init__(self, model='qwen3.5:cloud', base_url='http://localhost:11434/v1', api_key='gemma3', api_type='openai', price=[0.0, 0.0], OUTPUT_DIR='.'):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.api_type = api_type
        self.price = price
        self.OUTPUT_DIR = OUTPUT_DIR
        self.config_list = {
            "model": self.model,
            "base_url": self.base_url,
            "api_key": self.api_key,
            "api_type": self.api_type,
            "price": self.price
        }
        self.llm_config = {
            "config_list": self.config_list,
            "temperature": 0.5,
            "max_tokens": 2000,
        }
        self.llm_config_2 = {
            "config_list": self.config_list,
            "temperature": 0.7,
            "max_tokens": 5000,
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
            any(line.strip() == "STATUS: APPROVED" for line in content.splitlines())
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
            plan_path = os.path.join(self.OUTPUT_DIR, "implementation_plan.md")
            os.makedirs(os.path.dirname(plan_path), exist_ok=True)
            with open(plan_path, "w", encoding="utf-8") as f:
                f.write(plan_text)
            return f"Plan extracted and saved to {os.path.abspath(plan_path)}"
        except Exception as e:
            return f"Error saving plan: {str(e)}"

    def read_verified_plan(self) -> str:
        """Read the verified implementation plan from discourse, including any user annotations."""
        try:
            plan_path = os.path.join(self.OUTPUT_DIR, "implementation_plan.md")
            if os.path.exists(plan_path):
                with open(plan_path, "r", encoding="utf-8") as f:
                    return f.read()
            return "No verified plan found."
        except Exception as e:
            return f"Error reading plan: {str(e)}"

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

    def phase1_manager_init(self,user_request):
        phase1_manager = autogen.AssistantAgent(
            name="MANAGER",
            llm_config=self.llm_config,
            system_message=phase1_manager_prompt(user_request))
        return phase1_manager

    def phase2_manager_init(self):
        phase2_manager = autogen.AssistantAgent(
            name="MANAGER",
            llm_config=self.llm_config,
            system_message=phase2_manager_prompt)
        return phase2_manager

    def metadata_agent_init(self, metadata_text):
        meta_agent = autogen.AssistantAgent(
            name="MetaAgent",
            llm_config=self.llm_config,
            system_message=metaagent_prompt(metadata_text)
        )
        return meta_agent

    def planner_agent_init(self,user_request):
        planner_agent = autogen.AssistantAgent(
            name="Planner",
            llm_config=self.llm_config,
            system_message=planner_prompt(user_request)
        )
        planner_agent.register_function(function_map={"extract_and_save_plan": self.extract_and_save_plan})
        return planner_agent

    def coder_agent_init(self):
        coder_agent = autogen.AssistantAgent(
            name="Coder",
            llm_config=self.llm_config_2,
            system_message=coder_agent_prompt,
            is_termination_msg=self.is_termination_msg_v3,

        )
        coder_agent.register_function(function_map={"extract_and_save_code": self.extract_and_save_code})
        return coder_agent

    def validate_agent(self, user_request):
        feedback_agent = autogen.AssistantAgent(
            name="FeedbackAgent",
            llm_config=self.llm_config,
            is_termination_msg=self.is_termination_msg,
            system_message=validate_agent_prompt(user_request),
        )
        # feedback_agent.register_function(function_map={"python_code_executor": self.execute_generated_code})
        return feedback_agent

    def executor_agent_init(self):
        executor_agent = autogen.UserProxyAgent(
        name="Executor",
        llm_config = self.llm_config,
        code_execution_config={
                "work_dir": self.OUTPUT_DIR,
                "use_docker": False,
            },
        human_input_mode="NEVER",
        system_message="Execute Python code and return the output. Do not perform any other tasks.",
    )
        return executor_agent


    def result_agent_init(self, request, code_output):
        result_agent = autogen.AssistantAgent(
            name="ResultInterpreter",
            llm_config=self.llm_config,
            system_message=request_prompt(request, code_output)
        )
        
        return result_agent
         
        
