from langchain.utilities import DuckDuckGoSearchAPIWrapper
from typing import List, Dict, Any

def search_duckduckgo(query: str) -> List[Dict[str, str]]:
    """
    Search the web using DuckDuckGo through LangChain
    
    Args:
        query (str): The search query
        
    Returns:
        list: A list of search results
    """
    try:
        # Initialize the DuckDuckGo search wrapper with max_results in constructor
        search = DuckDuckGoSearchAPIWrapper(max_results=5)
        
        # Perform the search and get results - pass max_results as positional argument
        raw_results = search.results(query, 5) # Passing 5 as positional argument
        
        # Format the results to match the expected structure
        formatted_results = []
        
        for result in raw_results:
            formatted_results.append({
                "title": result.get("title", "No title"),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "No description available")
            })
        
        return formatted_results
    
    except Exception as e:
        print(f"Error searching DuckDuckGo: {str(e)}")
        # Return a fallback result if the search fails
        return [
            {
                "title": f"Search result for '{query}'",
                "link": "https://example.com/search",
                "snippet": "Could not retrieve search results. Please try again later."
            }
        ] 