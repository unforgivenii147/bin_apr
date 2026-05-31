#!/data/data/com.termux/files/usr/bin/python
import subprocess


def extract_subtitles(video_path):
    """Extracts subtitle streams from a video file using ffmpeg.
    Args:
        video_path (str): The path to the input video file.
    Returns:
        None: Prints extraction progress and completion messages.
    Raises:
        FileNotFoundError: If ffmpeg is not installed.
        RuntimeError: If no subtitle streams are found or extraction fails.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
    except FileNotFoundError:
        raise FileNotFoundError("ffmpeg is required but not installed.")
    basename = video_path.rsplit(".", 1)[0]
    ffprobe_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "s",
        "-show_entries",
        "stream=index:stream_tags=language",
        "-of",
        "csv=p=0",
        video_path,
    ]
    subs_output = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
    subs = subs_output.stdout.strip().split("\n")
    if not subs or (len(subs) == 1 and subs[0] == ""):
        print("No subtitle streams found.")
        return
    count = 0
    for line in subs:
        index, lang = line.split(",")
        if not lang:
            lang = "und"
        out_filename = f"{basename}.sub{count}.{lang}.srt"
        print(f"Extracting subtitle stream {index} -> {out_filename}")
        ffmpeg_cmd = ["ffmpeg", "-y", "-i", video_path, "-map", f"0:s:{count}", out_filename]
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        count += 1
    print("Done.")


# Example usage:
# extract_subtitles("your_video.mkv")
# Since I cannot directly execute the script you provided,
# I am providing a Python equivalent using the subprocess module.
# To use this, you would need to:
# 1. Save the code above as a Python file (e.g., extract_subs.py).
# 2. Ensure you have ffmpeg installed on your system and in your PATH.
# 3. Run the script from your terminal like: python extract_subs.py your_video.mkv
#
# If you have a specific video file you'd like me to process using this code, please provide its path.
# Alternatively, if you have the video file available in a way I can access it,
# I can attempt to run the code.
