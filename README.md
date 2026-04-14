# ⚖️ Legal AI Assistant

Indian legal guidance AI using Ollama LLM. Upload documents/images, get structured analysis.

## Features
- Text + file/image upload analysis
- Structured output: Summary, Risks, Steps, Laws, Documents
- Voice input
- PDF export, copy-to-clipboard
- Rule-based legal fallback
- Production-ready for Render.com

## Local Setup

1. **Python deps** (Python 3.11+):
```bash
pip install -r requirements.txt
```

2. **Ollama** (required for AI):
```bash
# Install Ollama: https://ollama.ai
ollama serve  # Run in background
ollama pull minicpm-v:latest  # Vision model (~4GB)
```

3. **Run**:
```bash
python app.py
```
Visit `http://localhost:5000`

## Test Cases
- Text: "My landlord isn't returning deposit"
- File: Upload .txt contract
- Image: Evidence photo

## Deployment: Render.com

1. Push to GitHub
2. New Web Service → Connect repo
3. **Settings**:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
   - Runtime: Python 3.12
4. **Env Vars**:
   ```
   SECRET_KEY=your-secret
   OLLAMA_URL=http://your-ollama-server:11434/api/generate
   OLLAMA_MODEL=minicpm-v:latest
   ```
5. **Note**: Ollama must run separately (VPS/Docker) as Render can't run GPU LLMs.

## Production Notes
- Uploads auto-cleaned
- 16MB file limit
- Error handling with fallbacks
- Responsive mobile-friendly

## Architecture
```
app.py (Flask) → ai_engine.py (Ollama) → Structured JSON
                     ↓
                laws.py (keyword fallback)
```

**Disclaimer**: AI-generated, not legal advice. Consult qualified lawyer.

