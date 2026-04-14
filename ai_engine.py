import requests
import re
import json
import os

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')

def parse_guidance(text):
    """Parse raw LLM response into structured dict"""
    if not text or isinstance(text, dict):
        return {"summary": text or "No response", "risks": "", "steps": "", "laws": "", "documents": ""}
    
    guidance = {
        "summary": "Legal guidance generated",
        "risks": "",
        "steps": "",
        "laws": "",
        "documents": ""
    }
    
    # Extract sections using regex
    sections = {
        'category': r'Legal Category:\s*(.*?)(?=\n[A-Z]|$)',
        'laws': r'Applicable Laws / Sections:\s*(.*?)(?=\n[A-Z]|$)',
        'steps': r'Suggested Actions:\s*(.*?)(?=\n[A-Z]|$)',
        'notes': r'Important Notes:\s*(.*?)(?=\n[A-Z]|$)',
        'disclaimer': r'Disclaimer:\s*(.*?)(?=\n[A-Z]|$)'
    }
    
    for key, pattern in sections.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            if key == 'category':
                guidance['summary'] = content
            elif key == 'laws':
                guidance['laws'] = content
            elif key == 'steps':
                guidance['steps'] = content
            elif key == 'notes':
                guidance['risks'] = content
    
    # Handle image/documents mention
    if 'image' in text.lower() or 'document' in text.lower():
        guidance['documents'] = "Review uploaded image/document with a lawyer."
    
    return guidance

def get_legal_guidance(problem, image_path=None):
    """
    Get structured legal guidance from Ollama.
    Returns dict even on error for template compatibility.
    """
    prompt = f"""You are an expert Indian legal AI assistant. Analyze the user's legal issue and respond in this EXACT JSON format only:

{{
  "summary": "Short summary of legal category/issue (1 sentence)",
  "risks": "Key risks and considerations",
  "steps": "Step-by-step action plan",
  "laws": "Relevant laws/sections (Indian laws preferred)",
  "documents": "Documents needed or references"
}}

User input (keep confidential): {problem}

Provide professional, accurate guidance. If image mentioned, note visual analysis needed."""

    payload = {
        "model": os.getenv('OLLAMA_MODEL', 'minicpm-v:latest'),
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9
        }
    }

    # Vision support for image path
    if image_path and os.path.exists(image_path):
        payload["images"] = [image_path]

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            raw_response = result.get("response", "")
            
            # Try JSON parse first
            try:
                guidance = json.loads(raw_response)
                return guidance
            except json.JSONDecodeError:
                # Fallback to regex parsing
                return parse_guidance(raw_response)
        else:
            return {"summary": f"Ollama error: {response.status_code}", "risks": response.text[:200], "steps": "Check Ollama service", "laws": "", "documents": ""}

    except requests.exceptions.Timeout:
        return {"summary": "Request timeout", "risks": "AI service slow", "steps": "Try shorter input", "laws": "", "documents": ""}
    except Exception as e:
        return {"summary": f"Connection error", "risks": str(e), "steps": "Ensure Ollama running: ollama serve", "laws": "", "documents": ""}

