#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Website Scraping Test Script

This script tests if https://ilovememphisblog.com/weekend can be scraped
from your local computer. If this works but Anvil's servers fail, it means
the website is blocking Anvil's server IP addresses.

Usage:
    python test_scraping_local.py

Requirements:
    pip install requests beautifulsoup4
"""

import sys
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def test_basic_scraping():
    """Test basic HTTP request to the website"""
    url = "https://ilovememphisblog.com/weekend"
    
    print("="*70)
    print("TESTING WEBSITE SCRAPING FROM YOUR LOCAL COMPUTER")
    print("="*70)
    print(f"\nTarget URL: {url}")
    print(f"Testing at: {datetime.now()}\n")
    
    try:
        print("Step 1: Making HTTP GET request...")
        response = requests.get(url, timeout=30)
        
        print(f"  ✅ Response Status: {response.status_code}")
        print(f"  ✅ Content Length: {len(response.text)} characters")
        print(f"  ✅ Content Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Website is accessible from your computer.\n")
            
            # Save raw HTML for inspection
            with open('scraped_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"  💾 Saved raw HTML to: scraped_page.html")
            
            # Try to parse events
            print("\nStep 2: Parsing HTML content...")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Save prettified HTML
            with open('scraped_page_pretty.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f"  💾 Saved formatted HTML to: scraped_page_pretty.html")
            
            # Extract text content
            text = soup.get_text()
            clean_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            
            with open('scraped_text.txt', 'w', encoding='utf-8') as f:
                f.write(clean_text)
            print(f"  💾 Saved text content to: scraped_text.txt")
            
            # Look for event indicators
            print("\nStep 3: Analyzing content...")
            event_indicators = {
                'Friday mentions': clean_text.lower().count('friday'),
                'Saturday mentions': clean_text.lower().count('saturday'),
                'Sunday mentions': clean_text.lower().count('sunday'),
                'Time patterns (PM/AM)': len([l for l in clean_text.split('\n') if 'pm' in l.lower() or 'am' in l.lower()]),
                'Cost indicators ($)': clean_text.count('$'),
                'Free mentions': clean_text.lower().count('free')
            }
            
            print("\n  Event Indicators Found:")
            for indicator, count in event_indicators.items():
                print(f"    • {indicator}: {count}")
            
            # Try to find event-like sections
            print("\nStep 4: Detecting possible events...")
            lines = clean_text.split('\n')
            
            possible_events = []
            for line in lines:
                # Look for lines that might be event titles
                # (20-100 chars, contains letters, not common nav words)
                if (20 < len(line) < 100 and 
                    not any(word in line.lower() for word in ['advertisement', 'subscribe', 'newsletter', 'follow us', 'copyright'])):
                    
                    # Check if it has time or date info nearby
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['friday', 'saturday', 'sunday', 'pm', 'am', '$', 'free']):
                        possible_events.append(line)
            
            print(f"  Found {len(possible_events)} possible event lines")
            if possible_events:
                print("\n  Sample possible events:")
                for event in possible_events[:10]:
                    print(f"    • {event[:80]}...")
            
            # Save possible events
            with open('possible_events.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(possible_events))
            print(f"\n  💾 Saved possible events to: possible_events.txt")
            
            # Final summary
            print("\n" + "="*70)
            print("SUMMARY")
            print("="*70)
            print(f"✅ Website is accessible from your local computer")
            print(f"✅ Downloaded {len(response.text)} characters")
            print(f"✅ Found {len(possible_events)} potential event entries")
            print("\nConclusion:")
            if len(possible_events) > 10:
                print("  ✅ Website has scrapable content!")
                print("  ✅ Direct scraping should work from Anvil too")
                print("\nIf Anvil scraping fails but this works:")
                print("  → Website is blocking Anvil's server IPs")
                print("  → Solution: Use a proxy or different scraping service")
            else:
                print("  ⚠️ Didn't find many events - might need better parsing")
                print("  → Check the saved HTML/text files")
                print("  → Adjust parsing logic based on actual structure")
            
            print("\nFiles Created:")
            print("  • scraped_page.html - Raw HTML from website")
            print("  • scraped_page_pretty.html - Formatted HTML")
            print("  • scraped_text.txt - Extracted text")
            print("  • possible_events.txt - Potential event lines")
            print("\n" + "="*70 + "\n")
            
            return True
            
        else:
            print(f"\n❌ ERROR: Got status code {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out")
        print("  → Website might be slow or blocking requests")
        return False
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ ERROR: Connection failed")
        print(f"  → {str(e)}")
        print("  → Website might be down or blocking your IP")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_with_headers():
    """Test with different user agent headers"""
    url = "https://ilovememphisblog.com/weekend"
    
    print("\n" + "="*70)
    print("TESTING WITH DIFFERENT USER AGENTS")
    print("="*70)
    
    user_agents = [
        ('Chrome/Windows', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
        ('Firefox/Mac', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'),
        ('Mobile Safari', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'),
    ]
    
    for name, user_agent in user_agents:
        print(f"\nTrying with {name}:")
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"  ✅ Status: {response.status_code}, Length: {len(response.text)}")
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")


def compare_with_firecrawl():
    """Compare local scraping with what Anvil/Firecrawl might see"""
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    print("\n📊 What This Test Reveals:")
    print("\n1. If local scraping WORKS:")
    print("   ✅ Website is accessible")
    print("   ✅ Content is scrapable")
    print("   → If Anvil fails but this works:")
    print("      = Website blocks Anvil's server IPs")
    print("      = Solution: Use proxy or different approach")
    
    print("\n2. If local scraping FAILS:")
    print("   ⚠️ Website has anti-scraping protection")
    print("   ⚠️ Might require JavaScript rendering")
    print("   → Solution: Use service with JS rendering")
    
    print("\n3. Firecrawl Error Analysis:")
    print("   Error: 'URL must have a valid top-level domain'")
    print("   → This is a Firecrawl API validation error")
    print("   → NOT a website blocking issue")
    print("   → Your Firecrawl plan might not allow this URL")
    print("   → Or Firecrawl v2 has strict URL validation")
    
    print("\n💡 Recommendation:")
    print("   → Use direct scraping from Anvil (already implemented!)")
    print("   → Skip Firecrawl API (not needed)")
    print("   → Direct scraper is simpler, faster, and free")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("I LOVE MEMPHIS BLOG - WEBSITE SCRAPING TEST")
    print("="*70)
    print("\nThis script will test if ilovememphisblog.com/weekend")
    print("can be scraped from your local computer.\n")
    
    # Test basic scraping
    success = test_basic_scraping()
    
    if success:
        # Test with different user agents
        test_with_headers()
    
    # Show diagnostic summary
    compare_with_firecrawl()
    
    print("\nNext Steps:")
    if success:
        print("  1. Check the saved files (scraped_page.html, scraped_text.txt)")
        print("  2. Review possible_events.txt to see what was detected")
        print("  3. The direct scraper in Anvil should work the same way")
        print("  4. Push code to GitHub and test in Anvil")
    else:
        print("  1. Check your internet connection")
        print("  2. Try visiting the website in your browser")
        print("  3. The website might be temporarily down")
    
    print("\n" + "="*70)
    print("Test complete! Check the files created in this directory.")
    print("="*70 + "\n")

