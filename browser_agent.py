import webbrowser
import urllib.parse
import requests
from bs4 import BeautifulSoup

def google_search(query: str) -> str:
    """Performs a Google Search in default browser."""
    safe_q = urllib.parse.quote(query.strip())
    url = f"https://www.google.com/search?q={safe_q}"
    print(f"[Browser Agent] Opening Google Search: '{query}'")
    webbrowser.open(url)
    return f"Searching Google for {query}, Boss."

def youtube_search(query: str) -> str:
    """Searches YouTube in default browser."""
    safe_q = urllib.parse.quote(query.strip())
    url = f"https://www.youtube.com/results?search_query={safe_q}"
    print(f"[Browser Agent] Opening YouTube Search: '{query}'")
    webbrowser.open(url)
    return f"Searching YouTube for {query}, Boss."

def read_web_page(url: str, max_chars: int = 2000) -> str:
    """Fetches a webpage and extracts clean readable paragraph text."""
    target_url = url if url.startswith("http") else f"https://{url}"
    print(f"[Browser Agent] Fetching webpage content: {target_url}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        res = requests.get(target_url, headers=headers, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            # Remove scripts and styling elements
            for elem in soup(["script", "style", "nav", "footer", "header"]):
                elem.extract()
            paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 30]
            text_content = " ".join(paragraphs[:6])
            clean_text = " ".join(text_content.split())
            if len(clean_text) > max_chars:
                clean_text = clean_text[:max_chars] + "..."
            return clean_text if clean_text else "Page loaded but no readable text paragraph found."
        else:
            return f"Failed to fetch webpage (HTTP status {res.status_code})."
    except Exception as e:
        print(f"[Browser Agent Error] Webpage fetch failed: {e}")
        return f"Could not read webpage: {e}"
