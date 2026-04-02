import os
import re

def parse_skill_file(filepath: str) -> dict:
    """
    Parses a SKILL.md file to extract the YAML frontmatter and the remaining instructions.
    Returns a dictionary with 'name', 'description', and 'instructions'.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by --- to separate YAML frontmatter from markdown content
        parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
        
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            instructions = parts[2].strip()
        else:
            frontmatter = ""
            instructions = content.strip()

        # Extract name and description from frontmatter
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)

        name = name_match.group(1).strip().strip('"\'') if name_match else "unknown"
        description = desc_match.group(1).strip().strip('"\'') if desc_match else "No description provided."

        return {
            "name": name,
            "description": description,
            "instructions": instructions
        }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def load_skills(skills_dir: str) -> list:
    """
    Scans the skills directory and loads all available skills.
    Returns a list of dictionaries containing skill details.
    """
    skills = []
    if not os.path.isdir(skills_dir):
        print(f"Skills directory not found: {skills_dir}")
        return skills

    for item in os.listdir(skills_dir):
        item_path = os.path.join(skills_dir, item)
        if os.path.isdir(item_path):
            skill_file = os.path.join(item_path, "SKILL.md")
            if os.path.isfile(skill_file):
                skill_data = parse_skill_file(skill_file)
                if skill_data:
                    # Use the folder name as a fallback or explicit identifier if needed
                    skill_data['folder_name'] = item 
                    skills.append(skill_data)
    
    return skills
