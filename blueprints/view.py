from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from blueprints.utils import get_user_session
from backend.file_handler import load_df
from backend.view_data import get_data

view_bp = Blueprint('view', __name__, url_prefix='/api')

@view_bp.route('/view', methods=['GET'])
@jwt_required()
def view():
    session_folder, filename, user_id, _ = get_user_session()
    if not session_folder:
        return jsonify({'error': 'No file uploaded'}), 404
    try:
        page = int(request.args.get('page', 1))
        rows = int(request.args.get('rows', 25))
        df = load_df(session_folder)
        data = get_data(df, rows, page)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'Session expired. Please re-upload.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500