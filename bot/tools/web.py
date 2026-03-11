"""Web tools - search and fetch URLs."""

import httpx
from ddgs import DDGS

DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web using DuckDuckGo and return results with titles, URLs, and snippets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default 5).",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch the text content of a URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch.",
                    },
                },
                "required": ["url"],
            },
        },
    },
]


def execute(name, args, context):
    if name == "web_search":
        return _web_search(args["query"], args.get("max_results", 5))
    elif name == "fetch_url":
        return _fetch_url(args["url"])


def _web_search(query, max_results=5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No results found."
        lines = []
        for r in results:
            lines.append(f"Title: {r['title']}\nURL: {r['href']}\n{r['body']}\n")
        return "\n".join(lines)
    except Exception as e:
        return f"Error searching: {e}"


def _fetch_url(url):
    try:
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            text = response.text
            if len(text) > 10000:
                text = text[:10000] + "\n... (truncated)"
            return text
    except Exception as e:
        return f"Error fetching URL: {e}"
