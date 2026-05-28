import asyncio
import os
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

# Bright Data Scraping Browser CDP Endpoint
# e.g., wss://brd-customer-xxxx-zone-xxxx:password@brd.superproxy.io:9222
SBR_WS_ENDPOINT = os.getenv("BRIGHTDATA_SBR_WS_ENDPOINT", "")

# Bright Data SERP API Configuration
BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY", "")
BRIGHTDATA_SERP_ZONE = os.getenv("BRIGHTDATA_SERP_ZONE", "")

async def scrape_with_brightdata(url: str) -> str:
    """
    Scrapes a web page using Bright Data's cloud-hosted Scraping Browser.
    Bypasses Cloudflare, CAPTCHAs, and renders JavaScript.
    """
    if not SBR_WS_ENDPOINT:
        raise ValueError("Bright Data Scraping Browser endpoint (BRIGHTDATA_SBR_WS_ENDPOINT) is not configured.")
        
    async with async_playwright() as p:
        print(f"[Bright Data] Connecting to Scraping Browser to fetch: {url}")
        browser = await p.chromium.connect_over_cdp(SBR_WS_ENDPOINT)
        try:
            page = await browser.new_page()
            # Navigate with a generous timeout for remote network delays
            await page.goto(url, timeout=90000, wait_until="domcontentloaded")
            
            # Bright Data solves any CAPTCHAs automatically in the background
            content = await page.content()
            return content
        finally:
            await browser.close()

def scrape_with_local_fallback(url: str) -> str:
    """
    Standard HTTP request fallback for local testing.
    """
    print(f"[Local Fallback] Fetching URL: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[Local Fallback] Error fetching {url}: {e}")
        return ""

def clean_html_to_text(html_content: str) -> str:
    """
    Parses HTML content, removes script/style tags, and returns clean readable text.
    """
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script, style, head, nav, footer, header to focus on main content
    for element in soup(["script", "style", "head", "nav", "footer", "header", "meta"]):
        element.decompose()
        
    # Get text and clean up whitespace
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    clean_lines = [line for line in lines if line]
    return "\n".join(clean_lines)

async def smart_scrape(url: str) -> str:
    """
    Attempts to scrape using Bright Data if configured, otherwise falls back to local request.
    Returns clean text content of the page.
    """
    html_content = ""
    method = ""
    
    if SBR_WS_ENDPOINT:
        try:
            html_content = await scrape_with_brightdata(url)
            method = "Bright Data Scraping Browser"
        except Exception as e:
            print(f"[Error] Bright Data scrape failed: {e}. Falling back...")
            html_content = scrape_with_local_fallback(url)
            method = "Local HTTP (Fallback)"
    else:
        html_content = scrape_with_local_fallback(url)
        method = "Local HTTP"
        
    text = clean_html_to_text(html_content)
    
    # If the scraped content is empty or blocked (e.g. captcha screen), return a notice
    if not text or "enable javascript" in text.lower() or "just a moment" in text.lower() or "cloudflare" in text.lower():
        # Return empty so the Agent can generate mock/typical data if needed
        return f"__BLOCKED_OR_EMPTY__ (Method: {method})"
        
    return f"--- Content from {url} (via {method}) ---\n{text}"

def search_news_serp(query: str) -> list:
    """
    Uses Bright Data SERP API to search Google for competitor news, returns structured results.
    """
    if not BRIGHTDATA_API_KEY or not BRIGHTDATA_SERP_ZONE:
        print("[Mock SERP] Bright Data SERP credentials missing. Returning simulated results.")
        return get_mock_serp_results(query)
        
    url = "https://api.brightdata.com/request"
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&tbm=nws&hl=en&gl=us"
    
    payload = {
        "zone": BRIGHTDATA_SERP_ZONE,
        "url": search_url,
        "format": "raw"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            # If formatted correctly as JSON, parse it
            try:
                data = response.json()
                # Parse Google News result structure from Bright Data SERP JSON
                results = []
                news_results = data.get("news_results", [])
                for item in news_results[:5]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "source": item.get("source", ""),
                        "date": item.get("date", ""),
                        "snippet": item.get("snippet", "")
                    })
                return results
            except Exception:
                # If raw HTML returned, parse with BeautifulSoup
                return parse_google_news_html(response.text)
        else:
            print(f"[SERP Error] {response.status_code}: {response.text}")
            return get_mock_serp_results(query)
    except Exception as e:
        print(f"[SERP Exception] {e}")
        return get_mock_serp_results(query)

def parse_google_news_html(html_text: str) -> list:
    """
    Helper to parse raw Google News search HTML when raw format is returned.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    results = []
    # Google news typical elements
    for div in soup.select("div.g")[:5]:
        title_el = div.select_one("h3")
        link_el = div.select_one("a")
        snippet_el = div.select_one("div.VwiC3b")
        source_el = div.select_one("div.N54Bgc") or div.select_one("span.aCOpRe")
        
        if title_el and link_el:
            results.append({
                "title": title_el.get_text(),
                "link": link_el.get("href", ""),
                "source": source_el.get_text() if source_el else "Unknown",
                "date": "Recent",
                "snippet": snippet_el.get_text() if snippet_el else ""
            })
    return results

def get_mock_serp_results(query: str) -> list:
    """
    Simulates search results when SERP API is unconfigured, ensuring the app works locally.
    """
    import random
    company_name = query.replace("news pricing", "").replace("funding recruitment", "").strip()
    sources = ["TechCrunch", "VentureBeat", "Bloomberg", "Reuters", "PR Newswire", "Business Wire"]
    
    headlines = [
        f"{company_name} Launches New AI-Powered Product Module to Automate Workflows",
        f"How {company_name} is Restructuring Its Pricing Model to Drive Enterprise Adoption",
        f"Speculation Mounts Over {company_name}'s Next Strategic Expansion Following Leadership Changes",
        f"{company_name} Expands Global Team, Hiring Extensively Across AI and Engineering",
        f"Industry Analysis: Is {company_name} Outpacing Competitors in the SaaS Market?"
    ]
    
    results = []
    for i, headline in enumerate(headlines[:4]):
        results.append({
            "title": headline,
            "link": f"https://example.com/news/{company_name.lower().replace(' ', '-')}-{i}",
            "source": random.choice(sources),
            "date": f"{random.randint(1, 28)} days ago",
            "snippet": f"Recent developments indicate that {company_name} is accelerating product capabilities and scaling operations. This article covers their strategic roadmap, hiring surges, and user feedback."
        })
    return results
