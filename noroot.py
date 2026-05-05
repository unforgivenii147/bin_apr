#!/data/data/com.termux/files/usr/bin/python
import re
import sys
from pathlib import Path
from dh import get_nobinary

# Regex to find bash 'if' blocks starting with '['
# It captures the variable name and the entire block until 'fi'
# Handles potential multi-line content and subtle formatting variations
IF_BLOCK_REGEX = re.compile(
    r"^if\s+\[\s*\$\((\S+)\)\s*\{\-ne\s+0\s*\}\]\s*;\s*then\s*\n"  # Start of the if block
    r"((?:.|\n)*?)"  # Capture group for the content inside the block
    r"^\s*exit\s+1\s*$"  # Look for 'exit 1' on its own line at the end
    r"(.*?)^\s*fi",  # Capture the rest of the line after exit 1 and ensure it ends with 'fi'
    re.MULTILINE | re.IGNORECASE,
)


def remove_conditional_exit_blocks(file_path: Path):
    """
    Recursively removes specific bash 'if' blocks from a file.
    These blocks typically check if a command's exit status is not zero,
    print an error, and then exit.
    """
    try:
        original_content = file_path.read_text(encoding="utf-8")
        modified_content = original_content

        # Find and remove all matching blocks
        # We use a loop because re.sub might not handle overlapping matches correctly if not careful
        # and we want to ensure all are removed.
        while True:
            match = IF_BLOCK_REGEX.search(modified_content)
            if not match:
                break

            # Reconstruct the content, skipping the matched block.
            # We keep the content *before* the block and the content *after* the block.
            # This effectively removes the entire if block (including its 'fi')
            # and anything immediately following it before the next 'fi'.
            # The regex already captures the lines after 'exit 1' up to 'fi'.
            # We simply replace the entire match with the content *before* the match
            # and the content *after* the match part that was captured by the last group in the regex.

            # The regex captures the content *inside* the if block in group 1 and
            # the content *after* 'exit 1' and *before* 'fi' in group 2.
            # For simplicity and to avoid complex reconstruction:
            # Replace the entire matched block with an empty string.
            # This is a more robust way to remove the full 'if ... exit 1 ... fi' structure.
            modified_content = modified_content[: match.start()] + modified_content[match.end() :]

            # If we want to keep lines *after* the 'fi', we'd need more sophisticated logic.
            # For now, this removes the entire matched block.
            # If the requirement is to *only* remove the `if [[ $(...) -ne 0 ]]; then ... exit 1; fi`
            # part and keep preceding/succeeding code, the regex and replacement logic
            # would need to be more precise about what is being removed.
            # A simpler approach is to remove the *entire* block.

            # Re-matching from the start of the modified content ensures we catch all occurrences.
            # A better approach might be to use re.sub with a callback function.
            # For simpler removal, we'll just replace the matched part and continue searching.
            # The current loop structure handles this by repeatedly searching the modified string.
            pass  # The loop continues until no more matches are found

        if original_content != modified_content:
            file_path.write_text(modified_content, encoding="utf-8")
            print(f"Cleaned: {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)


def main():
    """
    Traverses the current directory and its subdirectories,
    processing all files that are likely bash scripts.
    """
    cwd = Path.cwd()
    # Process all files, including those without extensions
    files_to_process = get_nobinary(cwd)

    for item_path in files_to_process:
        if item_path.is_file():
            # Simple heuristic: check for common bash shebang or execute permissions
            # or assume any file might be a bash script if no extension
            try:
                content = item_path.read_text(encoding="utf-8", errors="ignore")
                is_likely_bash = False
                if content.startswith("#!/bin/bash") or content.startswith("#!/usr/bin/env bash"):
                    is_likely_bash = True
                elif oct(item_path.stat().st_mode)[-3:] not in (
                    "000",
                    "001",
                    "010",
                    "011",
                    "002",
                    "012",
                    "100",
                    "110",
                    "111",
                    "101",
                ):  # Check for execute permission for owner, group, or others
                    is_likely_bash = True
                if is_likely_bash:
                    remove_conditional_exit_blocks(item_path)
            except Exception as e:
                print(f"Could not read or process {item_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
