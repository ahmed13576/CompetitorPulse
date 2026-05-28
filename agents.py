import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from scraper import smart_scrape, search_news_serp
import database

load_dotenv()

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    # If no key in environment, we will check Streamlit secrets or raise warning
    print("Warning: GEMINI_API_KEY is not set in environment variables.")

class CompetitorIntelligenceSystem:
    def __init__(self):
        # We use gemini-1.5-flash as default because it is fast, highly capable, and cost-efficient
        self.model_name = "gemini-1.5-flash"
        
    def _get_model(self):
        return genai.GenerativeModel(self.model_name)
        
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
        
        model = self._get_model()
        try:
            extractor_response = model.generate_content(extractor_prompt)
            structured_data = extractor_response.text
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
            analyst_response = model.generate_content(analyst_prompt)
            analysis_output = analyst_response.text
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
            strategist_response = model.generate_content(strategist_prompt)
            battlecard_md = strategist_response.text
        except Exception as e:
            battlecard_md = f"Error running Strategist Agent: {e}"
            
        # Get brief summary for database storage
        summary_prompt = f"Summarize this sales battlecard in a 2-sentence executive summary:\n{battlecard_md}"
        try:
            summary = model.generate_content(summary_prompt).text
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
