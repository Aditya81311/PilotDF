import os
import json
import pandas as pd
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from blueprints.utils import get_user_session
from backend.file_handler import load_df, save_df, log_operation, get_ops_log, reapply_ops
from backend import clean_data

clean_bp = Blueprint('clean', __name__, url_prefix='/api')

def session_guard():
    session_folder, filename, user_id, _ = get_user_session()
    if not session_folder:
        return None, None, jsonify({'error': 'No file uploaded'}), 404
    return session_folder, filename, None, None


@clean_bp.route('/clean/columns', methods=['GET'])
@jwt_required()
def get_columns():
    session_folder, filename, user_id, _ = get_user_session()
    if not session_folder:
        return jsonify({'error': 'No file uploaded'}), 404
    df = load_df(session_folder)
    columns = [{'name': col, 'type': str(df[col].dtype)} for col in df.columns]
    return jsonify({'columns': columns})


@clean_bp.route('/clean/null', methods=['POST'])
@jwt_required()
def clean_null():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.clean_null(df, data['column'], data['method'], data.get('custom_val', ''))
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'clean_null', 'column': data['column'], 'method': data['method'], 'custom_val': data.get('custom_val', '')})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/drop-rows', methods=['POST'])
@jwt_required()
def drop_rows():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.drop_rows(df, data['scope'], data.get('column', ''))
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'drop_rows', 'scope': data['scope'], 'column': data.get('column', '')})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/drop-column', methods=['POST'])
@jwt_required()
def drop_column():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.drop_column(df, data['column'])
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'drop_column', 'column': data['column']})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/rename-column', methods=['POST'])
@jwt_required()
def rename_column():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.rename_column(df, data['column'], data['new_name'])
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'rename_column', 'column': data['column'], 'new_name': data['new_name']})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/remove-duplicates', methods=['POST'])
@jwt_required()
def remove_duplicates():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.remove_duplicates(df, data['keep'])
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'remove_duplicates', 'keep': data['keep']})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/change-dtype', methods=['POST'])
@jwt_required()
def change_dtype():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.change_dtype(df, data['column'], data['type_'])
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'change_dtype', 'column': data['column'], 'type_': data['type_']})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/replace-val', methods=['POST'])
@jwt_required()
def replace_val():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.replace_val(df, data['column'], data['find_val'], data['replace_val'], data['exact_match'])
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'replace_val', 'column': data['column'], 'find_val': data['find_val'], 'replace_val': data['replace_val'], 'exact_match': data['exact_match']})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/trim-space', methods=['POST'])
@jwt_required()
def trim_space():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.trim_space(df, data['column'])
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'trim_space', 'column': data['column']})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/change-case', methods=['POST'])
@jwt_required()
def change_case():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.change_case(df, data['column'], data['case'])
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'change_case', 'column': data['column'], 'case': data['case']})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/reorder-columns', methods=['POST'])
@jwt_required()
def reorder_columns():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    result = clean_data.reorder_columns(df, data['new_order'])
    if result['status'] == 'success':
        save_df(result['df'], session_folder)
        log_operation(session_folder, {'action': 'reorder_columns', 'new_order': data['new_order']})
        return jsonify({'success': True})
    return jsonify({'error': result['error']}), 400


@clean_bp.route('/clean/undo', methods=['POST'])
@jwt_required()
def undo():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    log = get_ops_log(session_folder)
    if not log:
        return jsonify({'error': 'Nothing to undo'}), 400
    log.pop()
    log_path = os.path.join(session_folder, 'ops_log.json')
    with open(log_path, 'w') as f:
        json.dump(log, f, indent=2)
    df = pd.read_csv(os.path.join(session_folder, 'original.csv'))
    df = reapply_ops(df, log)
    save_df(df, session_folder)
    return jsonify({'success': True})