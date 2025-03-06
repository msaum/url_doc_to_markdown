#!/usr/bin/env python3
###############################################################################
# Name:      url2markdown.py
# Purpose:   Create a markdown file from a URL.
#            The output is in Markdown format.
# Version:   1.0
# Date:      March 6, 2025
# Author(s): mark@saum.net
###############################################################################

import os
import sys
from newspaper import Article, Config
from datetime import datetime
import re
import time
from requests.exceptions import RequestException
import random
import json
from urllib.parse import urlparse
from http.cookiejar import CookieJar
from newspaper.network import get_html
from newspaper.utils import domain_to_filename

def clean_filename(title):
    """Clean the title to create a valid filename."""
    # Remove invalid characters and replace spaces with underscores
    clean = re.sub(r'[<>:"/\\|?*]', '', title)
    clean = clean.replace(' ', '_')
    return clean[:100]  # Limit length to avoid too long filenames

def get_random_user_agent():
    """Return a random modern browser user agent."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
    ]
    return random.choice(user_agents)

def get_browser_headers():
    """Return realistic browser headers."""
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

def extract_article(url, max_retries=3, timeout=10):
    """Extract article content from URL using newspaper3k with browser-like behavior."""
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        print("Error: URL must start with http:// or https://")
        return None

    # Configure newspaper with browser-like settings
    config = Config()
    config.browser_user_agent = get_random_user_agent()
    config.request_timeout = timeout
    config.cookie_jar = CookieJar()
    config.headers = get_browser_headers()

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}...")
            
            # Add random delay between attempts (1-3 seconds)
            if attempt > 0:
                delay = random.uniform(1, 3)
                print(f"Waiting {delay:.1f} seconds before retrying...")
                time.sleep(delay)

            article = Article(url, config=config)
            
            print("Downloading article...")
            # First get the HTML with our custom headers
            html = get_html(url, config=config)
            if not html:
                print("Failed to get HTML content")
                continue
                
            article.set_html(html)
            
            print("Parsing article...")
            article.parse()
            
            print("Extracting NLP features...")
            article.nlp()  # This extracts keywords and summary
            
            if not article.title or not article.text:
                print("Error: Could not extract article content. The page might be empty or not accessible.")
                continue
                
            return {
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'summary': article.summary,
                'keywords': article.keywords
            }
            
        except RequestException as e:
            print(f"Network error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Waiting 2 seconds before retrying...")
                time.sleep(2)
            continue
        except Exception as e:
            print(f"Error extracting article: {str(e)}")
            print("Tip: Some websites may block automated requests. Try a different URL or website.")
            if attempt < max_retries - 1:
                print(f"Waiting 2 seconds before retrying...")
                time.sleep(2)
            continue
    
    print(f"Failed to extract article after {max_retries} attempts.")
    return None

def create_markdown(article_data, source_url):
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

Source: [{source_url}]({source_url})
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
    
    # Extract article content with retries
    article_data = extract_article(url)
    if not article_data:
        print("Failed to extract article content")
        sys.exit(1)

    # Create markdown content
    markdown_content = create_markdown(article_data, url)
    if not markdown_content:
        print("Failed to create markdown content")
        sys.exit(1)

    # Save to file
    if not save_markdown(markdown_content, article_data['title']):
        print("Failed to save markdown file")
        sys.exit(1)

if __name__ == "__main__":
    main() 