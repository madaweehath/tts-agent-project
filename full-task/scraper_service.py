# scraper_service.py
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_alriyadh_news():
    """Scrape news from AlRiyadh RSS feed"""
    return [
    {
        'title': "شخصية مُلهِمة",
        'description_fusha': "في بعض الأحيان.",
        'date': "Sun, 23 Nov 2025 00:16:15 +0300",
        'source': "AlRiyadh",
        'scraped_time': "2025-11-23T19:29:44.504955"
    },
    {
        'title': "مجرد كلام في سكة التايهين",
        'description_fusha': "هكذا بدون ألقاب تسبقه",
        'date': "Sun, 23 Nov 2025 00:20:23 +0300",
        'source': "AlRiyadh",
        'scraped_time': "2025-11-23T19:29:44.520892"
    }
    ]
    # try:
    #     print("📡 Fetching news from AlRiyadh...")
    #     url = "https://www.alriyadh.com/section.columns.xml"
    #     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    #     response = requests.get(url, headers=headers, verify=False, timeout=10)
    #     response.raise_for_status()
        
    #     root = ET.fromstring(response.content)
    #     news_data = []
        
    #     for item in root.findall('.//item'):
    #         try:
    #             # Extract title
    #             title_elem = item.find('title')
    #             title_text = title_elem.text if title_elem is not None else "No title"
    #             if title_text and title_text.startswith('<![CDATA['):
    #                 title_text = title_text[9:-3]
                
    #             # Extract description
    #             description_elem = item.find('description')
    #             description_text = description_elem.text if description_elem is not None else ""
    #             if description_text and description_text.startswith('<![CDATA['):
    #                 description_text = description_text[9:-3]
                
    #             # Extract date
    #             pub_date_elem = item.find('pubDate')
    #             pub_date_text = pub_date_elem.text if pub_date_elem is not None else ""
                
    #             # Clean HTML
    #             if description_text and "<" in description_text:
    #                 soup = BeautifulSoup(description_text, 'html.parser')
    #                 description_text = soup.get_text()
                
    #             description_text = re.sub(r'\s+', ' ', description_text if description_text else "").strip()
                
    #             # Only include substantial articles
    #             if description_text and len(description_text) > 50:
    #                 news_data.append({
    #                     'title': title_text.strip() if title_text else "",
    #                     'description_fusha': description_text,
    #                     'date': pub_date_text,
    #                     'source': 'AlRiyadh',
    #                     'scraped_time': datetime.now().isoformat()
    #                 })
    #         except Exception as e:
    #             print(f"⚠️  Error processing item: {e}")
    #             continue
        
    #     print(f"✓ Successfully scraped {len(news_data)} articles")
    #     return news_data
        
    # except Exception as e:
    #     print(f"❌ Error scraping news: {e}")
    #     return []