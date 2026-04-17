from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config import *
from models import db, User, Chat, Document
from ai_engine import get_legal_guidance, draft_legal_notice, detect_red_flags
import os
import json
from werkzeug.utils import secure_filename
from utils import get_file_content, cleanup_file

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

db.init_app(app)

@app.template_filter('from_json')
def from_json_filter(s):
    try:
        return json.loads(s)
    except:
        return {}

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

@lm.user_loader
def load_user(user_id):
    # Fixed SQLAlchemy 2.0 deprecation: session.get() instead of User.query.get()
    return db.session.get(User, int(user_id))

def init_db():
    with app.app_context():
        db.create_all()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    chat_count = Chat.query.filter_by(user_id=current_user.id).count()
    doc_count = Document.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html', user=current_user, chat_count=chat_count, doc_count=doc_count)

@app.route('/history')
@login_required
def history():
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.timestamp.desc()).all()
    return render_template('history.html', chats=chats)

@app.route('/documents')
@login_required
def documents():
    docs = Document.query.filter_by(user_id=current_user.id).all()
    return render_template('documents.html', documents=docs)

@app.route('/result', methods=['POST'])
def result():
    problem = request.form.get('problem', '').strip()
    file_obj = request.files.get('file')
    
    file_text = ""
    filename = ""
    
    if file_obj and file_obj.filename != '':
        filename = secure_filename(file_obj.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_obj.save(filepath)
        file_text = get_file_content(filepath)
        
        # If user is logged in, save the document
        if current_user.is_authenticated:
            # Check for red flags if it's a document
            flags_data = detect_red_flags(file_text)
            doc = Document(
                user_id=current_user.id,
                filename=filename,
                content_summary=file_text[:500] + "...",
                red_flags=json.dumps(flags_data),
                file_path=filepath
            )
            db.session.add(doc)
            db.session.commit()
        else:
            cleanup_file(filepath)

    if not problem and not file_text:
        flash("Please provide a legal problem or upload a document.", "warning")
        return redirect(url_for('home'))

    # Get AI Guidance
    try:
        guidance = get_legal_guidance(problem, file_text)
    except Exception as e:
        app.logger.error(f"AI Guidance error: {e}")
        guidance = {"summary": "Service Temporarily Unavailable", "full_analysis": "Error communicating with AI engine."}
    
    # Save to chat history if logged in
    if current_user.is_authenticated:
        chat = Chat(
            user_id=current_user.id,
            user_query=problem or f"Uploaded: {filename}",
            response_json=json.dumps(guidance)
        )
        db.session.add(chat)
        db.session.commit()

    return render_template("result.html", 
                         problem=problem, 
                         filename=filename,
                         guidance=guidance)

@app.route('/draft_notice', methods=['GET', 'POST'])
@login_required
def draft_notice():
    try:
        data = request.get_json()
        analysis = data.get('analysis')
        if not analysis:
            return jsonify({"error": "No analysis data provided"}), 400
        
        notice_data = draft_legal_notice(analysis)
        return jsonify(notice_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template("index.html"), 404

if __name__ == "__main__":
    init_db()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)


