import os
import PyPDF2
from docx import Document
from werkzeug.utils import secure_filename

def extract_text_from_pdf(filepath):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return f"Error reading PDF: {str(e)}"
    return text

def extract_text_from_docx(filepath):
    """Extract text from a .docx file."""
    text = ""
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return f"Error reading DOCX: {str(e)}"
    return text

def get_file_content(filepath):
    """Check extension and extract text accordingly."""
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(filepath)
    elif ext in ['docx', 'doc']: # Note: python-docx only supports .docx
        return extract_text_from_docx(filepath)
    elif ext == 'txt':
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return "Error reading text file."
    return "Unsupported file format for text extraction."

def cleanup_file(filepath):
    """Safely delete a file if it exists."""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass
