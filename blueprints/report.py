from flask import Blueprint, session, redirect, url_for, render_template, Response
from backend.file_handler import load_df, get_file_info, get_ops_log
from backend.report_data import get_report_data, generate_report_html

report_bp = Blueprint('report', __name__)


def get_report_html(session_folder, filename):
    df           = load_df(session_folder)
    _, file_size = get_file_info(session_folder, filename)
    ops_log      = get_ops_log(session_folder)
    data         = get_report_data(df, filename, file_size, ops_log)
    return generate_report_html(data), filename


@report_bp.route("/report")
def report():
    session_folder = session.get('session_folder')
    filename       = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    try:
        html, _ = get_report_html(session_folder, filename)
        return render_template('report.html', report_html=html)
    except Exception as e:
        print(e)
        return redirect(url_for('dashboard.dashboard'))


@report_bp.route("/report/download/html")
def download_html():
    session_folder = session.get('session_folder')
    filename       = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    try:
        html, fname = get_report_html(session_folder, filename)
        safe_name   = fname.replace(' ', '_').replace('.csv', '').replace('.xlsx', '')
        return Response(
            html,
            mimetype='text/html',
            headers={'Content-Disposition': f'attachment; filename=report_{safe_name}.html'}
        )
    except Exception as e:
        print(e)
        return redirect(url_for('report.report'))


@report_bp.route("/report/download/pdf")
def download_pdf():
    session_folder = session.get('session_folder')
    filename       = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    try:
        from weasyprint import HTML
        html, fname = get_report_html(session_folder, filename)
        safe_name   = fname.replace(' ', '_').replace('.csv', '').replace('.xlsx', '')
        pdf         = HTML(string=html).write_pdf()
        return Response(
            pdf,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=report_{safe_name}.pdf'}
        )
    except Exception as e:
        print(e)
        return redirect(url_for('report.report'))