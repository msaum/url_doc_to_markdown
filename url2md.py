#!/usr/bin/env python3
"""Convert web articles to markdown format with metadata extraction.
###############################################################################
# Name:      url2md.py
# Purpose:   Create a markdown file from a URL or process URLs from a markdown file.
#            The output is in Markdown format.
# Version:   1.1
# Date:      March 6, 2025
# Author(s): mark@saum.net
###############################################################################
"""

import os
import sys
import time
import random
import click
import trafilatura
import re
from datetime import datetime
from urllib.parse import urlparse

def sanitize_filename(url):
    """Create a sanitized filename from the URL."""
    parsed = urlparse(url)
    # Get the domain and path
    domain = parsed.netloc
    path = parsed.path.strip('/')
    
    # If path is empty, use domain as filename
    if not path:
        return domain
    
    # Use the last part of the path as filename
    filename = path.split('/')[-1]
    if not filename:
        filename = domain
    
    # Remove any file extensions and invalid characters
    filename = os.path.splitext(filename)[0]
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_'))
    
    # If filename is empty after sanitization, use domain
    if not filename:
        filename = domain
    
    # If still empty, generate a random name
    if not filename:
        random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        filename = f"article_{random_suffix}"
    
    return filename

def extract_article(url, max_retries=3):
    """Extract article content using trafilatura."""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}...")
            
            # Download the webpage
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                print("Failed to download the webpage")
                continue
                
            # Extract content
            content = trafilatura.extract(
                downloaded,
                include_links=True,
                include_images=True,
                include_tables=True
            )
            
            if not content:
                print("Failed to extract content")
                continue
                
            # Extract metadata
            metadata = trafilatura.extract_metadata(downloaded)
            
            # Handle metadata fields
            title = metadata.title if metadata and hasattr(metadata, 'title') else 'Untitled'
            authors = metadata.authors if metadata and hasattr(metadata, 'authors') else []
            publish_date = metadata.date if metadata and hasattr(metadata, 'date') else datetime.now().strftime("%Y-%m-%d")
            
            return {
                'title': title,
                'content': content,
                'authors': authors,
                'publish_date': publish_date
            }
            
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retrying
            continue
            
    return None

def save_as_markdown(content, url, output_dir="articles"):
    """Save the article content as markdown file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename without timestamp
    filename = sanitize_filename(url)
    full_filename = f"{filename}.md"
    filepath = os.path.join(output_dir, full_filename)
    
    # Format the date if available
    date_str = content['publish_date'] if content['publish_date'] else ""
    
    # Prepare markdown content
    markdown_content = f"""# {content['title']}

{date_str}

{content['content']}

---
*Extracted from article by {', '.join(content['authors']) if content['authors'] else 'Unknown author'}*

Source: [{url}]({url})
"""
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filepath

def article_exists(url, output_dir):
    """Check if an article has already been downloaded."""
    filename = sanitize_filename(url)
    filepath = os.path.join(output_dir, f"{filename}.md")
    return os.path.exists(filepath)

def clean_url(url):
    """Clean and validate a URL."""
    # Remove any trailing punctuation
    url = url.rstrip('.,;:!?()[]{}')
    # Remove any whitespace
    url = url.strip()
    # Ensure it starts with http
    if not url.startswith('http'):
        return None
        
    # Parse the URL to handle fragments and query parameters properly
    parsed = urlparse(url)
    # Reconstruct the URL without fragments and with cleaned path
    clean_path = parsed.path.strip('/')
    if clean_path:
        # Clean the path component
        clean_path = "".join(c for c in clean_path if c.isalnum() or c in ('/', '-', '_'))
        if not clean_path:
            clean_path = None
            
    # Reconstruct the URL
    if clean_path:
        url = f"{parsed.scheme}://{parsed.netloc}/{clean_path}"
    else:
        url = f"{parsed.scheme}://{parsed.netloc}"
        
    return url

def extract_urls_from_markdown(markdown_file):
    """Extract URLs from a markdown file."""
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all URLs in markdown format [text](url) or plain URLs
        urls = set()  # Use set to automatically remove duplicates
        
        # Match markdown links [text](url)
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for _, url in markdown_links:
            url = clean_url(url)
            if url:
                urls.add(url)
        
        # Match plain URLs
        plain_urls = re.findall(r'https?://[^\s<>"]+', content)
        for url in plain_urls:
            url = clean_url(url)
            if url:
                urls.add(url)
        
        # Convert set to sorted list and log the URLs
        unique_urls = sorted(list(urls))
        click.echo("\nExtracted URLs:")
        for i, url in enumerate(unique_urls, 1):
            click.echo(f"{i}. {url}")
        click.echo()
        
        return unique_urls
    except Exception as e:
        click.echo(f"Error reading markdown file: {str(e)}", err=True)
        return []

@click.command()
@click.argument('input_source')
@click.option('--output-dir', default='articles', help='Directory to save markdown files')
def main(input_source, output_dir):
    """Extract article content from URL or process URLs from a markdown file."""
    # Check if input is a file or URL
    if os.path.isfile(input_source):
        click.echo(f"Processing markdown file: {input_source}")
        urls = extract_urls_from_markdown(input_source)
        
        if not urls:
            click.echo("No URLs found in the markdown file", err=True)
            sys.exit(1)
            
        click.echo(f"Found {len(urls)} unique URLs to process")
        
        # Create a set of already downloaded articles
        downloaded_articles = set()
        for url in urls:
            if article_exists(url, output_dir):
                click.echo(f"Skipping already downloaded article: {url}")
                downloaded_articles.add(url)
                continue
        
        # Filter out already downloaded articles
        urls_to_process = [url for url in urls if url not in downloaded_articles]
        click.echo(f"\nProcessing {len(urls_to_process)} new articles...")
        
        for url in urls_to_process:
            click.echo(f"\nProcessing URL: {url}")
            article = extract_article(url)
            if article:
                filepath = save_as_markdown(article, url, output_dir)
                click.echo(f"Article saved to: {filepath}")
            else:
                click.echo(f"Failed to process URL: {url}", err=True)
    else:
        # Process single URL
        click.echo(f"Processing URL: {input_source}")
        article = extract_article(input_source)
        if not article:
            click.echo("Failed to extract article content", err=True)
            sys.exit(1)
        
        filepath = save_as_markdown(article, input_source, output_dir)
        click.echo(f"Article saved to: {filepath}")

if __name__ == '__main__':
    main()
