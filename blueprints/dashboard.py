import os
import json
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from blueprints.utils import get_user_session
from backend.file_handler import load_df, get_file_info
from backend.analyzer import get_dashboard_data

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    session_folder, filename, user_id, _ = get_user_session()
    if not session_folder:
        return jsonify({'error': 'No file uploaded'}), 404
    try:
        df = load_df(session_folder)
        _, file_size = get_file_info(session_folder, filename)
        data = get_dashboard_data(df, filename, file_size)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'Session expired. Please re-upload.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500