import json
import ollama
from workers import call_cloud_worker
from tools import AVAILABLE_TOOLS
from skills_manager import load_skills

import os
# Get the model name from environment, defaulting to a stable qwen version
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "qwen2.5:7b")

def analyze_and_route(user_prompt: str) -> str:
    """
    Uses the local Ollama model to analyze the user's prompt, determine the domain,
    and decide if local tools need to be executed.
    """
    print(f"\n[Main AI] Analyzing request using local {ROUTER_MODEL}...")
    
    # Load available skills mapped from the skills folder
    skills_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
    available_skills = load_skills(skills_dir)
    
    # Format skills for the prompt
    skills_prompt_list = "\n".join([f"- \"{s['name']}\": {s['description']}" for s in available_skills])
    
    # Extract domain names to validate routing
    domain_names = [s['name'] for s in available_skills]
    # Keep some generic fallback domains just in case
    domain_names.extend(["coding", "general", "creative", "math"])
    
    system_prompt = f"""
    You are the Main AI Coordinator. Your job is to analyze the user's request and determine how to route it.
    You have access to specialized Cloud Worker AIs and local tools.
    
    Here are the specialized domains (skills) you can route to based on the user's request:
    {skills_prompt_list}
    - "coding": General programming
    - "general": General knowledge
    - "creative": Creative writing
    - "math": Mathematics
    
    Available Local Tools:
    - "create_file": Used when the user wants to create, save, or write a file to the laptop.
    - "run_local_command": Used when the user wants to execute a terminal command.
    - "none": Used when the user just wants information or an answer.
    
    Output your decision strictly as a JSON object with the following keys:
    {{
        "domain": "<one of the domain names listed above>",
        "tool_needed": "<one of: create_file, run_local_command, none>",
        "worker_prompt": "<The exact prompt you will send to the cloud worker to execute the task>",
        "tool_arg_1": "<If tool matching create_file, put the FULL filepath here. If run_local_command, put the command here. Otherwise empty string.>"
    }}
    
    For "create_file", if no explicit path is given, default to the current directory with a logical name.
    IMPORTANT: ONLY return the JSON object, absolutely no other text.
    """
    
    try:
        response = ollama.chat(
            model=ROUTER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            format="json" # Force JSON output if the model supports it
        )
        
        router_decision_text = response['message']['content'].strip()
        print(f"  [Main AI] Decision: {router_decision_text}")
        
        try:
            decision = json.loads(router_decision_text)
        except json.JSONDecodeError:
            # Fallback if the model hallucinated markdown formatting
            cleaned = router_decision_text.replace("```json", "").replace("```", "").strip()
            decision = json.loads(cleaned)
            
        domain = decision.get("domain", "general")
        tool_needed = decision.get("tool_needed", "none")
        worker_prompt = decision.get("worker_prompt", user_prompt)
        tool_arg = decision.get("tool_arg_1", "")
        
        # Modify worker prompt depending on if a tool is needed
        if tool_needed == "create_file":
            worker_prompt += "\n\nCRITICAL INSTRUCTION: Output ONLY the raw file content. Do NOT include markdown code blocks, do NOT include explanations. Just the raw text/code that goes into the file."
            
        print(f"  [Main AI] Routing to '{domain}' worker...")
        worker_result = call_cloud_worker(worker_prompt, domain)
        
        if "ERROR" in worker_result and not "API key" in worker_result:
            return f"[FAILED] Worker failed: {worker_result}"
            
        # Execute tool if required
        if tool_needed == "create_file":
            print(f"  [Main AI] Executing local tool '{tool_needed}'...")
            if not tool_arg:
                return f"[FAILED] Router failed to specify a filepath for creation."
            # Call tool
            tool_status = AVAILABLE_TOOLS["create_file"]["function"](tool_arg, worker_result)
            return tool_status
            
        elif tool_needed == "run_local_command":
            print(f"  [Main AI] Executing local tool '{tool_needed}'...")
            if not tool_arg:
                return "[FAILED] Router failed to specify a command."
            # Call tool
            tool_status = AVAILABLE_TOOLS["run_local_command"]["function"](tool_arg)
            return tool_status
            
        else:
            # No tool needed, just return the worker's answer
            return f"[Cloud AI ({domain})]:\n{worker_result}\n"

    except Exception as e:
        return f"[FAILED] Main AI routing error: {str(e)}\nMake sure Ollama is running and the {ROUTER_MODEL} model is pulled."
