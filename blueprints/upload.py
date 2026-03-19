from flask import Blueprint, request, redirect, url_for, session, jsonify, current_app
from werkzeug.utils import secure_filename
from backend.file_handler import save_upload

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/', methods=['GET'])
def index():
    from flask import render_template
    return render_template('index.html')


@upload_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only CSV and Excel files are supported"}), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']

    try:
        session_id, session_folder, filename = save_upload(file, upload_folder, filename)
        session['session_id']     = session_id
        session['session_folder'] = session_folder
        session['filename']       = filename
        return jsonify({"success": True, "redirect": url_for('dashboard.dashboard')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@upload_bp.route('/reset', methods=['GET'])
def reset():
    session_folder = session.get('session_folder')
    if not session_folder:
        return redirect(url_for('upload.index'))
    try:
        from backend.file_handler import reset_df
        reset_df(session_folder)
    except Exception:
        pass
    return redirect(url_for('dashboard.dashboard'))