#!/data/data/com.termux/files/usr/bin/python
import sys
import json
from pathlib import Path

import ffmpeg
from pymediainfo import MediaInfo


def get_subtitle_streams_info(input_path: str) -> list[dict]:
    """
    Uses ffprobe via ffmpeg-python to get detailed info about subtitle streams.
    This is generally more reliable for stream mapping than pymediainfo alone.
    """
    try:
        probe_data = ffmpeg.probe(input_path, select_streams="s")
        streams_info = []
        for stream in probe_data.get("streams", []):
            print(stream)
            if stream.get("codec_type") == "subtitle":
                stream_info = {
                    "index": stream.get("index"),
                    "language": stream.get("tags", {}).get("language", "und"),
                    "title": stream.get("tags", {}).get("title"),
                    "forced": stream.get("disposition", {}).get("forced", 0) == 1,
                    "codec_name": stream.get("codec_name"),
                }
                print(stream_info)
                streams_info.append(stream_info)
        return streams_info
    except ffmpeg.Error as e:
        print(f"Error probing file: {e.stderr.decode('utf8')}")
        return []


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <video.mkv|video.mp4>")
        sys.exit(1)

    input_path_str = sys.argv[1]
    input_path = Path(input_path_str)

    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    basename = input_path.with_suffix("")

    # Get subtitle stream information using ffprobe via ffmpeg-python
    subtitle_streams = get_subtitle_streams_info(input_path_str)
    print(subtitle_streams)

    if not subtitle_streams:
        print("No subtitle streams found.")
        sys.exit(0)

    print(f"Found {len(subtitle_streams)} subtitle streams.")
    try:
        extracted_files = []
        for i, stream_info in enumerate(subtitle_streams):
            index = stream_info["index"]
            lang = stream_info["language"]
            title = stream_info["title"]
            forced = stream_info["forced"]
            codec_name = stream_info["codec_name"]

            filename_parts = [str(basename)]
            filename_parts.append(f"sub{index}")  # Use the actual stream index for clarity
            if lang != "und":
                filename_parts.append(lang)
            if title:
                # Sanitize title for filename
                safe_title = "".join(c if c.isalnum() else "_" for c in title)
                filename_parts.append(safe_title)
            if forced:
                filename_parts.append("forced")

            out_filename = ".".join(filename_parts) + ".srt"
            out_path = Path(out_filename)
            extracted_files.append(str(out_path))
    except:
        pass
        print(f"Extracting stream index {index} (Lang: {lang}, Forced: {forced}, Codec: {codec_name}) -> {out_path}")


"""

        try:
            # Map using the stream index from probe, and ensure output is SRT
            process = (
                ffmpeg.input(input_path_str, **{"loglevel": "quiet"})  # Suppress ffmpeg verbose output
                .output(
                    str(out_path), map=f"0:s:{index}", c="srt", **{"force_key_frames": None}
                )  # c='srt' for conversion
                .overwrite_output()
            )
            process.run()
            print(f"Successfully extracted: {out_path}")
        except ffmpeg.Error as e:
            print(f"Error extracting stream index {index}: {e.stderr.decode('utf8')}")
        except Exception as e:
            print(f"An unexpected error occurred during extraction of stream index {index}: {e}")

    if extracted_files:
        print("\n--- Extraction Complete ---")
        print("Extracted subtitle files:")
        for f_path in extracted_files:
            # The sandbox path is for the tool's internal file system
            print(f"- {f_path}")
            # To make it downloadable, you'd typically need a mechanism to serve these files.
            # For demonstration, let's print a path that a system might use.
            # If this were a web service, you'd generate a download link.
            # Here, we'll use a convention similar to how some systems link files.
    #            print(f"  Downloadable link (example): [/mnt/data/{Path(f_path](https://storage.gapgpt.app/media/code_interpreter/ba384828-490a-47a2-b5d9-b3dd4931e301/%7BPath%28f_path)).name}") # Assuming files are saved in /mnt/data
#    else:
#        print("\nNo subtitle files were successfully extracted.")


"""


if __name__ == "__main__":
    main()
