# URL to Markdown Converter

This Python script extracts article content from URLs and converts them to well-formatted markdown files. It can process either a single URL or multiple URLs from a markdown file.

## NOTE

This repository has been superceded by: https://github.com/msaum/mdtools

## Features

- Extracts article title, content, authors, and publication date
- Creates clean, formatted markdown output
- Saves articles in an organized directory structure
- Handles various article formats and websites
- Supports batch processing of URLs from markdown files
- Skips already downloaded articles to avoid duplicates
- Includes robust URL cleaning and validation
- Provides detailed progress and error reporting

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Process a Single URL

```bash
python url2md.py "https://example.com/article"
```

### Process Multiple URLs from a Markdown File

```bash
python url2md.py path/to/your/file.md
```

### Specify Custom Output Directory

```bash
python url2md.py "https://example.com/article" --output-dir custom_folder
```

The script will:
1. Download and parse the article(s)
2. Extract relevant information
3. Create markdown file(s) in the output directory (default: `articles`)
4. Name files based on sanitized article URLs
5. Skip any articles that have already been downloaded

## Output Format

The generated markdown files include:
- Article title
- Publication date
- Full article content
- Author information
- Source URL reference

## Requirements

- Python 3.6 or higher
- Dependencies listed in requirements.txt

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
