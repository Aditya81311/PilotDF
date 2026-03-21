from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from backend.file_handler import load_df, get_file_info
from backend import visualize_data
import os
import json
import pandas as pd
visualize_bp = Blueprint('visualize',__name__)

@visualize_bp.route("/visualize")
def visualize():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    df = load_df(session_folder)
    columns = [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
    return render_template("visualize.html",columns = columns)

@visualize_bp.route("/visualize-generate",methods = ["GET","POST"])
def generate():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.method == "POST":
        orientation = request.form.get("orientation")
        color_by = request.form.get("color_by")
        options = {
            "chart_type": request.form.get("chart_type"),
            "x":          request.form.get("x"),
            "y":          request.form.get("y"),
            "title":      request.form.get("title"),
            "color_by":   color_by if color_by else None,
            "bins":       int(request.form.get("bins",10)),
             "orientation": "h" if orientation == "horizontal" else "v"
            }
        df = load_df(session_folder)
        chart_html = visualize_data.generate_chart(df,options)
        return jsonify({"success": True, "chart": chart_html})
    return render_template("transform.html")

