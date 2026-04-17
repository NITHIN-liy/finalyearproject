import requests
import re
import json
import os
import openai
from config import OLLAMA_URL, OLLAMA_MODEL, OPENAI_API_KEY

def parse_guidance(text):
    """Parse raw LLM response into structured dict if JSON fails"""
    if not text or isinstance(text, dict):
        return {"summary": text or "No response", "risks": "", "steps": "", "laws": "", "documents": ""}
    
    guidance = {
        "summary": "Legal guidance generated",
        "full_analysis": text,
        "risks": "",
        "steps": "",
        "laws": "",
        "documents": "",
        "follow_ups": []
    }
    
    # Simple regex parsing as fallback
    sections = {
        'summary': r'(?:Summary|Overview):\s*(.*?)(?=\n[A-Z]|$)',
        'laws': r'(?:Laws|Sections):\s*(.*?)(?=\n[A-Z]|$)',
        'steps': r'(?:Steps|Actions):\s*(.*?)(?=\n[A-Z]|$)',
        'risks': r'(?:Risks|Warnings):\s*(.*?)(?=\n[A-Z]|$)'
    }
    
    for key, pattern in sections.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            guidance[key] = match.group(1).strip()
    
    return guidance

def get_legal_guidance(problem, context_text=""):
    """
    Get structured legal guidance from Ollama/OpenAI.
    Prioritizes Indian legal context.
    """
    prompt = f"""You are an expert Indian legal assistant. Analyze the issue and provide a response in valid JSON.
    Structure:
    1. A concise "summary" (max 3 sentences).
    2. A comprehensive "full_analysis" (detailed documentation).
    3. Specific "risks".
    4. "steps" to take.
    5. "laws" cited.
    6. "documents" needed.
    7. "follow_ups" (list of strings).

    Issue: {problem}
    Additional Context: {context_text}

    RESPONSE MUST BE ONLY JSON."""

    return _call_ai(prompt)

def draft_legal_notice(analysis_data):
    """Generate a formal legal notice based on existing analysis."""
    prompt = f"""Based on this legal analysis, draft a professional formal Legal Notice in Indian legal format.
    Analysis: {json.dumps(analysis_data)}
    
    IMPORTANT: Write the notice as a complete, formal text document that can be printed. 
    Do NOT format the notice itself as JSON. Use standard legal document structure: 
    - Heading/Subject
    - Details of parties (placeholders)
    - Chronological facts
    - Legal demands and consequences
    - Notice period (usually 30 days)
    - Signature placeholders
    
    Return your response as a JSON object with a 'notice_text' field containing this full text."""
    
    return _call_ai(prompt)

def detect_red_flags(document_text):
    """identify potential legal traps or dangerous clauses."""
    prompt = f"""Analyze this document for 'RED FLAGS' (unfair clauses, hidden liabilities, or illegal terms) in Indian law.
    Document: {document_text[:4000]}
    
    Return JSON: {{"red_flags": ["flag 1", "flag 2"], "severity": "High/Medium/Low", "explanation": "..."}}"""
    
    return _call_ai(prompt)

def _call_ai(prompt):
    """Internal helper to route AI requests."""
    # Try OpenAI if key exists
    if OPENAI_API_KEY:
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI error: {e}")

    # Fallback to Ollama
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            raw_res = response.json().get("response", "")
            return json.loads(raw_res)
        else:
            return {"summary": "AI Engine Error", "full_analysis": f"Ollama returned status code: {response.status_code}"}
    except requests.exceptions.Timeout:
        print("Timeout connecting to Ollama")
        return {"summary": "AI Service Timeout", "full_analysis": "The local AI engine (Ollama) is taking too long to respond. Please ensure it has enough resources (RAM/GPU) or try a smaller model."}
    except requests.exceptions.ConnectionError:
        print("ConnectionError: Ollama might be offline")
        return {"summary": "AI Service Offline", "full_analysis": "Could not connect to the local AI engine at localhost:11434. Please ensure Ollama is running and accessible."}
    except Exception as e:
        print(f"AI Error: {e}")
        return {"summary": "AI Processing Failure", "full_analysis": str(e)}

    return {"summary": "Processing failed", "full_analysis": "No response from AI engine."}
