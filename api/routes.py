import agents.memory as memory_agent
import agents.tools as tools_agent
from agents.brain import AgentBrain

agent_brain = AgentBrain()

def handle_user_request(command_text: str) -> dict:
    """
    Main API endpoint handler for user requests.
    Executes fast local tools or routes to AI Agent Brain.
    """
    cmd = command_text.strip()
    if not cmd:
        return {"status": "empty", "response": ""}

    # 1. Fast Local Tool Interception (<0.005s)
    is_tool_handled, tool_reply = tools_agent.check_fast_local_tools(cmd)
    if is_tool_handled:
        return {
            "status": "success",
            "is_fast_tool": True,
            "response": tool_reply,
            "actions": []
        }

    # 2. AI Brain Orchestration
    clean_response, actions = agent_brain.process(cmd)
    
    # 3. Execute actions
    executed_results = []
    if actions:
        for intent, arg in actions:
            res = tools_agent.execute_tool(intent, arg, command_text=cmd)
            if res:
                executed_results.append(res)
                
    return {
        "status": "success",
        "is_fast_tool": False,
        "response": clean_response,
        "actions": actions,
        "executed_results": executed_results
    }

def get_system_status() -> dict:
    """Returns current system profile and state."""
    return {
        "user_title": memory_agent.get_user_title(),
        "assistant_name": memory_agent.get_assistant_name(),
        "memory_context": memory_agent.get_memory_context()
    }
