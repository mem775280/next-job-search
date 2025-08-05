#!/usr/bin/env python3
"""
Test fixed LinkedIn scraper browser initialization
"""
import asyncio
import os
from playwright.async_api import async_playwright

async def test_fixed_scraper_browser():
    """Test browser initialization with fixed configuration"""
    try:
        # Set browser path
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/pw-browsers'
        
        playwright = await async_playwright().start()
        
        # Test with fixed scraper args
        browser_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
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
            '--window-size=1366,768',
            '--headless=new',
            '--disable-background-tasks'
        ]
        
        print("Testing with fixed scraper browser args...")
        browser = await playwright.chromium.launch(
            headless=True,
            args=browser_args,
            timeout=60000
        )
        
        print("✅ Browser launched successfully with fixed args")
        
        # Create context
        context = await browser.new_context()
        print("✅ Context created successfully")
        
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
        
        print("✅ All tests passed - Fixed scraper browser configuration is working")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_fixed_scraper_browser())
    exit(0 if result else 1)