import os
import uuid
import json
import shutil
import pandas as pd
from datetime import datetime


def create_session_folder(upload_folder):
    session_id = str(uuid.uuid4())
    session_folder = os.path.join(upload_folder, session_id)
    os.makedirs(session_folder, exist_ok=True)
    return session_id, session_folder


def save_upload(file, upload_folder, filename):
    session_id, session_folder = create_session_folder(upload_folder)

    ext = filename.rsplit('.', 1)[-1].lower()
    csv_path = os.path.join(session_folder, "original.csv")
    pkl_path = os.path.join(session_folder, "working.pkl")
    log_path = os.path.join(session_folder, "ops_log.json")

    if ext == 'csv':
        file.save(csv_path)
        df = pd.read_csv(csv_path)
    elif ext in ('xlsx', 'xls'):
        tmp_path = os.path.join(session_folder, f"original.{ext}")
        file.save(tmp_path)
        df = pd.read_excel(tmp_path)
        df.to_csv(csv_path, index=False)
        os.remove(tmp_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    df.to_pickle(pkl_path)

    with open(log_path, 'w') as f:
        json.dump([], f)

    return session_id, session_folder, filename


def load_df(session_folder):
    pkl_path = os.path.join(session_folder, "working.pkl")
    if not os.path.exists(pkl_path):
        raise FileNotFoundError("Working file not found. Please re-upload.")
    return pd.read_pickle(pkl_path)


def save_df(df, session_folder):
    pkl_path = os.path.join(session_folder, "working.pkl")
    df.to_pickle(pkl_path)


def reset_df(session_folder):
    csv_path = os.path.join(session_folder, "original.csv")
    pkl_path = os.path.join(session_folder, "working.pkl")
    if not os.path.exists(csv_path):
        raise FileNotFoundError("Original file not found.")
    df = pd.read_csv(csv_path)
    df.to_pickle(pkl_path)

    log_path = os.path.join(session_folder, "ops_log.json")
    with open(log_path, 'w') as f:
        json.dump([], f)
    return df


def log_operation(session_folder, operation: dict):
    log_path = os.path.join(session_folder, "ops_log.json")
    log = []
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log = json.load(f)
    operation['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log.append(operation)
    with open(log_path, 'w') as f:
        json.dump(log, f, indent=2)


def get_ops_log(session_folder):
    log_path = os.path.join(session_folder, "ops_log.json")
    if not os.path.exists(log_path):
        return []
    with open(log_path, 'r') as f:
        return json.load(f)


def cleanup_session(session_folder):
    if os.path.exists(session_folder):
        shutil.rmtree(session_folder)


def get_file_info(session_folder, filename):
    csv_path = os.path.join(session_folder, "original.csv")
    size_bytes = os.path.getsize(csv_path)
    if size_bytes < 1024:
        size_str = f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    return filename, size_str