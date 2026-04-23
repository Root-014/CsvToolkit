import sys
import os
import re

with open('agentic_runner.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update the loop start
old_block = """        current_request = initial_request
        is_first_turn = True

        while True:
            # Read current context
            current_plan = agent_factory.read_verified_plan()
            current_code = agent_factory.read_current_code()
            
 

            
            # Initialize core agents for Phase 1
            user_proxy = agent_factory.userproxy_agent_init()
            phase1_manager = agent_factory.phase1_manager_init(current_request, is_followup=not is_first_turn)
            metadata_specialist = agent_factory.metadata_agent_init(metadata_text)
            planner_agent = agent_factory.planner_agent_init(current_request, current_plan=current_plan, current_code=current_code)"""

new_block = """        current_request = initial_request
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
            planner_agent = agent_factory.planner_agent_init(current_request, current_plan=current_plan, current_code=current_code)"""

# Clean up the whitespace issues in my target content
code = code.replace(old_block, new_block)

# If it didn't find the exact block (due to whitespace), try a regex or simpler match
if new_block not in code:
    # Try a more flexible match for the initialization block
    code = re.sub(
        r'current_request = initial_request\s+is_first_turn = True\s+while True:\s+# Read current context\s+current_plan = agent_factory.read_verified_plan\(\)\s+current_code = agent_factory.read_current_code\(\)\s+.*?\s+# Initialize core agents for Phase 1\s+user_proxy = agent_factory.userproxy_agent_init\(\)\s+phase1_manager = agent_factory.phase1_manager_init\(current_request, is_followup=not is_first_turn\)',
        new_block,
        code,
        flags=re.DOTALL
    )

with open('agentic_runner.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('agentic_runner.py loop updated.')
