import xml.etree.ElementTree as ET
import re

file_path = "Epstine_File.docx" 

print(f"Attempting to recover {file_path}...")

try:
    # Use 'utf-8-sig' to automatically handle hidden Windows BOM characters
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        raw_content = f.read().strip()

    # REMOVE AI GARBAGE: Strip ```xml or other markdown wrappers if they exist
    clean_xml = re.sub(r'^```[a-z]*\s*', '', raw_content)
    clean_xml = re.sub(r'```$', '', clean_xml).strip()

    # Standard Word namespaces
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    # Attempt to parse the XML
    root = ET.fromstring(clean_xml)
    text_parts = []

    # Find all paragraph tags and extract the text inside them
    for p in root.findall('.//w:p', ns):
        # Join all text pieces within a single paragraph
        paragraph_text = "".join([t.text for t in p.findall('.//w:t', ns) if t.text])
        if paragraph_text:
            text_parts.append(paragraph_text)

    # Save to a clean text file
    with open("RECOVERED_FINAL.txt", "w", encoding='utf-8') as f:
        f.write("\n\n".join(text_parts))

    print("✅ SUCCESS! Your text is now in 'RECOVERED_FINAL.txt'")

except Exception as e:
    print(f"❌ Standard extraction failed: {e}")
    print("🛠️ Switching to Brute Force mode...")
    
    # BRUTE FORCE: Just find anything sitting between <w:t> tags
    # This works even if the XML structure is totally broken
    brute_text = re.findall(r'<w:t.*?>(.*?)</w:t>', raw_content)
    
    with open("RECOVERED_BRUTEFORCE.txt", "w", encoding='utf-8') as f:
        f.write("\n\n".join(brute_text))
        
    print("✅ DONE! Check 'RECOVERED_BRUTEFORCE.txt' for your data.")