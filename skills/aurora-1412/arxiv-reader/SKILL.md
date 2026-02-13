ArXiv Reader Skill

This skill allows the agent to read one arXiv paper (by arXiv ID or URL) and output raw markdown notes by running a Python script.

Setup
Install dependencies in your Python environment:
pip install -r "{baseDir}/requirements.txt"

Configure environment variables (for example in .env):
- LLM_BASE_URL
- LLM_API_KEY
- LLM_TEMPERATURE
- LLM_MAX_TOKENS

Instructions
To read a paper:
Execute the Python script located at {baseDir}/main.py. Use the following command:
python "{baseDir}/main.py" --arxiv-id "<arxiv_id_or_url>"
Typical examples of <arxiv_id_or_url>:
- New style ID: 2401.12345
- New style ID with version: 2401.12345v2
- Legacy style ID: cs/9901001
- abs URL: https://arxiv.org/abs/2401.12345
- abs URL with version: https://arxiv.org/abs/2401.12345v2
- pdf URL: https://arxiv.org/pdf/2401.12345.pdf
The script will output the paper reading result in raw markdown format.
Return the script's output directly as the final answer.

To list available paper categories:
python "{baseDir}/main.py" --list

If the user specifies a category, run:
python "{baseDir}/main.py" --arxiv-id "<arxiv_id_or_url>" --category "<category_name>"

Adding a New Category
If none of the existing categories fits, you can add a new category under skills/.
Follow these rules:
1. The new category must not duplicate any existing category.
2. The new category folder name is the category name.
3. The new category folder must contain exactly these two files:
   - _metadata.md: describe the characteristics of papers in this category and provide keywords.
   - reading_prompt.md: explain how to read papers in this category and what format the generated reading notes should follow.

Example structure
skills/
  <category_name>/
    _metadata.md
    reading_prompt.md
