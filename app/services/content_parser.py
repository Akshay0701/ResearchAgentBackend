import requests
from newspaper import Article
from trafilatura import fetch_url, extract
from app.utils.logger import logger
from typing import Optional

class ContentParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _try_newspaper(self, url: str) -> Optional[str]:
        """Try to parse content using newspaper3k"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            if article.text:
                return article.text
        except Exception as e:
            logger.debug(f"Newspaper3k parsing failed for {url}: {str(e)}")
        return None

    def _try_trafilatura(self, url: str) -> Optional[str]:
        """Try to parse content using trafilatura"""
        try:
            downloaded = fetch_url(url, headers=self.headers)
            if downloaded:
                text = extract(downloaded, include_comments=False, include_tables=True)
                if text:
                    return text
        except Exception as e:
            logger.debug(f"Trafilatura parsing failed for {url}: {str(e)}")
        return None

    def fetch_and_parse(self, url: str) -> str:
        """Fetch and parse content from URL using multiple methods"""
        logger.info(f"Fetching and parsing URL: {url}")
        
        # Try newspaper3k first
        content = self._try_newspaper(url)
        if content:
            return content

        # If newspaper3k fails, try trafilatura
        content = self._try_trafilatura(url)
        if content:
            return content

        # If both methods fail, try a simple requests fallback
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text[:2000]  # Limit size for fallback
        except Exception as e:
            logger.error(f"All parsing methods failed for {url}: {str(e)}")
            return "" 