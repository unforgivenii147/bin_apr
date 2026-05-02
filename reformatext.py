#!/data/data/com.termux/files/usr/bin/python
import re
import sys
from pathlib import Path


def restructure_text_file(filepath: Path):
    """
    Restructures a text file according to specified rules:
    - Preserves paragraph structure.
    - Each sentence on a new line.
    - Breaks long sentences (>120 chars) at commas, respecting word boundaries.
    - Creates a .bak backup file.
    """
    if not filepath.is_file():
        print(f"Error: File not found at {filepath}")
        return
    try:
        with filepath.open("r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return
    # Create backup
    bak_filepath = filepath.with_suffix(filepath.suffix + ".bak")
    try:
        with filepath.open("r", encoding="utf-8") as src, bak_filepath.open("w", encoding="utf-8") as dst:
            dst.write(src.read())
        print(f"Backup created at: {bak_filepath}")
    except Exception as e:
        print(f"Error creating backup file {bak_filepath}: {e}")
        return
    restructured_lines = []
    paragraphs = content.split("\n\n")  # Split into paragraphs first
    for paragraph in paragraphs:
        if not paragraph.strip():
            restructured_lines.append("")  # Preserve empty lines between paragraphs
            continue
        # Split paragraph into sentences. This regex tries to be smart about abbreviations (e.g., Mr., Dr.)
        # but might not be perfect for all cases. It splits on ., !, ? followed by whitespace or end of string.
        sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+", paragraph)
        for sentence in sentences:
            if not sentence.strip():
                continue
            processed_sentence_parts = []
            current_line_length = 0
            words = sentence.split()
            current_line_words = []
            for word in words:
                # Check if adding the next word exceeds the line length (120 chars)
                # Also consider the space between words
                potential_line_length = current_line_length + len(word) + (1 if current_line_words else 0)
                if (
                    potential_line_length > 120 and current_line_length > 0
                ):  # If exceeding and we have content on the current line
                    # Try to break at the last comma found in current_line_words
                    break_point = -1
                    for i, w in enumerate(current_line_words):
                        if w.endswith(","):
                            break_point = i
                    if break_point != -1:
                        # Break at the comma
                        processed_sentence_parts.append(" ".join(current_line_words[: break_point + 1]))
                        current_line_words = current_line_words[break_point + 1 :]
                        current_line_length = len(" ".join(current_line_words))
                    else:
                        # No comma found, commit the line as is
                        processed_sentence_parts.append(" ".join(current_line_words))
                        current_line_words = [word]
                        current_line_length = len(word)
                else:
                    # Add word to current line
                    current_line_words.append(word)
                    current_line_length = potential_line_length
            # Add any remaining words for the current line
            if current_line_words:
                processed_sentence_parts.append(" ".join(current_line_words))
            # Add all parts of the sentence (potentially broken) to the main list
            restructured_lines.extend(processed_sentence_parts)
    # Write back to the original file
    try:
        with filepath.open("w", encoding="utf-8") as f:
            f.write("\n".join(restructured_lines))
        print(f"File successfully restructured: {filepath}")
    except Exception as e:
        print(f"Error writing to file {filepath}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    file_path = Path(filename)
    restructure_text_file(file_path)
