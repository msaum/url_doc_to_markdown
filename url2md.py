#!/usr/bin/env python3
"""Convert web articles to markdown format with metadata extraction.
###############################################################################
# Name:      url2md.py
# Purpose:   Create a markdown file from a URL.
#            The output is in Markdown format.
# Version:   1.0
# Date:      March 6, 2025
# Author(s): mark@saum.net
###############################################################################
"""

import os
import sys
import re
import time
import random
from http.cookiejar import CookieJar
from requests.exceptions import RequestException
from newspaper import Article, Config
from newspaper.network import get_html
from newspaper.article import ArticleException
import click
import nltk

def clean_filename(title):
    """Clean the title to create a valid filename."""
    # Remove invalid characters and replace spaces with underscores
    clean = re.sub(r'[<>:"/\\|?*]', "", title)
    clean = clean.replace(" ", "_")
    return clean[:100]  # Limit length to avoid too long filenames


def get_random_user_agent():
    """Return a random modern browser user agent."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ]
    return random.choice(user_agents)


def get_browser_headers():
    """Return realistic browser headers."""
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "DNT": "1",
        "Referer": random.choice([
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://duckduckgo.com/",
            "https://www.linkedin.com/",
            "https://www.facebook.com/",
        ]),
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }


def extract_article(url, max_retries=5, timeout=30):
    """Extract article content from URL using newspaper3k with browser-like behavior."""
    # Validate URL format
    if not url.startswith(("http://", "https://")):
        print("Error: URL must start with http:// or https://")
        return None

    # Configure newspaper with browser-like settings
    config = Config()
    config.browser_user_agent = get_random_user_agent()
    config.request_timeout = timeout
    config.cookie_jar = CookieJar()
    config.headers = get_browser_headers()
    config.keep_article_html = True
    config.http_success_only = False
    config.memoize_articles = False
    config.browser_user_agent = get_random_user_agent()
    config.verify_ssl = False  # Sometimes needed for certain sites

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}...")

            # Add random delay between attempts (3-7 seconds)
            if attempt > 0:
                delay = random.uniform(3, 7)
                print(f"Waiting {delay:.1f} seconds before retrying...")
                time.sleep(delay)

            # Simulate human-like behavior
            if random.random() < 0.3:  # 30% chance to add extra delay
                extra_delay = random.uniform(2, 4)
                print(f"Adding extra delay of {extra_delay:.1f} seconds...")
                time.sleep(extra_delay)

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
                print(
                    "Error: Could not extract article content. "
                    "The page might be empty or not accessible."
                )
                continue

            return {
                "title": article.title,
                "text": article.text,
                "authors": article.authors,
                "publish_date": article.publish_date,
                "top_image": article.top_image,
                "summary": article.summary,
                "keywords": article.keywords,
            }

        except RequestException as e:
            print(f"Network error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                delay = random.uniform(4, 8)
                print(f"Waiting {delay:.1f} seconds before retrying...")
                time.sleep(delay)
            continue
        except ArticleException as e:
            print(f"Error extracting article: {str(e)}")
            print(
                "Tip: Some websites may block automated requests. Try a different URL or website."
            )
            if attempt < max_retries - 1:
                delay = random.uniform(4, 8)
                print(f"Waiting {delay:.1f} seconds before retrying...")
                time.sleep(delay)
            continue
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                delay = random.uniform(4, 8)
                print(f"Waiting {delay:.1f} seconds before retrying...")
                time.sleep(delay)
            continue

    print(f"Failed to extract article after {max_retries} attempts.")
    return None


def create_markdown(article_data, source_url):
    """Create markdown content from article data."""
    if not article_data:
        return None

    # Format the date if available
    date_str = ""
    if article_data["publish_date"]:
        date_str = article_data["publish_date"].strftime("%Y-%m-%d")

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


def save_markdown(content, title, output_dir="articles"):
    """Save markdown content to file."""
    if not content:
        return False

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create filename from title
    filename = clean_filename(title)
    filepath = os.path.join(output_dir, f"{filename}.md")

    # Save the content
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Article saved to: {filepath}")
        return True
    except (OSError, IOError) as e:
        print(f"Error saving file: {str(e)}")
        return False


def extract_urls_from_markdown(markdown_file):
    """Extract URLs from a markdown file."""
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Match both markdown links [text](url) and bare URLs
            urls = re.findall(r'\[([^\]]+)\]\(([^)]+)\)|(?<![\[\(])(https?://[^\s<>"]+)(?![\]\)])', content)
            # Extract URLs from matches, handling both link formats
            return [url[1] if url[1] else url[2] for url in urls]
    except (OSError, IOError) as e:
        print(f"Error reading markdown file: {str(e)}")
        return []


@click.command()
@click.argument("url", type=click.STRING, required=False)
@click.option(
    "--markdown-file",
    "-m",
    help="Process all URLs from a markdown file",
)
@click.option(
    "--output-dir",
    "-o",
    default="articles",
    help="Directory to save the markdown file (default: articles)",
)
@click.option(
    "--timeout",
    "-t",
    default=30,
    help="Timeout in seconds for the request (default: 30)",
)
@click.option(
    "--max-retries",
    "-r",
    default=5,
    help="Maximum number of retry attempts (default: 5)",
)
@click.version_option(version="1.0.0")
def main(url, markdown_file, output_dir, timeout, max_retries):
    """Convert web articles to markdown format.

    URL: The URL of the article to convert (not required if --markdown-file is used)
    """
    nltk.download('punkt_tab')

    if not url and not markdown_file:
        print("Error: Either URL or --markdown-file must be provided")
        sys.exit(1)

    if markdown_file:
        urls = extract_urls_from_markdown(markdown_file)
        if not urls:
            print("No URLs found in markdown file")
            sys.exit(1)
        print(f"Found {len(urls)} URLs in markdown file")
        for url in urls:
            print(f"\nProcessing: {url}")
            process_url(url, output_dir, timeout, max_retries)
    else:
        process_url(url, output_dir, timeout, max_retries)


def process_url(url, output_dir, timeout, max_retries):
    """Process a single URL and convert it to markdown."""
    print(f"Processing article from: {url}")

    # Extract article content with retries
    article_data = extract_article(url, max_retries=max_retries, timeout=timeout)
    if not article_data:
        print("Failed to extract article content")
        return False

    # Create markdown content
    markdown_content = create_markdown(article_data, url)
    if not markdown_content:
        print("Failed to create markdown content")
        return False

    # Save to file
    if not save_markdown(markdown_content, article_data["title"], output_dir):
        print("Failed to save markdown file")
        return False

    return True


if __name__ == "__main__":
    main()  # noqa: E1120, F821, F822, F823 Click handles argument passing internally
