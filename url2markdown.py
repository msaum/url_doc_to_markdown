#!/usr/bin/env python3
###############################################################################
# Name:      url2markdown.py
# Purpose:   Create a markdown file from a URL.
#            The output is in Markdown format.
# Version:   1.0
# Date:      March 6, 2025
# Author(s): mark@saum.net
###############################################################################import os
import sys
from newspaper import Article
from datetime import datetime
import re

def clean_filename(title):
    """Clean the title to create a valid filename."""
    # Remove invalid characters and replace spaces with underscores
    clean = re.sub(r'[<>:"/\\|?*]', '', title)
    clean = clean.replace(' ', '_')
    return clean[:100]  # Limit length to avoid too long filenames

def extract_article(url):
    """Extract article content from URL using newspaper3k."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()  # This extracts keywords and summary
        
        return {
            'title': article.title,
            'text': article.text,
            'authors': article.authors,
            'publish_date': article.publish_date,
            'top_image': article.top_image,
            'summary': article.summary,
            'keywords': article.keywords
        }
    except Exception as e:
        print(f"Error extracting article: {str(e)}")
        return None

def create_markdown(article_data):
    """Create markdown content from article data."""
    if not article_data:
        return None

    # Format the date if available
    date_str = ""
    if article_data['publish_date']:
        date_str = article_data['publish_date'].strftime("%Y-%m-%d")

    # Create markdown content
    markdown_content = f"""# {article_data['title']}

{date_str}

## Summary
{article_data['summary']}

## Article
{article_data['text']}

## Keywords
{', '.join(article_data['keywords'])}

---
*Extracted from article by {', '.join(article_data['authors']) if article_data['authors'] else 'Unknown author'}*
"""
    return markdown_content

def save_markdown(content, title):
    """Save markdown content to file."""
    if not content:
        return False

    # Create output directory if it doesn't exist
    output_dir = "articles"
    os.makedirs(output_dir, exist_ok=True)

    # Create filename from title
    filename = clean_filename(title)
    filepath = os.path.join(output_dir, f"{filename}.md")

    # Save the content
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Article saved to: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python url_to_markdown.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Processing article from: {url}")
    
    # Extract article content
    article_data = extract_article(url)
    if not article_data:
        print("Failed to extract article content")
        sys.exit(1)

    # Create markdown content
    markdown_content = create_markdown(article_data)
    if not markdown_content:
        print("Failed to create markdown content")
        sys.exit(1)

    # Save to file
    if not save_markdown(markdown_content, article_data['title']):
        print("Failed to save markdown file")
        sys.exit(1)

if __name__ == "__main__":
    main() 