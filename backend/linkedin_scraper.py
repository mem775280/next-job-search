"""
Enterprise-grade LinkedIn Job Scraper with Advanced Anti-Detection
"""
import asyncio
import random
import time
import re
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LinkedInScraperConfig:
    """Configuration for LinkedIn scraper with enterprise-grade stealth"""
    
    # Anti-detection settings
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    VIEWPORTS = [
        {"width": 1366, "height": 768},
        {"width": 1920, "height": 1080},
        {"width": 1440, "height": 900},
        {"width": 1536, "height": 864},
    ]
    
    # Timing settings (randomized delays)
    MIN_DELAY = 2
    MAX_DELAY = 5
    SCROLL_DELAY = (1, 3)
    PAGE_LOAD_TIMEOUT = 30000
    
    # LinkedIn URLs
    BASE_URL = "https://www.linkedin.com"
    LOGIN_URL = f"{BASE_URL}/login"
    JOBS_SEARCH_BASE = f"{BASE_URL}/jobs/search"

class LinkedInScraper:
    """Enterprise-grade LinkedIn job scraper with advanced anti-detection"""
    
    def __init__(self, session_data_dir: str = "/tmp/linkedin_sessions"):
        self.config = LinkedInScraperConfig()
        self.session_data_dir = Path(session_data_dir)
        self.session_data_dir.mkdir(exist_ok=True)
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        
        # Anti-detection features
        self.ua = UserAgent()
        self.current_user_agent = random.choice(self.config.USER_AGENTS)
        self.current_viewport = random.choice(self.config.VIEWPORTS)
        
    async def init_browser(self, headless: bool = True):
        """Initialize Playwright browser with stealth settings"""
        try:
            # Set browser path if specified
            import os
            browsers_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
            if browsers_path:
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
                
            playwright = await async_playwright().start()
            
            # Launch browser with stealth settings
            self.browser = await playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-dev-shm-usage',
                    '--disable-extensions',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-infobars',
                    '--window-size=1366,768',
                    '--start-maximized'
                ]
            )
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            # For testing purposes, set browser to None and handle gracefully
            self.browser = None
            raise e
        
        # Create context with anti-detection settings
        self.context = await self.browser.new_context(
            user_agent=self.current_user_agent,
            viewport=self.current_viewport,
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        # Add stealth scripts
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            window.chrome = {
                runtime: {},
            };
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)
        
        self.page = await self.context.new_page()
        
        # Set additional stealth properties
        await self.page.evaluate("""
            () => {
                delete navigator.__proto__.webdriver;
                navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        Promise.resolve({ state: 'granted' })
                );
            }
        """)
        
    async def human_like_delay(self, min_delay: float = None, max_delay: float = None):
        """Add human-like random delays"""
        min_d = min_delay or self.config.MIN_DELAY
        max_d = max_delay or self.config.MAX_DELAY
        delay = random.uniform(min_d, max_d)
        await asyncio.sleep(delay)
        
    async def human_like_scroll(self, scrolls: int = 3):
        """Perform human-like scrolling"""
        for _ in range(scrolls):
            # Random scroll amounts
            scroll_amount = random.randint(300, 800)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await self.human_like_delay(*self.config.SCROLL_DELAY)
            
    async def check_login_status(self) -> bool:
        """Check if user is logged into LinkedIn"""
        try:
            if not self.page:
                logger.warning("Browser page not initialized")
                return False
                
            await self.page.goto(self.config.BASE_URL, wait_until='networkidle')
            await self.human_like_delay()
            
            # Check for login indicators
            login_indicators = [
                'nav[aria-label="Primary navigation"]',
                '.global-nav__me',
                '[data-test-id="nav-me-dropdown"]'
            ]
            
            for indicator in login_indicators:
                element = await self.page.query_selector(indicator)
                if element:
                    self.is_logged_in = True
                    return True
                    
            self.is_logged_in = False
            return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    async def wait_for_manual_login(self) -> Dict[str, Any]:
        """Handle manual login process"""
        try:
            if not self.page:
                return {
                    "success": False,
                    "message": "Browser not initialized. Please ensure Playwright browsers are installed."
                }
                
            # Navigate to login page
            await self.page.goto(self.config.LOGIN_URL, wait_until='networkidle')
            await self.human_like_delay()
            
            logger.info("Please log in manually in the browser window...")
            
            # Wait for successful login by monitoring URL changes and page elements
            login_successful = False
            timeout = 300  # 5 minutes timeout
            start_time = time.time()
            
            while not login_successful and (time.time() - start_time) < timeout:
                current_url = self.page.url
                
                # Check if we're redirected from login page
                if '/login' not in current_url or await self.check_login_status():
                    login_successful = True
                    self.is_logged_in = True
                    break
                
                await asyncio.sleep(2)
            
            if login_successful:
                # Save session data for future use
                await self.save_session()
                return {
                    "success": True,
                    "message": "Login successful! Session saved for future use.",
                    "user_info": await self.get_user_info()
                }
            else:
                return {
                    "success": False,
                    "message": "Login timeout. Please try again."
                }
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {
                "success": False,
                "message": f"Login failed: {str(e)}"
            }
    
    async def save_session(self):
        """Save browser session for future use"""
        try:
            session_file = self.session_data_dir / "session_cookies.json"
            cookies = await self.context.cookies()
            
            with open(session_file, 'w') as f:
                json.dump(cookies, f, indent=2)
                
            logger.info("Session saved successfully")
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    async def load_session(self) -> bool:
        """Load saved session"""
        try:
            session_file = self.session_data_dir / "session_cookies.json"
            
            if not session_file.exists():
                return False
                
            with open(session_file, 'r') as f:
                cookies = json.load(f)
            
            await self.context.add_cookies(cookies)
            
            # Verify session is still valid
            if await self.check_login_status():
                self.is_logged_in = True
                logger.info("Session loaded successfully")
                return True
            else:
                logger.info("Saved session is expired")
                return False
                
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False
    
    async def get_user_info(self) -> Dict[str, str]:
        """Get basic user information"""
        try:
            if not self.page:
                return {"name": "Unknown User", "logged_in": False, "error": "Browser not initialized"}
                
            await self.page.goto(f"{self.config.BASE_URL}/in/me/", wait_until='networkidle')
            
            name = await self.page.text_content('h1')
            
            return {
                "name": name.strip() if name else "Unknown User",
                "logged_in": True
            }
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {"name": "Unknown User", "logged_in": self.is_logged_in}
    
    async def logout(self) -> Dict[str, Any]:
        """Logout from LinkedIn"""
        try:
            if not self.is_logged_in:
                return {"success": True, "message": "Already logged out"}
            
            await self.page.goto(self.config.BASE_URL)
            
            # Click on profile menu
            profile_button = await self.page.query_selector('.global-nav__me')
            if profile_button:
                await profile_button.click()
                await self.human_like_delay()
                
                # Click logout
                logout_link = await self.page.query_selector('a[href*="/logout"]')
                if logout_link:
                    await logout_link.click()
                    await self.human_like_delay(3, 5)
            
            # Clear saved session
            session_file = self.session_data_dir / "session_cookies.json"
            if session_file.exists():
                session_file.unlink()
            
            self.is_logged_in = False
            
            return {"success": True, "message": "Logged out successfully"}
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {"success": False, "message": f"Logout failed: {str(e)}"}
    
    async def build_search_url(self, filters: Dict[str, Any]) -> str:
        """Build LinkedIn job search URL with filters"""
        params = {}
        
        # Keywords
        if filters.get('keywords'):
            params['keywords'] = filters['keywords']
        
        # Location
        if filters.get('location'):
            params['location'] = filters['location']
        
        # Date posted filter
        if filters.get('date_posted'):
            date_map = {
                '24h': 'r86400',
                '3d': 'r259200', 
                '1w': 'r604800',
                '2w': 'r1209600',
                '1m': 'r2592000'
            }
            if filters['date_posted'] in date_map:
                params['f_TPR'] = date_map[filters['date_posted']]
        
        # Experience level
        if filters.get('experience_level'):
            exp_map = {
                'internship': '1',
                'entry': '2',
                'associate': '3', 
                'mid': '4',
                'director': '5',
                'executive': '6'
            }
            if filters['experience_level'] in exp_map:
                params['f_E'] = exp_map[filters['experience_level']]
        
        # Job type
        if filters.get('job_type'):
            type_map = {
                'full-time': 'F',
                'part-time': 'P',
                'contract': 'C',
                'temporary': 'T',
                'volunteer': 'V',
                'internship': 'I'
            }
            if filters['job_type'] in type_map:
                params['f_JT'] = type_map[filters['job_type']]
        
        # Remote work
        if filters.get('remote'):
            params['f_WT'] = '2'  # Remote jobs
        
        # Salary range (if provided)
        if filters.get('salary_min'):
            params['f_SB2'] = filters['salary_min']
        
        query_string = urlencode(params)
        return f"{self.config.JOBS_SEARCH_BASE}?{query_string}"
    
    async def extract_job_data(self, job_element) -> Optional[Dict[str, Any]]:
        """Extract comprehensive job data from job element"""
        try:
            job_data = {}
            
            # Job title
            title_element = await job_element.query_selector('[data-test-id="job-title"]')
            if not title_element:
                title_element = await job_element.query_selector('h3 a, .job-search-card__title a')
            job_data['title'] = await title_element.text_content() if title_element else 'N/A'
            
            # Company name
            company_element = await job_element.query_selector('[data-test-id="job-search-card-subtitle"] a')
            if not company_element:
                company_element = await job_element.query_selector('.job-search-card__subtitle a')
            job_data['company'] = await company_element.text_content() if company_element else 'N/A'
            
            # Location
            location_element = await job_element.query_selector('.job-search-card__location')
            job_data['location'] = await location_element.text_content() if location_element else 'N/A'
            
            # Job URL
            link_element = await job_element.query_selector('h3 a, .job-search-card__title a')
            job_data['url'] = await link_element.get_attribute('href') if link_element else 'N/A'
            if job_data['url'] and not job_data['url'].startswith('http'):
                job_data['url'] = self.config.BASE_URL + job_data['url']
            
            # Posted date
            date_element = await job_element.query_selector('time')
            job_data['posted_date'] = await date_element.get_attribute('datetime') if date_element else 'N/A'
            
            # Try to get more details by clicking on job
            try:
                if link_element:
                    await link_element.click()
                    await self.human_like_delay(2, 4)
                    
                    # Job description
                    desc_element = await self.page.query_selector('.jobs-search__job-details--container')
                    if desc_element:
                        description = await desc_element.text_content()
                        job_data['description'] = description.strip()[:500] if description else 'N/A'
                        
                        # Extract emails from description
                        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                        emails = re.findall(email_pattern, description) if description else []
                        job_data['emails'] = list(set(emails))
                    
                    # Salary information
                    salary_element = await self.page.query_selector('.jobs-details__salary-main-rail')
                    if salary_element:
                        salary_text = await salary_element.text_content()
                        job_data['salary'] = salary_text.strip() if salary_text else 'N/A'
                    else:
                        job_data['salary'] = 'N/A'
                    
                    # Go back to search results
                    await self.page.go_back()
                    await self.human_like_delay(1, 2)
                    
            except Exception as detail_error:
                logger.warning(f"Error extracting job details: {detail_error}")
                job_data['description'] = 'N/A'
                job_data['emails'] = []
                job_data['salary'] = 'N/A'
            
            # Clean up the data
            for key, value in job_data.items():
                if isinstance(value, str):
                    job_data[key] = value.strip()
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    async def scrape_jobs(self, filters: Dict[str, Any], max_jobs: int = 50) -> Dict[str, Any]:
        """Main job scraping method"""
        try:
            if not self.is_logged_in:
                return {
                    "success": False,
                    "message": "Please login first",
                    "jobs": []
                }
            
            # Build search URL
            search_url = await self.build_search_url(filters)
            logger.info(f"Searching jobs: {search_url}")
            
            # Navigate to search page
            await self.page.goto(search_url, wait_until='networkidle')
            await self.human_like_delay(3, 5)
            
            jobs = []
            page_num = 1
            
            while len(jobs) < max_jobs:
                # Check if we have job results
                job_elements = await self.page.query_selector_all('.job-search-card')
                
                if not job_elements:
                    logger.info("No job elements found")
                    break
                
                logger.info(f"Found {len(job_elements)} jobs on page {page_num}")
                
                # Extract job data
                for job_element in job_elements:
                    if len(jobs) >= max_jobs:
                        break
                    
                    job_data = await self.extract_job_data(job_element)
                    if job_data:
                        jobs.append(job_data)
                        logger.info(f"Extracted job: {job_data['title']} at {job_data['company']}")
                    
                    await self.human_like_delay(0.5, 1.5)
                
                # Try to go to next page
                next_button = await self.page.query_selector('button[aria-label="Next"]')
                if next_button and await next_button.is_enabled():
                    await next_button.click()
                    await self.human_like_delay(3, 5)
                    page_num += 1
                else:
                    logger.info("No more pages available")
                    break
            
            return {
                "success": True,
                "message": f"Successfully scraped {len(jobs)} jobs",
                "jobs": jobs,
                "total_found": len(jobs)
            }
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return {
                "success": False,
                "message": f"Scraping failed: {str(e)}",
                "jobs": []
            }
    
    async def close(self):
        """Clean up resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

# Global scraper instance (singleton pattern)
_scraper_instance: Optional[LinkedInScraper] = None

async def get_scraper_instance() -> LinkedInScraper:
    """Get or create scraper instance"""
    global _scraper_instance
    
    if _scraper_instance is None:
        _scraper_instance = LinkedInScraper()
        try:
            await _scraper_instance.init_browser(headless=False)  # Set to False for manual login
        except Exception as e:
            logger.error(f"Failed to initialize scraper browser: {e}")
            # For testing, we'll still return the instance but it won't be functional
            pass
    
    return _scraper_instance

async def cleanup_scraper():
    """Cleanup scraper instance"""
    global _scraper_instance
    
    if _scraper_instance:
        await _scraper_instance.close()
        _scraper_instance = None