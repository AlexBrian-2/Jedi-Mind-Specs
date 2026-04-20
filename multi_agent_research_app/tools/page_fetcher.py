"""Page fetcher with httpx + BeautifulSoup4 for deep-dive parsing."""

import asyncio
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FetchedPage:
    """Fetched web page."""
    url: str
    title: str
    content: str
    error: Optional[str] = None


class PageFetcher:
    """Fetch and parse web pages."""
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ResearchOrchestrator/1.0)',
        }
    
    async def fetch(self, url: str) -> FetchedPage:
        """Fetch a URL and parse its content."""
        try:
            import httpx
            
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
                headers=self._headers,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                content = await self._parse_html(response.text)
                title = self._extract_title(response.text)
                
                return FetchedPage(
                    url=url,
                    title=title,
                    content=content,
                )
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return FetchedPage(
                url=url,
                title='',
                content='',
                error=str(e),
            )
    
    def _parse_html(self, html: str) -> str:
        """Parse HTML and extract text content."""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html, 'lxml')
            
            for script in soup(['script', 'style']):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            
            lines = [line for line in text.split('\n') if line.strip()]
            cleaned_lines = []
            prev_line = ''
            for line in lines:
                if line != prev_line:
                    cleaned_lines.append(line)
                    prev_line = line
            
            return '\n'.join(cleaned_lines[:500])
        except Exception as e:
            logger.warning(f"Failed to parse HTML: {e}")
            return html[:5000]
    
    def _extract_title(self, html: str) -> str:
        """Extract page title from HTML."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')
            title = soup.find('title')
            if title:
                return title.get_text(strip=True)
        except:
            pass
        return ''
    
    async def fetch_multiple(self, urls: list[str]) -> list[FetchedPage]:
        """Fetch multiple URLs concurrently."""
        tasks = [self.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        pages = []
        for result in results:
            if isinstance(result, FetchedPage):
                pages.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Fetch error: {result}")
        
        return pages
    
    def fetch_sync(self, url: str) -> FetchedPage:
        """Synchronous fetch (for non-async contexts)."""
        return asyncio.run(self.fetch(url))