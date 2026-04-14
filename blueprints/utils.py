import os
import json
from flask_jwt_extended import get_jwt_identity

def get_user_session():
    user_id = get_jwt_identity()
    user_folder = os.path.join('uploads', user_id)
    meta_path = os.path.join(user_folder, 'meta.json')
    if not os.path.exists(meta_path):
        return None, None, None, user_id
    with open(meta_path) as f:
        meta = json.load(f)
    return meta['session_folder'], meta['filename'], user_id, user_folder