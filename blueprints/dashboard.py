from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from backend.file_handler import load_df, get_file_info
from backend.analyzer import get_dashboard_data

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
    session_folder = session.get('session_folder')
    filename       = session.get('filename')

    # No session — redirect to upload
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))

    # AJAX request from dashboard.js — return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            df = load_df(session_folder)
            _, file_size = get_file_info(session_folder, filename)
            data = get_dashboard_data(df, filename, file_size)
            return jsonify(data)
        except FileNotFoundError:
            return jsonify({"error": "Session expired. Please re-upload."}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Normal page load — return HTML template
    return render_template('dashboard.html')