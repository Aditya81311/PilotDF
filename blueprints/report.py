from flask import Blueprint, jsonify, Response
from flask_jwt_extended import jwt_required
from blueprints.utils import get_user_session
from backend.file_handler import load_df, get_file_info, get_ops_log
from backend.report_data import get_report_data, generate_report_html

report_bp = Blueprint('report', __name__, url_prefix='/api')

def build_report(session_folder, filename):
    df = load_df(session_folder)
    _, file_size = get_file_info(session_folder, filename)
    ops_log = get_ops_log(session_folder)
    data = get_report_data(df, filename, file_size, ops_log)
    return generate_report_html(data), filename


@report_bp.route('/report', methods=['GET'])
@jwt_required()
def report():
    session_folder, filename, _, __ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    try:
        html, _ = build_report(session_folder, filename)
        return jsonify({'html': html})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@report_bp.route('/report/download/html', methods=['GET'])
@jwt_required()
def download_html():
    session_folder, filename, _, __ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    try:
        html, fname = build_report(session_folder, filename)
        safe_name = fname.replace(' ', '_').replace('.csv', '').replace('.xlsx', '')
        return Response(html, mimetype='text/html',
            headers={'Content-Disposition': f'attachment; filename=report_{safe_name}.html'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@report_bp.route('/report/download/pdf', methods=['GET'])
@jwt_required()
def download_pdf():
    session_folder, filename, _, __ = get_user_session()
    if not session_folder: return jsonify({'error': 'No file uploaded'}), 404
    try:
        from weasyprint import HTML
        html, fname = build_report(session_folder, filename)
        safe_name = fname.replace(' ', '_').replace('.csv', '').replace('.xlsx', '')
        pdf = HTML(string=html).write_pdf()
        return Response(pdf, mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=report_{safe_name}.pdf'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500