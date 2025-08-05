#!/usr/bin/env python3
"""
Test LinkedIn scraper browser initialization with simplified args
"""
import asyncio
import os
from playwright.async_api import async_playwright

async def test_scraper_browser():
    """Test browser initialization with scraper-like configuration"""
    try:
        # Set browser path
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/pw-browsers'
        
        playwright = await async_playwright().start()
        
        # Test with full scraper args
        browser_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--no-first-run',
            '--disable-default-apps',
            '--disable-infobars',
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--window-size=1366,768',
            '--headless=new',
            '--virtual-time-budget=5000',
            '--run-all-compositor-stages-before-draw',
            '--disable-background-tasks'
        ]
        
        print("Testing with full scraper browser args...")
        browser = await playwright.chromium.launch(
            headless=True,
            args=browser_args,
            timeout=60000
        )
        
        print("✅ Browser launched successfully with scraper args")
        
        # Create context with anti-detection settings
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            java_script_enabled=True,
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }
        )
        
        print("✅ Context created successfully with anti-detection settings")
        
        # Create page
        page = await context.new_page()
        print("✅ Page created successfully")
        
        # Test navigation to LinkedIn
        await page.goto('https://www.linkedin.com', timeout=30000)
        print("✅ LinkedIn navigation successful")
        
        title = await page.title()
        print(f"✅ Page title: {title}")
        
        # Cleanup
        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()
        
        print("✅ All tests passed - Scraper browser configuration is working")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_scraper_browser())
    exit(0 if result else 1)