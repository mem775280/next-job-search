#!/usr/bin/env python3
"""
Specific test for browser initialization and dependency verification
Tests the reported issues with soupsieve and Playwright browser installation
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / 'backend'))

async def test_browser_initialization():
    """Test browser initialization and dependencies"""
    print("=" * 80)
    print("BROWSER INITIALIZATION AND DEPENDENCY TEST")
    print("=" * 80)
    
    # Test 1: Import dependencies
    print("🔍 Testing dependency imports...")
    try:
        from bs4 import BeautifulSoup
        import soupsieve
        print("✅ BeautifulSoup and soupsieve imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import BeautifulSoup/soupsieve: {e}")
        return False
    
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Playwright: {e}")
        return False
    
    # Test 2: Test soupsieve CSS selectors with BeautifulSoup
    print("\n🔍 Testing soupsieve CSS selector functionality...")
    try:
        html = """
        <html>
            <body>
                <div class="job-card">
                    <h3 class="job-title">Software Engineer</h3>
                    <span class="company">Tech Corp</span>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Test CSS selectors that would be used in LinkedIn scraping
        job_cards = soup.select('.job-card')
        job_titles = soup.select('.job-title')
        companies = soup.select('.company')
        
        if len(job_cards) == 1 and len(job_titles) == 1 and len(companies) == 1:
            print("✅ soupsieve CSS selectors working correctly")
        else:
            print("❌ soupsieve CSS selectors not working as expected")
            return False
            
    except Exception as e:
        print(f"❌ soupsieve CSS selector test failed: {e}")
        return False
    
    # Test 3: Browser initialization
    print("\n🔍 Testing Playwright browser initialization...")
    try:
        from linkedin_scraper import LinkedInScraper
        
        scraper = LinkedInScraper()
        await scraper.init_browser(headless=True)
        
        if scraper.browser and scraper.context:
            print("✅ Browser and context initialized successfully")
            
            # Test basic page navigation
            page = await scraper.context.new_page()
            await page.goto('data:text/html,<html><body><h1>Test Page</h1></body></html>')
            title = await page.title()
            
            if title == "":  # Data URLs don't have titles, but page should load
                print("✅ Basic page navigation working")
            
            await page.close()
            await scraper.context.close()
            await scraper.browser.close()
            
        else:
            print("❌ Browser or context initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Browser initialization failed: {e}")
        return False
    
    # Test 4: Check Playwright browsers installation
    print("\n🔍 Checking Playwright browsers installation...")
    try:
        browsers_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '/pw-browsers')
        print(f"Browsers path: {browsers_path}")
        
        if os.path.exists(browsers_path):
            print("✅ Playwright browsers directory exists")
            
            # Check for chromium
            chromium_paths = [
                os.path.join(browsers_path, 'chromium-*'),
                '/pw-browsers/chromium-*'
            ]
            
            import glob
            chromium_found = False
            for pattern in chromium_paths:
                if glob.glob(pattern):
                    chromium_found = True
                    break
            
            if chromium_found:
                print("✅ Chromium browser found")
            else:
                print("⚠️  Chromium browser directory not found, but browser initialization worked")
                
        else:
            print("⚠️  Browsers directory not found, but browser initialization worked")
            
    except Exception as e:
        print(f"⚠️  Browser path check failed: {e}, but browser initialization worked")
    
    print("\n" + "=" * 80)
    print("✅ ALL DEPENDENCY AND BROWSER TESTS PASSED")
    print("✅ soupsieve dependency is working correctly")
    print("✅ Playwright browsers are properly installed and functional")
    print("=" * 80)
    
    return True

async def main():
    """Main test function"""
    success = await test_browser_initialization()
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))