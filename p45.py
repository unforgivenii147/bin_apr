#!/data/data/com.termux/files/usr/bin/python
import ast
import os
import sys
import textwrap
from pathlib import Path

from dh import DOC_TH1, DOC_TH2
from loguru import logger


def format_python_file(filepath):
    """
    Formats a Python file to wrap commented lines and docstrings to a maximum of 35 characters.
        filepath (str): The path to the Python file.
    """
    if not Path(filepath).exists():
        logger.info(f"Error: File not found at {filepath}", file=sys.stderr)
        return
    # Create a backup file
    backup_filepath = filepath + ".bak"
    try:
        with (
            Path(filepath).open("r", encoding="utf-8") as f_in,
            Path(backup_filepath).open("w", encoding="utf-8") as f_bak,
        ):
            content = f_in.read()
            f_bak.write(content)
    except OSError as e:
        logger.info(f"Error creating backup file {backup_filepath}: {e}", file=sys.stderr)
        return
    formatted_lines = []
    lines = content.splitlines()
    # Keep track of whether we are inside a multiline string (docstring or multiline comment)
    in_multiline_string = False
    current_multiline_string_lines = []
    string_type = ""  # To store if it's a docstring triple quote or comment triple quote
    for _i, line in enumerate(lines):
        stripped_line = line.strip()
        if "# type:" in stripped_line:
            continue
        if stripped_line.startswith("#!"):
            continue
        # Check for start/end of multiline strings
        if stripped_line.startswith((DOC_TH1, DOC_TH2)):
            if not in_multiline_string:
                in_multiline_string = True
                string_type = stripped_line[:3]  # Store the quote type
                current_multiline_string_lines = [line]
            else:  # This means we encountered another triple quote while already in one (e.g., inside a string literal)
                current_multiline_string_lines.append(line)
                # If the line ends with the same quote type, it's the end of the multiline string
                if line.strip().endswith(string_type) and len(line.strip()) > len(string_type):
                    in_multiline_string = False
                    # Process the collected multiline string
                    processed_string = "\n".join(current_multiline_string_lines)
                    # Extract content for wrapping
                    content_to_wrap = processed_string[len(string_type) : -len(string_type)]
                    wrapped_content = textwrap.fill(
                        content_to_wrap,
                        width=35,
                        initial_indent=string_type,
                        subsequent_indent=string_type + " " * (len(string_type) - 1),  # Indent subsequent lines
                        break_long_words=False,
                        break_on_hyphens=False,
                    )
                    # Add the closing quotes back
                    if not wrapped_content.endswith(string_type):
                        wrapped_content += string_type
                    formatted_lines.append(wrapped_content)
                    current_multiline_string_lines = []
                    string_type = ""
            continue
        # If we are inside a multiline string, just append the line
        if in_multiline_string:
            current_multiline_string_lines.append(line)
            # Check if this line is the end of the multiline string
            if line.strip().endswith(string_type) and len(line.strip()) > len(string_type):
                in_multiline_string = False
                # Process the collected multiline string
                processed_string = "\n".join(current_multiline_string_lines)
                content_to_wrap = processed_string[len(string_type) : -len(string_type)]
                wrapped_content = textwrap.fill(
                    content_to_wrap,
                    width=35,
                    initial_indent=string_type,
                    subsequent_indent=string_type + " " * (len(string_type) - 1),
                    break_long_words=False,
                    break_on_hyphens=False,
                )
                if not wrapped_content.endswith(string_type):
                    wrapped_content += string_type
                formatted_lines.append(wrapped_content)
                current_multiline_string_lines = []
                string_type = ""
            continue
        # Handle single-line comments
        comment_index = line.find("#")
        if comment_index != -1:
            code_part = line[:comment_index]
            comment_part = line[comment_index:].strip()  # Get the comment part and strip leading/trailing whitespace
            if comment_part:  # If there's an actual comment
                # Wrap the comment part
                # We need to preserve the indentation of the comment
                comment_indent = " " * (len(line) - len(line.lstrip()))
                # Remove the '#' for wrapping
                comment_content = comment_part[1:].strip()
                # Use textwrap.fill, ensuring it respects word boundaries
                wrapped_comment = textwrap.fill(
                    comment_content,
                    width=35,
                    initial_indent=comment_indent + "# ",  # Add back comment marker and space
                    subsequent_indent=comment_indent + "# ",
                    break_long_words=False,
                    break_on_hyphens=False,
                )
                formatted_lines.append(code_part + wrapped_comment[len(comment_indent + "# ") :])
            else:
                # If it's just a comment marker with no text, keep the original line
                formatted_lines.append(line)
        else:
            # No comment, just add the line as is
            formatted_lines.append(line)
    # If we were still in a multiline string at the end of the file (malformed input)
    if in_multiline_string:
        formatted_lines.extend(current_multiline_string_lines)
    final_formatted_content = "\n".join(formatted_lines)
    # Verify if the result is parsable by AST
    try:
        ast.parse(final_formatted_content)
        # If parsing is successful, write to the file
        try:
            Path(filepath).write_text(final_formatted_content, encoding="utf-8")
            logger.info(f"Successfully formatted {filepath}. Backup created at {backup_filepath}")
        except OSError as e:
            logger.info(f"Error writing formatted content to {filepath}: {e}", file=sys.stderr)
    except SyntaxError as e:
        temp_file = Path("temporary.py")
        temp_file.write_text(final_formatted_content, encoding="utf-8")
        logger.info(
            f"Error: Formatted code is not parsable by AST. Aborting write operation for {filepath}.", file=sys.stderr
        )
        logger.info(f"AST Syntax Error: {e}", file=sys.stderr)
        # Optionally, you could restore from backup here if you don't want to leave the file modified
        Path(backup_filepath).replace(filepath)
        logger.info(f"Restored {filepath} from backup.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.info("Usage: python format_python.py <file_path>")
        sys.exit(1)
    file_to_format = sys.argv[1]
    format_python_file(file_to_format)
