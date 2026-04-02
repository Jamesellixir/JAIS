import os
from openai import OpenAI
from dotenv import load_dotenv
from skills_manager import load_skills

# Load environment variables, specifically OPENROUTER_API_KEY
load_dotenv()

# We use OpenRouter as a generic OpenAI-compatible endpoint to access free cloud models.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def call_cloud_worker(prompt: str, domain: str) -> str:
    """
    Calls a specialized cloud model based on the domain.
    If the domain matches a loaded skill, its specific instructions are injected into the system prompt.
    """
    if not OPENROUTER_API_KEY:
        return "ERROR: OPENROUTER_API_KEY environment variable is not set. Cloud workers are unavailable until you provide an API key."

    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )

    # Map domains to specific free models on OpenRouter
    model_mapping = {
        "coding": "openrouter/auto",
        "general": "openrouter/auto",
        "creative": "openrouter/auto", 
        "math": "openrouter/auto"
    }

    selected_model = model_mapping.get(domain, "openrouter/auto")

    print(f"  [Worker System] Delegating to cloud model: {selected_model}")
    
    # Load available skills mapped from the skills folder
    skills_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
    available_skills = load_skills(skills_dir)
    
    # Check if the domain matches a specific skill and retrieve its instructions
    skill_instructions = ""
    for skill in available_skills:
        if skill['name'] == domain:
            skill_instructions = skill['instructions']
            break
            
    if skill_instructions:
        system_content = f"You are an expert AI worker specializing in {domain}. Answer the user's prompt directly and accurately. Do not include meta-commentary, just provide the result or code.\n\nHere are the specific rules and instructions you MUST follow for this skill:\n\n{skill_instructions}"
    else:
        system_content = f"You are an expert AI worker specializing in {domain}. Answer the user's prompt directly and accurately. Do not include meta-commentary, just provide the result or code."

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: Failed to call cloud worker: {str(e)}"
