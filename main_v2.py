import pandas as pd
import traceback
from agents.csv_analyzer import CSVAnalysisAgent
import os
import autogen
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


# ======================== Configuration Management (Same as before) ======================== #

@dataclass
class ModelConfig:
    """Centralized model configuration"""
    model: str
    base_url: str
    api_key: str
    api_type: str
    temperature: float = 0.7
    


class ModelType(Enum):
    """Available model types"""
    GENERAL = "general"
    CODING = "coding"
    ANALYSIS = "analysis"


class ConfigManager:
    """Manages all LLM configurations"""
    
    def __init__(self):
        self.configs = {
            ModelType.GENERAL: ModelConfig(
                model='minimax-m2:cloud',
                base_url='http://localhost:11434/v1',
                api_key='minimax-m2:cloud',
                api_type='openai',
                temperature=0.7,
                
            ),
            ModelType.CODING: ModelConfig(
                model='minimax-m2:cloud',
                base_url='http://localhost:11434/v1',
                api_key='minimax-m2:cloud',
                api_type='openai',
                temperature=0.5,
              
            ),
            ModelType.ANALYSIS: ModelConfig(
                model='glm-4.7-flash',
                base_url='http://localhost:11434/v1',
                api_key='glm-4.7-flash',
                api_type='openai',
                temperature=0.3,
                
            )
        }
    
    def get_llm_config(self, model_type: ModelType) -> Dict:
        """Get LLM config for specific model type"""
        config = self.configs[model_type]
        return {
            "config_list": [{
                'model': config.model,
                'base_url': config.base_url,
                'api_key': config.api_key,
                'api_type': config.api_type,
            }],
            "temperature": config.temperature,
            
        }


# ======================== Agent Factory (Updated) ======================== #

