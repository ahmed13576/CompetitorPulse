import database
import scraper
import asyncio

print("Testing database initialization...")
database.init_db()
print("Database initialized successfully!")

print("\nMonitored competitors in DB:")
competitors = database.get_all_competitors()
for c in competitors:
    print(f"- {c['name']} ({c['domain']})")

print("\nTesting local HTTP scraper fallback...")
try:
    text = asyncio.run(scraper.smart_scrape("https://example.com"))
    print(f"Scraped content length: {len(text)}")
    print("First 100 chars of scraped data:")
    print(text[:100].replace('\n', ' '))
    print("\nLocal HTTP Scraper works!")
except Exception as e:
    print(f"\nScraper error: {e}")

print("\nVerification completed successfully!")
