import os
import tempfile
import whisper

def transcribe_audio_and_make_srt(video_path, language="en"):
    model = whisper.load_model("base")
    result = model.transcribe(video_path, language=language)
    # Build SRT
    srt_lines = []
    for i, seg in enumerate(result["segments"], start=1):
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].strip()
        srt_lines.append(f"{i}\n{format_time(start)} --> {format_time(end)}\n{text}\n")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".srt")
    with open(tmp.name, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    return tmp.name

def format_time(t):
    hours = int(t // 3600)
    minutes = int((t % 3600) // 60)
    seconds = int(t % 60)
    milliseconds = int((t - int(t)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