class AgentFactory:
    """Factory for creating all agents with consistent configuration"""
    
    def __init__(self, config_manager: ConfigManager, output_dir: str):
        self.config_manager = config_manager
        self.output_dir = output_dir
        self.agents = {}
        
    def create_user_proxy(self) -> autogen.UserProxyAgent:
        """Create user proxy agent - ONLY for code execution"""
        agent = autogen.UserProxyAgent(
            name="Executor",  # Renamed for clarity
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,  # Don't auto-reply
            is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
            code_execution_config={
                "work_dir": self.output_dir,
                "use_docker": False,
            },
            system_message="Execute code when requested. Do not initiate conversations."
        )
        self.agents['executor'] = agent
        return agent
    
    def create_coordinator(self) -> autogen.AssistantAgent:
        """Create coordinator agent - the hierarchical leader"""
        agent = autogen.AssistantAgent(
            name="Coordinator",
            llm_config=self.config_manager.get_llm_config(ModelType.GENERAL),
            system_message="""You are the COORDINATOR - the leader of a hierarchical team.

ROLE:
- Receive user requests and break them into subtasks
- Directly communicate with specialized agents
- Make decisions on workflow and next steps
- Aggregate results and ensure quality

YOUR TEAM:
- MetaAgent: Dataset structure expert (ask about columns, data types)
- Coder: Python code generator (request code generation)
- Validator: Code quality checker (request validation)

COMMUNICATION PROTOCOL:
When you need information from an agent:
1. State what you need clearly
2. Ask your question directly
3. Wait for their response
4. Use their response to guide next steps

EXAMPLE:
"MetaAgent, I need to understand the dataset structure. What is the exact column name for 'Fcst_BaselineFcst_Baseline' in the Final_Merge dataset?"

WORKFLOW:
1. Understand the user request
2. Ask MetaAgent for dataset information
3. Based on MetaAgent's response, instruct Coder to generate code
4. Ask Validator to check the code
5. If issues found, work with Coder to fix
6. When satisfied, respond with: TERMINATE

IMPORTANT:
- Always wait for responses before proceeding
- Make decisions based on team feedback
- Be specific in your requests to agents
"""
        )
        self.agents['coordinator'] = agent
        return agent
    
    def create_meta_agent(self) -> autogen.AssistantAgent:
        """Create metadata analysis agent"""
        agent = autogen.AssistantAgent(
            name="MetaAgent",
            llm_config=self.config_manager.get_llm_config(ModelType.ANALYSIS),
            system_message="""You are a METADATA SPECIALIST.

ROLE:
- Answer questions about dataset structure
- Identify column names, data types, and relationships
- Provide concise, factual information

RESPONSE FORMAT:
When asked about columns or structure, respond with:
- Exact column names (copy from metadata)
- Data types
- Any relevant notes about the data

Be direct and factual. Answer only what was asked.
"""
        )
        self.agents['meta_agent'] = agent
        return agent
    
    def create_coder(self) -> autogen.AssistantAgent:
        """Create code generation agent"""
        agent = autogen.AssistantAgent(
            name="Coder",
            llm_config=self.config_manager.get_llm_config(ModelType.CODING),
            system_message="""You are a PYTHON CODE SPECIALIST.

ROLE:
- Generate clean, executable Python code based on coordinator's instructions
- Follow best practices
- Include error handling

CODE REQUIREMENTS:
- Target file: "main.py"
- Import pandas and other needed libraries
- Include comments for clarity
- Handle potential errors
- Print results or save to file as appropriate

RESPONSE FORMAT:
Provide the complete code in a code block, then briefly explain what it does.
"""
        )
        self.agents['coder'] = agent
        return agent
    
    def create_validator(self) -> autogen.AssistantAgent:
        """Create validation agent"""
        agent = autogen.AssistantAgent(
            name="Validator",
            llm_config=self.config_manager.get_llm_config(ModelType.GENERAL),
            system_message="""You are a CODE VALIDATOR.

ROLE:
- Review code for correctness
- Check if it solves the requested task
- Identify potential issues

VALIDATION CHECKLIST:
✓ Does code match the task requirements?
✓ Are imports correct?
✓ Will it run without errors?
✓ Is error handling adequate?

RESPONSE FORMAT:
- If valid: "APPROVED: [brief reason]"
- If issues: "REJECTED: [specific issues]"
"""
        )
        self.agents['validator'] = agent
        return agent
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Return all created agents"""
        return self.agents


# ======================== FIXED: Direct Communication Orchestrator ======================== #

class DirectCommunicationOrchestrator:
    """
    Orchestrator where agents communicate directly without UserProxy relay
    This fixes the empty response issue
    """
    
    def __init__(self, agents: Dict[str, Any], metadata_path: str):
        self.agents = agents
        self.metadata_path = metadata_path
        self.metadata_cache = None
        
    def load_metadata(self) -> str:
        """Load and cache metadata"""
        if self.metadata_cache is None:
            with open(self.metadata_path, "r") as f:
                self.metadata_cache = f.read()
        return self.metadata_cache
    
    def execute_task(self, user_request: str) -> Dict[str, Any]:
        """
        Execute task using direct agent-to-agent communication
        
        Key Fix: Agents talk to each other directly via GroupChat
        Coordinator orchestrates, but agents respond to each other
        """
        print(f"\n{'='*60}")
        print(f"[ORCHESTRATOR] Processing: {user_request}")
        print(f"{'='*60}\n")
        
        coordinator = self.agents['coordinator']
        meta_agent = self.agents['meta_agent']
        coder = self.agents['coder']
        validator = self.agents['validator']
        
        # Load metadata
        metadata = self.load_metadata()
        
        # Create a group chat where agents can talk to each other
        groupchat = autogen.GroupChat(
            agents=[coordinator, meta_agent, coder, validator],
            messages=[],
            max_round=20,
            speaker_selection_method="auto",  # Let agents naturally respond
        )
        
        # Manager facilitates the conversation
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=coordinator.llm_config
        )
        
        # Initial message to coordinator with full context
        initial_message = f"""USER REQUEST: {user_request}

DATASET METADATA:
{metadata}

INSTRUCTIONS:
1. Analyze this request
2. Ask MetaAgent about the dataset structure
3. Based on MetaAgent's response, instruct Coder to generate code
4. Have Validator check the code
5. If issues, work with Coder to fix
6. When complete, respond with TERMINATE

