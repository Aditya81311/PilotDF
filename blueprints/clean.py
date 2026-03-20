from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from backend.file_handler import load_df, get_file_info , save_df , log_operation , reapply_ops
from backend import clean_data
import os
import json
import pandas as pd
from backend.file_handler import get_ops_log, save_df
clean_bp = Blueprint('clean',__name__)

@clean_bp.route("/clean")
def clean():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    df = load_df(session_folder)
    columns = [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
    return render_template('clean.html',columns = columns)

@clean_bp.route("/clean-clean_null",methods = ["GET","POST"])
def clean_null():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            column =request.form["column"]
            method = request.form["method"]
            custom_val = request.form["custom_val"] 
            df = clean_data.clean_null(df,column,method,custom_val)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "clean_null",
                "column": column,
                "method": method,
                "custom_val": custom_val
            })
            return jsonify({"success": True})
    return render_template('clean.html')

@clean_bp.route("/clean-drop_rows",methods = ["GET","POST"])
def drop_rows():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            scope = request.form["scope"]
            column =request.form["column"]
            df = clean_data.drop_rows(df,scope,column)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "drop_rows",
                "scope": scope,
                "column": column
            })
            return jsonify({"success": True})
    return render_template('clean.html')

@clean_bp.route("/clean-drop_column",methods = ["GET","POST"])
def drop_column():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            column =request.form["column"]
            df = clean_data.drop_column(df,column)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "drop_column",
                "column": column
            })
            return jsonify({"success": True})
    return render_template('clean.html')

@clean_bp.route("/clean-rename_column",methods = ["GET","POST"])
def rename_column():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            column =request.form["column"]
            new_name =request.form["new_name"]
            df = clean_data.rename_column(df,column,new_name)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "rename_column",
                "column": column
            })
            return jsonify({"success": True})
    return render_template('clean.html')

@clean_bp.route("/clean-remove_duplicates",methods = ["GET","POST"])
def remove_duplicates():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            keep =request.form["keep"]
            df = clean_data.remove_duplicates(df,keep)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "remove_duplicates",
                "keep": keep
            })
            return jsonify({"success": True})
    return render_template('clean.html')

@clean_bp.route("/clean-change_dtype",methods = ["GET","POST"])
def change_dtype():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            column =request.form["column"]
            type_ =request.form["type_"]
            df = clean_data.change_dtype(df,column,type_)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "change_dtype",
                "column": column,
                "type_":type_
            })
            return jsonify({"success": True})
    return render_template('clean.html')

@clean_bp.route("/clean-replace_val",methods = ["GET","POST"])
def replace_val():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            column =request.form["column"]
            find_val =request.form["find_val"]
            replace_val = request.form["replace_val"] 
            exact_match = request.form["exact_match"]
            df = clean_data.replace_val(df,column, find_val, replace_val, exact_match)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "replace_val",
                "column": column,
                "find_val":find_val,
                "replace_val":replace_val,
                "exact_match":exact_match
            })
            return jsonify({"success": True})
    return render_template('clean.html')

@clean_bp.route("/clean-trim_space",methods = ["GET","POST"])
def trim_space():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            column =request.form["column"]
            df = clean_data.trim_space(df,column)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "trim_space",
                "column": column
            })
            return jsonify({"success": True})
    return render_template('clean.html')

@clean_bp.route("/clean-change_case",methods = ["GET","POST"])
def change_case():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            column =request.form["column"]
            case =request.form["case"]
            df = clean_data.change_case(df,column,case)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "change_case",
                "column": column,
                "case":case
            })
            return jsonify({"success": True})
    return render_template('clean.html')

@clean_bp.route("/clean-reorder_columns",methods = ["GET","POST"])
def reorder_columns():
    session_folder = session.get('session_folder')
    filename = session.get('filename')
    if not session_folder or not filename:
        return redirect(url_for('upload.index'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            df =load_df(session_folder)
            new_order =request.form["new_order"]
            df = clean_data.reorder_columns(df,new_order)
            save_df(df,session_folder)
            log_operation(session_folder, {
                "action": "reorder_columns",
                "new_order": new_order
            })
            return jsonify({"success": True})
    return render_template('clean.html')
@clean_bp.route("/clean-undo", methods=["POST"])
def undo():
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