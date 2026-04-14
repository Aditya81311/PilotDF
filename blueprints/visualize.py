from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from blueprints.utils import get_user_session
from backend.file_handler import load_df
from backend import visualize_data

visualize_bp = Blueprint('visualize', __name__, url_prefix='/api')

@visualize_bp.route('/visualize/columns', methods=['GET'])
@jwt_required()
def get_columns():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    df = load_df(session_folder)
    return jsonify({'columns': [{'name': col, 'type': str(df[col].dtype)} for col in df.columns]})


@visualize_bp.route('/visualize/generate', methods=['POST'])
@jwt_required()
def generate():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    orientation = data.get('orientation', 'vertical')
    options = {
        'chart_type': data.get('chart_type'),
        'x':          data.get('x'),
        'y':          data.get('y'),
        'title':      data.get('title'),
        'color_by':   data.get('color_by') or None,
        'bins':       int(data.get('bins', 10)),
        'orientation': 'h' if orientation == 'horizontal' else 'v'
    }
    df = load_df(session_folder)
    chart_html = visualize_data.generate_chart(df, options)
    return jsonify({'success': True, 'chart': chart_html})