Begin by asking MetaAgent about the relevant columns and data structure.
"""
        
        try:
            # Coordinator receives the task and starts orchestrating
            result = coordinator.initiate_chat(
                manager,
                message=initial_message
            )
            
            print(f"\n{'='*60}")
            print("[ORCHESTRATOR] Task execution completed")
            print(f"{'='*60}\n")
            
            return {
                'status': 'success',
                'result': result,
                'conversation_history': groupchat.messages
            }
            
        except Exception as e:
            print(f"[ERROR] Orchestration failed: {e}")
            traceback.print_exc()
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }


# ======================== ALTERNATIVE: Explicit Sequential Orchestrator ======================== #

class ExplicitSequentialOrchestrator:
    """
    Alternative approach: Coordinator explicitly calls each agent in sequence
    More control, more predictable
    """
    
    def __init__(self, agents: Dict[str, Any], metadata_path: str):
        self.agents = agents
        self.metadata_path = metadata_path
        self.metadata_cache = None
        
    def load_metadata(self) -> str:
        """Load and cache metadata"""
        if self.metadata_cache is None:
            with open(self.metadata_path, "r") as f:
                self.metadata_cache = f.read()
        return self.metadata_cache
    
    def execute_task(self, user_request: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Execute task with explicit sequential steps
        No UserProxy relay - agents talk directly
        """
        print(f"\n{'='*60}")
        print(f"[SEQUENTIAL ORCHESTRATOR] Processing: {user_request}")
        print(f"{'='*60}\n")
        
        coordinator = self.agents['coordinator']
        meta_agent = self.agents['meta_agent']
        coder = self.agents['coder']
        validator = self.agents['validator']
        
        metadata = self.load_metadata()
        
        try:
            # PHASE 1: Coordinator → MetaAgent
            print("[PHASE 1] Coordinator consulting MetaAgent...")
            
            # Create a simple 2-agent chat: Coordinator asks, MetaAgent answers
            meta_result = coordinator.initiate_chat(
                meta_agent,
                message=f"""I need your help understanding the dataset.

USER REQUEST: {user_request}

METADATA:
{metadata}

QUESTIONS:
1. What is the exact column name corresponding to 'Fcst_BaselineFcst_Baseline' in the 'Final_Merge' dataset?
2. Which column(s) represent the item level?
3. Any special considerations for aggregation?

Please answer each question clearly.
""",
                max_turns=2  # Coordinator asks, MetaAgent answers, done
            )
            
            # Extract MetaAgent's response
            meta_response = meta_result.chat_history[-1]['content'] if meta_result.chat_history else ""
            print(f"\n[MetaAgent Response]: {meta_response}\n")
            
            # PHASE 2: Coordinator → Coder
            print("[PHASE 2] Coordinator instructing Coder...")
            
            code_result = coordinator.initiate_chat(
                coder,
                message=f"""Based on MetaAgent's analysis, generate code for this task.

ORIGINAL REQUEST: {user_request}

METADATA INSIGHTS:
{meta_response}

Generate Python code that:
1. Loads the CSV from 'Input/input.csv'
2. Performs the requested aggregation
3. Saves results appropriately
4. Handles errors

Provide complete, executable code.
""",
                max_turns=2
            )
            
            code_response = code_result.chat_history[-1]['content'] if code_result.chat_history else ""
            print(f"\n[Coder Response]: {code_response[:200]}...\n")
            
            # PHASE 3: Coordinator → Validator
            print("[PHASE 3] Coordinator requesting validation...")
            
            validation_result = coordinator.initiate_chat(
                validator,
                message=f"""Review this code for the task.

ORIGINAL REQUEST: {user_request}

GENERATED CODE:
{code_response}

Validate and respond with APPROVED or REJECTED with specific issues.
""",
                max_turns=2
            )
            
            validation_response = validation_result.chat_history[-1]['content'] if validation_result.chat_history else ""
            print(f"\n[Validator Response]: {validation_response}\n")
            
            # PHASE 4: Iteration if needed
            iteration = 0
            while "REJECTED" in validation_response and iteration < max_iterations:
                iteration += 1
                print(f"\n[PHASE 4.{iteration}] Coordinator requesting code fixes...")
                
                code_result = coordinator.initiate_chat(
                    coder,
                    message=f"""The validator found issues. Please fix the code.

VALIDATION FEEDBACK:
{validation_response}

ORIGINAL CODE:
{code_response}

Provide corrected code.
""",
                    max_turns=2
                )
                
                code_response = code_result.chat_history[-1]['content'] if code_result.chat_history else ""
                
                # Re-validate
                validation_result = coordinator.initiate_chat(
                    validator,
                    message=f"""Review the updated code.

UPDATED CODE:
{code_response}

Validate again.
""",
                    max_turns=2
                )
                
                validation_response = validation_result.chat_history[-1]['content'] if validation_result.chat_history else ""
            
            print(f"\n{'='*60}")
            print(f"[SEQUENTIAL ORCHESTRATOR] Task completed in {iteration} iterations")
            print(f"{'='*60}\n")
            
            return {
                'status': 'success',
                'iterations': iteration,
                'final_validation': validation_response,
                'final_code': code_response
            }
            
        except Exception as e:
            print(f"[ERROR] Sequential orchestration failed: {e}")
            traceback.print_exc()
            return {
                'status': 'error',
                'error': str(e)
            }


