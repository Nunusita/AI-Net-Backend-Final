import os
import subprocess
import tempfile
from moviepy.editor import VideoFileClip
from .subtitles import transcribe_audio_and_make_srt

def download_youtube_video(url: str) -> str:
    import yt_dlp
    tmp_dir = tempfile.mkdtemp()
    out_path = os.path.join(tmp_dir, "%(title)s.%(ext)s")
    ydl_opts = {
        'outtmpl': out_path,
        'format': 'mp4/bestaudio/best',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

def split_into_clips(video_path, max_clips=10, clip_length=60):
    clips = []
    with VideoFileClip(video_path) as vid:
        duration = int(vid.duration)
        start = 0
        while start < duration and len(clips) < max_clips:
            end = min(start + clip_length, duration)
            sub = vid.subclip(start, end)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            sub.write_videofile(tmp.name, codec="libx264", audio_codec="aac", verbose=False, logger=None)
            clips.append(tmp.name)
            start = end
    return clips

def burn_captions(input_video, srt_path, output_video):
    # Usa ffmpeg para quemar subtítulos
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-vf", f"subtitles='{srt_path}'",
        "-c:a", "copy",
        output_video
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_video

def add_captions_to_clip(clip_path, language="en"):
    srt_path = transcribe_audio_and_make_srt(clip_path, language)
    out_path = clip_path.replace(".mp4", "_captioned.mp4")
    burn_captions(clip_path, srt_path, out_path)
    return out_path
