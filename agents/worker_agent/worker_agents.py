import autogen
import os
import re

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

manager_agent_prompt = """
YOU ARE THE MANAGER (STRICT CONTROLLER)

====================================
YOUR TEAM:
===================================

- MetaAgent: Dataset expert (ask about any info related to the dataset ONLY)
- Coder: Python code generator (request only for code generation)


- DON'T RUN METAAGENT AGAIN ONCE IT WAS CALLED EARLIER OR WHEN METADATA_READY IS RESPONDED.

EXAMPLE:
"MetaAgent : I need to understand the input dataset. What is the exact column name for 'Fcst_BaselineFcst_Baseline' in the Final_Merge dataset?"
"Coder : generate code to read the CSV file from the specified path and filter for holidays in the year 2026"

====================================
WORKFLOW (MANDATORY)
====================================

1. Ask MetaAgent first for ALL required dataset details in ONE message
    * Ask them in a pointed way
2. After receiving response:
    * Store the information
    * Always pass the format of the Time column to the coder agent.
    * Respond: METADATA_READY
3. NEVER call MetaAgent again
4. Ask Coder to generate code using metadata and request 
    - If plots are requested use plotly.
    - Always save the them as .html and also display them
5. IF Validator says REJECTED:
    * Ask Coder to fix using feedback
    * Repeat loop
6. IF Validator says Approved :
    * With final result you have to explain the final response to the ask of the user request directly in the end. FOLLOW THE FORMAT : 
            "REQUEST : <USER REQUEST> 
            "RESPONSE : <FINAL RESPONSE>" based with the code result
            "STATUS   : TERMINATE"
    * SEND "EXIT" to terminate the run.

7. DON'T CALL THE SAME AGENT AGAIN.

NOTE : DON'T CALL THE SAME AGENT WHICH SPOKE JUST NOW.

====================================
COMMUNICATION RULES (STRICT)
====================================

- Speak to ONLY ONE agent at a time
- ALWAYS prefix messages exactly as:
    MetaAgent:
    Coder:

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
- ONCE VALIDATOR RESULT MEETS THE ASK OF THE USER IMMEDIATELY EXIT DON'T GO BEYOND THAT.

====================================
FAILSAFE
====================================

If unsure or missing information:
 * Ask MetaAgent (only if METADATA phase not completed)

"""
metaagent_prompt = lambda metadata_text: f""" 
    
    You are a METADATA SPECIALIST.

    METADATA : {metadata_text}

    ROLE:
        - Answer questions asked by the Manager.
        - Identify column names, data types, and relationships
        - Provide concise, factual information. Be direct.
        - STRICTLY DON'T ASK ANY FOLLOW UP QUESTIONS
        - SHOULD NOT GIVE ANY INFORMATION THAT WAS NOT REQUESTED.
        - DON'T GIVE ANY SUGGESTION JUST RESPOND FOR WHAT WAS ASKED.
        
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
coder_agent_prompt = """
You are a PYTHON CODE SPECIALIST.

- Generate clean, efficient, optimized executable Python code based on Manager's instructions
- Follow best practices
- Include error handling

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
    - DO NOT ask questions.
    - DO NOT request additional information.
    - DO NOT provide suggestions or analysis.
    - DO NOT add extra features beyond the requested task.
    - If input details are missing, use placeholders or minimal assumptions inside the code.
    - Ensure the code runs without modification.
    - CREATE CHARTS UNTILL IT'S REQUESTED BY THE MANAGER (save it in the output folder).

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

validate_agent_prompt = lambda user_request: f""" 
You are a CODE VALIDATOR AGENT.

INPUT:
    - USER REQUEST: {user_request}
    - GENERATED CODE: CODER AGENT OUTPUT

***** FIRST EXECUTE THE CODE AND GET THE OUTPUT *****

ROLE:
    - Validate whether the generated code correctly and fully satisfies the USER REQUEST.
    - Perform strict technical validation before any execution.

STRICT RULES:
    - DO NOT modify or rewrite the code.
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
VALIDATION RULES: STATUS IS MUST
    - If execution returns error → STATUS: ERROR
    - If output satisfies user request → STATUS: APPROVED
    - Otherwise → STATUS: ERROR

STATUS: <APPROVED/ERROR>
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

class Agents:
    def __init__(self, model='minimax-m2.5:cloud', base_url='http://localhost:11434/v1', api_key='gemma3', api_type='openai', price=[0.0, 0.0], OUTPUT_DIR='.'):
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

    def is_termination_msg(self, msg):
        if msg is None:
            return False
        content = msg.get("content", "")
        return "TERMINATE" in content or "APPROVED" in content or "EXIT" in content

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
            is_termination_msg=self.is_termination_msg,
            code_execution_config={
                "work_dir": self.OUTPUT_DIR,
                "use_docker": False,
            },
            system_message="""Execute code when requested. Do not initiate conversations.""")
        return user_proxy

    def manager_agent_init(self):
        manager_agent = autogen.AssistantAgent(
            name="MANAGER",
            llm_config=self.llm_config,
            system_message=manager_agent_prompt)
        return manager_agent

    def metadata_agent_init(self, metadata_text):
        meta_agent = autogen.AssistantAgent(
            name="MetaAgent",
            llm_config=self.llm_config,
            system_message=metaagent_prompt(metadata_text)
        )
        return meta_agent

    def coder_agent_init(self):
        coder_agent = autogen.AssistantAgent(
            name="Coder",
            llm_config=self.llm_config,
            system_message=coder_agent_prompt,
            is_termination_msg=self.is_termination_msg,

        )
        coder_agent.register_function(function_map={"extract_and_save_code": self.extract_and_save_code})
        return coder_agent

    def validate_agent(self, user_request):
        feedback_agent = autogen.AssistantAgent(
            name="FeedbackAgent",
            llm_config=self.llm_config,
            system_message=validate_agent_prompt(user_request),
        )
        feedback_agent.register_function(function_map={"execute_generated_code": self.execute_generated_code})
        return feedback_agent

    def executor_agent_init(self):
        executor = autogen.UserProxyAgent(
            name="Executor",
            human_input_mode="NEVER",
            code_execution_config={
                "work_dir": "generated_code",
                "use_docker": False})
        return executor

    def result_agent_init(self, request, code_output):
        result_agent = autogen.AssistantAgent(
            name="ResultInterpreter",
            llm_config=self.llm_config,
            system_message=request_prompt(request, code_output)
        )
        
        return result_agent
         
        