# ======================== Main Application ======================== #

class CSVAgentSystem:
    """Main application coordinating everything"""
    
    def __init__(self, csv_file: str, output_dir: str):
        self.csv_file = csv_file
        self.output_dir = output_dir
        self.metadata_file = os.path.join(output_dir, 's.md')
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.agent_factory = AgentFactory(self.config_manager, output_dir)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
    def initialize_system(self) -> bool:
        """Initialize the complete system"""
        print("[INIT] Initializing CSV Agent System...")
        
        # Step 1: Analyze CSV and generate metadata
        try:
            print("[INIT] Analyzing CSV file...")
            agent = CSVAnalysisAgent()
            agent.load_csv(self.csv_file)
            results = agent.analyze(detailed=True)
            report_path = agent.generate_report(output_path=self.metadata_file)
            print(f"[OK] Metadata generated: {report_path}")
        except Exception as e:
            print(f"[ERROR] Failed to analyze CSV: {e}")
            return False
        
        # Step 2: Create all agents
        print("[INIT] Creating agent hierarchy...")
        self.agent_factory.create_user_proxy()
        self.agent_factory.create_coordinator()
        self.agent_factory.create_meta_agent()
        self.agent_factory.create_coder()
        self.agent_factory.create_validator()
        print("[OK] All agents created")
        
        # Step 3: Initialize orchestrators (BOTH FIXED VERSIONS)
        agents = self.agent_factory.get_all_agents()
        self.direct_orchestrator = DirectCommunicationOrchestrator(agents, self.metadata_file)
        self.sequential_orchestrator = ExplicitSequentialOrchestrator(agents, self.metadata_file)
        
        print("[OK] System initialized successfully!\n")
        return True
    
    def process_request(self, request: str, mode: str = "sequential") -> Dict[str, Any]:
        """
        Process a user request
        
        Args:
            request: User's task description
            mode: "sequential" (explicit steps) or "direct" (group chat)
        """
        if mode == "sequential":
            return self.sequential_orchestrator.execute_task(request)
        elif mode == "direct":
            return self.direct_orchestrator.execute_task(request)
        else:
            raise ValueError(f"Unknown mode: {mode}. Use 'sequential' or 'direct'")


# ======================== Usage Example ======================== #

if __name__ == "__main__":
    # Configuration
    CSV_FILE = 'generated_code/Input/input.csv'
    OUTPUT_DIR = 'generated_code'
    
    # Initialize system
    system = CSVAgentSystem(CSV_FILE, OUTPUT_DIR)
    
    if system.initialize_system():
        # Process request
        request = "agg the Final_Merge Fcst_BaselineFcst_Baseline by item level"
        
        print("\n" + "="*60)
        print("PROCESSING REQUEST:")
        print(f"'{request}'")
        print("="*60)
        
        # Use sequential mode (most reliable)
        result = system.process_request(request, mode="sequential")
        
        print("\n" + "="*60)
        print("EXECUTION RESULT:")
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Iterations: {result.get('iterations', 0)}")
            print(f"Validation: {result.get('final_validation', 'N/A')[:100]}...")
        print("="*60)