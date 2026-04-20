"""Web search tools with Tavily primary + DuckDuckGo fallback."""

import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result."""
    title: str
    url: str
    content: str
    score: float


class WebSearchTool:
    """Web search with three-tier fallback strategy."""
    
    def __init__(self, tavily_api_key: Optional[str] = None):
        self.tavily_api_key = tavily_api_key
        self._tavily_client = None
        
        if tavily_api_key:
            try:
                from tavily import TavilyClient
                self._tavily_client = TavilyClient(api_key=tavily_api_key)
            except ImportError:
                logger.warning("Tavily not installed, using DuckDuckGo only")
    
    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Search the web using the three-tier fallback strategy."""
        results = []
        
        if self._tavily_client:
            try:
                results = await self._search_tavily(query, max_results)
                if results:
                    return results
            except Exception as e:
                logger.warning(f"Tavily search failed: {e}")
        
        try:
            results = await self._search_duckduckgo(query, max_results)
            if results:
                return results
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
        
        return results
    
    async def _search_tavily(self, query: str, max_results: int) -> list[SearchResult]:
        """Search using Tavily API."""
        import asyncio
        
        def _sync_search():
            response = self._tavily_client.search(
                query=query,
                max_results=max_results,
                include_answer=True,
                include_raw_content=False,
            )
            return response
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _sync_search)
        
        results = []
        for item in response.get('results', []):
            results.append(SearchResult(
                title=item.get('title', ''),
                url=item.get('url', ''),
                content=item.get('content', ''),
                score=item.get('score', 0.0),
            ))
        
        return results
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> list[SearchResult]:
        """Search using DuckDuckGo (no API key required)."""
        import asyncio
        
        def _sync_search():
            from duckduckgo_search import DDGS
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=max_results))
            return results
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _sync_search)
        
        results = []
        for item in response:
            results.append(SearchResult(
                title=item.get('title', ''),
                url=item.get('href', ''),
                content=item.get('body', ''),
                score=1.0,
            ))
        
        return results
    
    def search_sync(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Synchronous search (for non-async contexts)."""
        return asyncio.run(self.search(query, max_results))