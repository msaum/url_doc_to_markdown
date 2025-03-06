# URL to Markdown Converter

This Python script extracts article content from a given URL and converts it to a well-formatted markdown file.

## Features

- Extracts article title, content, authors, publication date, and summary
- Generates keywords from the article
- Creates clean, formatted markdown output
- Saves articles in an organized directory structure
- Handles various article formats and websites

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script with a URL as an argument:

```bash
python url_to_markdown.py "https://example.com/article"
```

The script will:
1. Download and parse the article
2. Extract relevant information
3. Create a markdown file in the `articles` directory
4. Name the file based on the article title

## Output

The generated markdown file will include:
- Article title
- Publication date
- Summary
- Full article content
- Keywords
- Author information

## Requirements

- Python 3.6 or higher
- Dependencies listed in requirements.txt
