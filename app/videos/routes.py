import os
import tempfile
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User, Clip, Style
from ..utils.usage import can_process_link, log_usage
from .processor import split_into_clips, add_captions_to_clip, download_youtube_video

videos_bp = Blueprint("videos", __name__)

@videos_bp.post("/process")
@jwt_required()
def process_video():
    uid = get_jwt_identity()
    user = User.query.get_or_404(uid)

    # Free plan limits
    ok, msg = can_process_link(user)
    if not ok:
        return {"error": msg}, 403

    max_clips = current_app.config.get("FREE_CLIPS_PER_LINK", 10)
    if user.plan.value != "free":
        max_clips = 9999  # unlimited, customize

    video_path = None
    youtube_url = request.json.get("youtube_url") if request.is_json else None

    if "file" in request.files:
        f = request.files["file"]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        f.save(tmp.name)
        video_path = tmp.name
    elif youtube_url:
        try:
            video_path = download_youtube_video(youtube_url)
        except Exception as e:
            return {"error": f"youtube download failed: {e}"}, 500
    else:
        return {"error": "Provide a file or youtube_url"}, 400

    raw_clips = split_into_clips(video_path, max_clips=max_clips)
    created = []
    for path in raw_clips:
        captioned_path = add_captions_to_clip(path)
        clip = Clip(user_id=user.id, source_url=youtube_url, file_path=captioned_path)
        db.session.add(clip)
        db.session.flush()  # to get clip.id
        created.append({"id": clip.id, "file_path": captioned_path})
    db.session.commit()

    log_usage(user.id, links=1, clips=len(created))
    return {"clips": created}
