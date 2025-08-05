#!/usr/bin/env python3
"""
Simple Playwright test to check browser initialization
"""
import asyncio
import os
from playwright.async_api import async_playwright

async def test_browser():
    """Test basic browser initialization"""
    try:
        # Set browser path
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/pw-browsers'
        
        playwright = await async_playwright().start()
        
        # Try to launch browser with minimal args
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--headless=new'
            ]
        )
        
        print("✅ Browser launched successfully")
        
        # Create context
        context = await browser.new_context()
        print("✅ Context created successfully")
        
        # Create page
        page = await context.new_page()
        print("✅ Page created successfully")
        
        # Navigate to a simple page
        await page.goto('https://www.google.com')
        print("✅ Navigation successful")
        
        title = await page.title()
        print(f"✅ Page title: {title}")
        
        # Cleanup
        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()
        
        print("✅ All tests passed - Playwright is working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_browser())
    exit(0 if result else 1)