import re
import os

# Path to your markdown file
markdown_file = "backend.md"

# Read the entire markdown file
with open(markdown_file, "r", encoding="utf-8") as f:
    content = f.read()

# This regex assumes your file headers are in the form:
# ### <number>. <Section Title> (<file_path>)
# followed by a code block starting with ``` (optionally with "python") and ending with ```
pattern = re.compile(
    r"###\s+\d+\.\s+.*\((?P<filepath>.+?)\)[\s\S]*?```(?:python)?\n(?P<code>[\s\S]*?)\n```",
    re.MULTILINE
)

# Find all matches in the markdown file
matches = pattern.finditer(content)

for match in matches:
    filepath = match.group("filepath").strip()
    code = match.group("code")

    # Create directory structure if it doesn't exist
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

    # Write the extracted code to the file
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(code)
        print(f"Created file: {filepath}")
