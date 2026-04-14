from flask import Flask, render_template, request, jsonify
from ai_engine import get_legal_guidance
from laws import suggest_law
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')

# Config
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_file(filepath):
    try:
        os.remove(filepath)
    except OSError:
        pass

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/documents')
def documents():
    return '<h1>Documents (Coming soon)</h1><p><a href="/">Back to Home</a></p>', 200

@app.route('/history')
def history():
    return '<h1>History (Coming soon)</h1><p><a href="/">Back to Home</a></p>', 200

@app.route('/result', methods=['POST'])
def result():
    try:
        problem = request.form.get('problem', '').strip()
        file_obj = request.files.get('file')
        image = request.files.get('image')

        file_text = ''
        uploaded_files = []

        # Handle document file
        if file_obj and file_obj.filename != '':
            if allowed_file(file_obj.filename):
                filename = secure_filename(file_obj.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_obj.save(filepath)
                uploaded_files.append(filepath)
                
                # Extract text from .txt files (PDF support can be added later with PyPDF2)
                if filename.lower().endswith('.txt'):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            file_text = f.read()
                    except Exception:
                        file_text = 'Could not read file content.'

        # Handle image for vision model
        image_path = None
        if image and image.filename != '':
            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                uploaded_files.append(image_path)

        combined_input = (problem + '\n\n' + file_text).strip()

        if not combined_input:
            guidance = {
                "summary": "No input provided.",
                "risks": "",
                "steps": "Enter your legal problem or upload a document.",
                "laws": "",
                "documents": ""
            }
        else:
            guidance = get_legal_guidance(combined_input, image_path)

            # Fallback if AI returns error string or not dict
            if isinstance(guidance, str) or not hasattr(guidance, 'get'):
                law_suggestion = suggest_law(combined_input)
                guidance = {
                    "summary": f"Quick legal match: {law_suggestion['type']}",
                    "risks": "This is basic keyword matching. AI temporarily unavailable.",
                    "steps": law_suggestion['action'],
                    "laws": law_suggestion['section'],
                    "documents": f"Contact: {law_suggestion['authority']}"
                }

        # Cleanup temporary files
        for fp in uploaded_files:
            cleanup_file(fp)

        return render_template("result.html", problem=combined_input, guidance=guidance)

    except Exception as e:
        # Cleanup on error
        if 'uploaded_files' in locals():
            for fp in uploaded_files:
                cleanup_file(fp)
        return render_template("result.html", 
                             problem='', 
                             guidance={
                                 "summary": "Processing error occurred.",
                                 "risks": str(e),
                                 "steps": "Please try again.",
                                 "laws": "",
                                 "documents": ""
                             }), 500

@app.errorhandler(404)
def not_found(error):
    return render_template("index.html"), 404

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)

