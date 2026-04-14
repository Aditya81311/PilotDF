import os
import json
import pandas as pd
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from blueprints.utils import get_user_session
from backend.file_handler import load_df, save_df, log_operation, get_ops_log, reapply_ops
from backend import transform_data

transform_bp = Blueprint('transform', __name__, url_prefix='/api')


@transform_bp.route('/transform/columns', methods=['GET'])
@jwt_required()
def get_columns():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    df = load_df(session_folder)
    return jsonify({'columns': [{'name': col, 'type': str(df[col].dtype)} for col in df.columns]})


@transform_bp.route('/transform/new-column', methods=['POST'])
@jwt_required()
def new_column():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    df = transform_data.new_column(df, data['name'], data['formula'])
    save_df(df, session_folder)
    log_operation(session_folder, {'action': 'new_column', 'new_col_name': data['name'], 'formula': data['formula']})
    return jsonify({'success': True})


@transform_bp.route('/transform/normalize', methods=['POST'])
@jwt_required()
def normalize():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    df = transform_data.normalize(df, data['column'], data['method'])
    save_df(df, session_folder)
    log_operation(session_folder, {'action': 'normalize', 'column': data['column'], 'method': data['method']})
    return jsonify({'success': True})


@transform_bp.route('/transform/encode', methods=['POST'])
@jwt_required()
def encode():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    df = transform_data.encode(df, data['column'], data['method'], data['drop_first'])
    save_df(df, session_folder)
    log_operation(session_folder, {'action': 'encode', 'column': data['column'], 'method': data['method'], 'drop_first': data['drop_first']})
    return jsonify({'success': True})


@transform_bp.route('/transform/bin', methods=['POST'])
@jwt_required()
def bin_numeric():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    df = transform_data.bin_numaric(df, data['column'], data['bins'], data['labels'])
    save_df(df, session_folder)
    log_operation(session_folder, {'action': 'bin_numaric', 'column': data['column'], 'bins': data['bins'], 'labels': data['labels']})
    return jsonify({'success': True})


@transform_bp.route('/transform/extract-datetime', methods=['POST'])
@jwt_required()
def extract_datetime():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    df = transform_data.extract_datetime(df, data['column'], data['extract'])
    save_df(df, session_folder)
    log_operation(session_folder, {'action': 'extract_datetime', 'column': data['column'], 'extract': data['extract']})
    return jsonify({'success': True})


@transform_bp.route('/transform/maths', methods=['POST'])
@jwt_required()
def maths():
    session_folder, _, __, ___ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    data = request.get_json()
    df = load_df(session_folder)
    df = transform_data.apply_maths(df, data['column'], data['operation'])
    save_df(df, session_folder)
    log_operation(session_folder, {'action': 'apply_math', 'column': data['column'], 'operation': data['operation']})
    return jsonify({'success': True})


@transform_bp.route('/transform/undo', methods=['POST'])
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