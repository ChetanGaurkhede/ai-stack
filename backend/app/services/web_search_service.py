import httpx
import asyncio
from typing import List, Dict, Any, Optional
from app.config import settings
import structlog

logger = structlog.get_logger()


class WebSearchService:
    def __init__(self):
        self.serpapi_key = settings.serpapi_api_key
        self.brave_key = settings.brave_api_key
    
    async def search_web(self, query: str, provider: str = "serpapi", 
                        max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using specified provider
        """
        try:
            if provider == "serpapi":
                return await self._search_serpapi(query, max_results)
            elif provider == "brave":
                return await self._search_brave(query, max_results)
            else:
                raise ValueError(f"Unsupported search provider: {provider}")
        except Exception as e:
            logger.error("Web search failed", error=str(e), provider=provider, query=query)
            raise
    
    async def _search_serpapi(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using SerpAPI"""
        if not self.serpapi_key:
            raise ValueError("SerpAPI key not configured")
        
        async with httpx.AsyncClient() as client:
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": max_results,
                "engine": "google"
            }
            
            response = await client.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            if "organic_results" in data:
                for result in data["organic_results"][:max_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "link": result.get("link", ""),
                        "source": "SerpAPI"
                    })
            
            return results
    
    async def _search_brave(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Brave Search API"""
        if not self.brave_key:
            raise ValueError("Brave API key not configured")
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_key
            }
            
            params = {
                "q": query,
                "count": max_results
            }
            
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            if "web" in data and "results" in data["web"]:
                for result in data["web"]["results"][:max_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("description", ""),
                        "link": result.get("url", ""),
                        "source": "Brave Search"
                    })
            
            return results
    
    async def search_multiple_providers(self, query: str, providers: List[str] = None,
                                      max_results: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Search using multiple providers concurrently"""
        if providers is None:
            providers = ["serpapi", "brave"]
        
        tasks = []
        for provider in providers:
            task = self.search_web(query, provider, max_results)
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            combined_results = {}
            for i, provider in enumerate(providers):
                if isinstance(results[i], Exception):
                    logger.error(f"Search failed for {provider}", error=str(results[i]))
                    combined_results[provider] = []
                else:
                    combined_results[provider] = results[i]
            
            return combined_results
            
        except Exception as e:
            logger.error("Multiple provider search failed", error=str(e))
            raise
    
    def format_search_results_for_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for use as context in LLM"""
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"{i}. {result['title']}\n"
                f"   URL: {result['link']}\n"
                f"   Summary: {result['snippet']}\n"
            )
        
        return "\n".join(context_parts)
    
    async def get_relevant_context(self, query: str, max_results: int = 3) -> str:
        """Get relevant web context for a query"""
        try:
            # Try SerpAPI first, fallback to Brave
            providers_to_try = ["serpapi", "brave"]
            
            for provider in providers_to_try:
                try:
                    results = await self.search_web(query, provider, max_results)
                    if results:
                        return self.format_search_results_for_context(results)
                except Exception as e:
                    logger.warning(f"Search failed for {provider}, trying next provider", error=str(e))
                    continue
            
            return ""
            
        except Exception as e:
            logger.error("Failed to get relevant context", error=str(e))
            return "" 