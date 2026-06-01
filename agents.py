import os
import json
import time
from dotenv import load_dotenv
from scraper import smart_scrape, search_news_serp
import database

load_dotenv()

# ---------------------------------------------------------------------------
# LLM Provider Abstraction
# ---------------------------------------------------------------------------

GEMINI_FALLBACK_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
]

GROQ_FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
]


def _call_with_retry(call_fn, models: list[str], max_retries: int = 3) -> str:
    """Try each model in order; retry with backoff on rate-limit errors."""
    last_error = None
    for model_name in models:
        for attempt in range(max_retries):
            try:
                return call_fn(model_name)
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "rate_limit" in err_str.lower():
                    wait = min(2 ** attempt * 15, 60)
                    print(f"[Rate-limited on {model_name}] Retry {attempt+1}/{max_retries} in {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        print(f"[Quota exhausted for {model_name}] Falling back to next model...")
    raise RuntimeError(f"All models exhausted. Last error: {last_error}")


class CompetitorIntelligenceSystem:
    """Multi-provider LLM system supporting Gemini and Groq."""

    def __init__(self, provider: str = "gemini"):
        self.provider = provider.lower()

        if self.provider == "groq":
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY", "")
            if not api_key:
                raise ValueError("GROQ_API_KEY is not set. Get one free at https://console.groq.com")
            self.groq_client = Groq(api_key=api_key)
            self.models = list(GROQ_FALLBACK_MODELS)
        else:
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY", "")
            if not api_key:
                print("Warning: GEMINI_API_KEY is not set.")
            self.gemini_client = genai.Client(api_key=api_key)
            self.models = list(GEMINI_FALLBACK_MODELS)

    # ---- internal generators per provider ----

    def _gemini_call(self, prompt: str, model: str) -> str:
        response = self.gemini_client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text

    def _groq_call(self, prompt: str, model: str) -> str:
        response = self.groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096,
        )
        return response.choices[0].message.content

    # ---- public interface ----

    def _generate(self, prompt: str) -> str:
        if self.provider == "groq":
            return _call_with_retry(lambda m: self._groq_call(prompt, m), self.models)
        else:
            return _call_with_retry(lambda m: self._gemini_call(prompt, m), self.models)

    async def run_analysis(self, competitor_id: int, competitor_name: str, domain: str, progress_callback=None) -> dict:
        """
        Executes the autonomous agentic pipeline:
        1. Crawls pricing, careers, and homepage.
        2. Gathers news via SERP.
        3. Agent 1 (Data Extractor): Cleans, parses and structures the raw data.
        4. Agent 2 (Market Analyst): Synthesizes trends, strategic shifts, and compares with history.
        5. Agent 3 (Sales Strategist): Generates the markdown Battlecard.
        """
        # Formulate typical URLs
        clean_domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
        base_url = f"https://{clean_domain}"
        pricing_url = f"{base_url}/pricing"
        careers_url = f"{base_url}/careers"
        if "stripe" in clean_domain:
            careers_url = "https://www.stripe.com/jobs"
        
        # --- PHASE 1: DATA COLLECTION ---
        if progress_callback:
            progress_callback(10, "Scraping homepage and positioning...")
        homepage_raw = await smart_scrape(base_url)
        
        if progress_callback:
            progress_callback(25, "Scraping pricing packages...")
        pricing_raw = await smart_scrape(pricing_url)
        
        if progress_callback:
            progress_callback(40, "Scraping careers page for hiring signals...")
        careers_raw = await smart_scrape(careers_url)
        
        if progress_callback:
            progress_callback(55, "Querying SERP API for news and PR...")
        news_data = search_news_serp(f"{competitor_name} news launch pricing funding")
        news_summary = json.dumps(news_data, indent=2)
        
        # Save raw scrapes to database
        database.save_scrape(competitor_id, base_url, "homepage", homepage_raw, homepage_raw[:5000])
        database.save_scrape(competitor_id, pricing_url, "pricing", pricing_raw, pricing_raw[:5000])
        database.save_scrape(competitor_id, careers_url, "careers", careers_raw, careers_raw[:5000])
        database.save_scrape(competitor_id, "Google News Query", "news", news_summary, news_summary)

        # --- PHASE 2: AGENT 1 - DATA EXTRACTOR & CLEANER ---
        if progress_callback:
            progress_callback(70, "Running Data Extractor Agent...")
            
        extractor_prompt = f"""
        You are the 'Lead Web Intelligence Crawler' Agent.
        Your job is to examine raw text scraped from {competitor_name}'s website and structure it.
        
        Below are the raw scrapes collected from the web:
        
        --- HOMEPAGE TEXT ---
        {homepage_raw[:8000]}
        
        --- PRICING PAGE TEXT ---
        {pricing_raw[:8000]}
        
        --- CAREERS PAGE TEXT ---
        {careers_raw[:8000]}
        
        --- RECENT NEWS & PR ---
        {news_summary}
        
        Instructions:
        1. Clean up garbage text, headers, cookies notices, etc.
        2. Extract and summarize:
           - Company Positioning (What do they claim to do?)
           - Pricing Model & Tiers (Include actual prices, plans, features if visible)
           - Hiring Signals (What kinds of jobs are they hiring for? e.g., AI Engineers, Enterprise Sales)
           - Recent News Events (Summarize the news links provided)
        3. If any section was BLOCKED or EMPTY, use your general knowledge of {competitor_name} to generate high-fidelity, typical data for them, but add a note '(Estimated based on market knowledge)'.
        
        Provide your output as a clean structured Markdown report.
        """
        
        try:
            structured_data = self._generate(extractor_prompt)
        except Exception as e:
            structured_data = f"Error running Extractor Agent: {e}\nRaw fallback data will be processed."
            
        # --- PHASE 3: AGENT 2 - COMPETITIVE ANALYST ---
        if progress_callback:
            progress_callback(80, "Running Market Analyst Agent...")
            
        # Fetch previous analysis for change detection
        previous_analysis = database.get_latest_analysis(competitor_id)
        change_context = ""
        if previous_analysis:
            change_context = f"""
            Here is the PREVIOUS analysis we conducted on {competitor_name} in the past:
            --- PREVIOUS BATTLECARD ---
            {previous_analysis['battlecard_md']}
            ---------------------------
            Compare the current structured data with this previous report and identify what has changed (e.g. pricing changes, new jobs added, new positioning, new products announced).
            """
        else:
            change_context = "This is our first scan of this competitor. No historical baseline exists yet."

        analyst_prompt = f"""
        You are the 'Competitive Intelligence Analyst' Agent.
        Your job is to analyze the structured data collected about {competitor_name} and extract strategic trends and intelligence.
        
        Here is the current structured intelligence report from the Web Crawler Agent:
        {structured_data}
        
        {change_context}
        
        Analyze this information and answer these questions:
        1. What are {competitor_name}'s core strengths based on their positioning and recent news?
        2. What are their potential weaknesses (e.g., gaps in features, pricing models, negative news)?
        3. What is their strategic direction? (Look at what jobs they are hiring for. E.g., hiring LLM/AI researchers implies they are planning an AI expansion; hiring Enterprise Account Executives implies a push to enterprise sales).
        4. If there were changes since the last scan, highlight them explicitly in a "What Changed" section.
        
        Output your analysis in a structured format.
        """
        
        try:
            analysis_output = self._generate(analyst_prompt)
        except Exception as e:
            analysis_output = f"Error running Analyst Agent: {e}"

        # --- PHASE 4: AGENT 3 - SALES STRATEGIST ---
        if progress_callback:
            progress_callback(90, "Running Sales Strategist Agent...")
            
        strategist_prompt = f"""
        You are the 'Head of Sales Enablement' Agent.
        Your job is to take raw competitive intelligence and turn it into a highly actionable **Sales Battlecard** that sales reps can use in client pitches when they encounter {competitor_name}.
        
        Here is the detailed analyst report:
        {analysis_output}
        
        Here is the crawler's structured product data:
        {structured_data}
        
        Generate a professional markdown **Sales Battlecard** with the following sections:
        1. **Company Overview & Positioning Quick-Take** (1-2 sentences)
        2. **Pricing & Packaging Reference** (Quick bullet list of plans)
        3. **How We Win (Our Strengths vs. Them)** (3 key battleground points)
        4. **Where We Lose (Their Strengths/Objections)** (Gaps we need to handle)
        5. **Objection Handling Scripts (Verbatim scripts for sales reps)**
           - E.g., Customer: "But {competitor_name} is cheaper." Rep script: "..."
           - E.g., Customer: "They have feature X." Rep script: "..."
        6. **Strategic Warning Signals** (Key signals to watch: e.g. their hiring activity, new launches)
        
        Format the Battlecard beautifully with clear Markdown headers, bold text, and clean lists. Make it look professional, readable, and direct. Do not include introductory conversational filler.
        """
        
        try:
            battlecard_md = self._generate(strategist_prompt)
        except Exception as e:
            battlecard_md = f"Error running Strategist Agent: {e}"
            
        # Get brief summary for database storage
        summary_prompt = f"Summarize this sales battlecard in a 2-sentence executive summary:\n{battlecard_md}"
        try:
            summary = self._generate(summary_prompt)
        except Exception:
            summary = f"Competitive Battlecard for {competitor_name}."

        # Save final reports to database
        database.save_analysis(competitor_id, f"Battlecard: {competitor_name}", summary, battlecard_md)
        
        if progress_callback:
            progress_callback(100, "Analysis complete!")
            
        return {
            "status": "success",
            "competitor_name": competitor_name,
            "domain": domain,
            "battlecard": battlecard_md,
            "summary": summary,
            "crawled_data": structured_data,
            "analyst_data": analysis_output
        }
