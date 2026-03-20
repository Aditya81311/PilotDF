from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from backend.file_handler import load_df, get_file_info
from backend.view_data import get_data

view_bp = Blueprint('view',__name__)

@view_bp.route("/view",methods = ["GET","POST"])
def view():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            if request.method == "POST":
                page     = int(request.form.get("page", 1))
                rows     = int(request.form.get("rows", 25))
            else:
                page     = int(request.args.get("page", 1))
                rows     = int(request.args.get("rows", 25))
                              
            df = load_df(session_folder)
            data = get_data(df,rows,page)
            return jsonify(data)
        except FileNotFoundError:
            return jsonify({"error": "Session expired. Please re-upload."}), 404
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500
    return render_template("view_data.html")