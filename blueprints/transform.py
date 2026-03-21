from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from backend.file_handler import load_df, get_file_info , save_df , log_operation , reapply_ops
from backend import transform_data
import os
import json
import pandas as pd
from backend.file_handler import get_ops_log, save_df
transform_bp = Blueprint('transform',__name__)


@transform_bp.route("/transform")
def transform():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    df = load_df(session_folder)
    columns = [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
    return render_template("transform.html",columns = columns)


@transform_bp.route("/transform-new_column",methods = ["GET","POST"])
def transform_new_column():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            name = request.form["name"]
            formula = request.form["formula"]
            print(formula)
            print(name)
            df = load_df(session_folder)
            df = transform_data.new_column(df,name,formula)
            save_df(df,session_folder)
            log_operation(session_folder,{"action": "new_column",
             "new_col_name": name, 
             "formula": formula})
            return jsonify({"success": True})
    return render_template("transform.html")

@transform_bp.route("/transform-normalize",methods = ["GET","POST"])
def transform_normalize():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            column = request.form["column"]
            method = request.form["method"]
            df = load_df(session_folder)
            df = transform_data.normalize(df,column,method)
            save_df(df,session_folder)
            log_operation(session_folder,{"action": "normalize", 
            "column": column, 
            "method": method})
            return jsonify({"success": True})
    return render_template("transform.html")

@transform_bp.route("/transform-encode",methods = ["GET","POST"])
def transform_encode():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            column = request.form["column"]
            method = request.form["method"]
            drop_first = request.form["drop_first"]
            df = load_df(session_folder)
            df = transform_data.encode(df,column,method,drop_first)
            save_df(df,session_folder)
            log_operation(session_folder,{"action": "encode", 
            "column": column, 
            "method": method, 
            "drop_first": drop_first})
            return jsonify({"success": True})
    return render_template("transform.html")

@transform_bp.route("/transform-bin",methods = ["GET","POST"])
def transform_bin():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            column = request.form["column"]
            bins = request.form["bins"]
            labels = request.form["labels"]
            df = load_df(session_folder)
            df = transform_data.bin_numaric(df,column,bins,labels)
            save_df(df,session_folder)
            log_operation(session_folder,{"action": "bin_numaric", 
            "column": column, 
            "bins": bins,
            "labels": labels})
            return jsonify({"success": True})
    return render_template("transform.html")

@transform_bp.route("/transform-extract",methods = ["GET","POST"])
def transform_extract():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            column = request.form["column"]
            extract = request.form["extract"]
            df = load_df(session_folder)
            df = transform_data.extract_datetime(df,column,extract)
            save_df(df,session_folder)
            log_operation(session_folder,{"action": "extract_datetime",
            "column": column, 
            "extract": extract})
            return jsonify({"success": True})
    return render_template("transform.html")

@transform_bp.route("/transform-maths",methods = ["GET","POST"])
def transform_maths():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            column = request.form["column"]
            operation = request.form["operation"]
            df = load_df(session_folder)
            df = transform_data.apply_maths(df,column,operation)
            save_df(df,session_folder)
            log_operation(session_folder,{"action": "apply_math", 
            "column": column, 
            "operation": operation})
            return jsonify({"success": True})
    return render_template("transform.html")

@transform_bp.route("/transform-undo", methods=["POST"])
def transform_undo():
    session_folder = session.get('session_folder')
    if not session_folder:
        return jsonify({"error": "Session expired"}), 404
    
    log = get_ops_log(session_folder)
    
    if not log:
        return jsonify({"error": "Nothing to undo"}), 400
    
    # Remove last operation
    log.pop()
    
    # Save updated log
    log_path = os.path.join(session_folder, "ops_log.json")
    with open(log_path, 'w') as f:
        json.dump(log, f, indent=2)
        
    # Reload original and re-apply remaining ops
    df = pd.read_csv(os.path.join(session_folder, "original.csv"))
    df = reapply_ops(df, log)
    save_df(df, session_folder)
    
    return jsonify({"success": True})