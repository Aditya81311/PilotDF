import os
import json
from flask import Blueprint, request, jsonify, current_app, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from backend.file_handler import save_upload, load_df, reset_df

upload_bp = Blueprint('upload', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    user_id = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV and Excel files are supported'}), 400

    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], user_id)
    os.makedirs(upload_folder, exist_ok=True)

    try:
        session_id, session_folder, filename = save_upload(file, upload_folder, filename)

        # Save meta.json for this user
        meta_path = os.path.join(upload_folder, 'meta.json')
        with open(meta_path, 'w') as f:
            json.dump({'session_folder': session_folder, 'filename': filename}, f)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@upload_bp.route('/reset', methods=['POST'])
@jwt_required()
def reset():
    from blueprints.utils import get_user_session
    session_folder, filename, user_id, _ = get_user_session()
    if not session_folder:
        return jsonify({'error': 'No active session'}), 404
    try:
        reset_df(session_folder)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@upload_bp.route('/download/csv', methods=['GET'])
@jwt_required()
def download_csv():
    from blueprints.utils import get_user_session
    session_folder, filename, user_id, _ = get_user_session()
    if not session_folder:
        return jsonify({'error': 'No active session'}), 404
    try:
        df = load_df(session_folder)
        csv_data = df.to_csv(index=False)
        safe_name = filename.replace('.xlsx', '.csv').replace('.xls', '.csv')
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=cleaned_{safe_name}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500