import os
from flask import Blueprint, send_file, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Clip

downloads_bp = Blueprint("downloads", __name__)

@downloads_bp.get("/clip/<int:clip_id>")
@jwt_required()
def download_clip(clip_id):
    uid = get_jwt_identity()
    clip = Clip.query.get_or_404(clip_id)
    if clip.user_id != uid:
        abort(403)
    if not os.path.exists(clip.file_path):
        abort(404)
    return send_file(clip.file_path, as_attachment=True)
