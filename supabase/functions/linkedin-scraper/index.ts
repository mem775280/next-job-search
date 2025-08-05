import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { launch } from 'https://deno.land/x/puppeteer@16.2.0/mod.ts';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface ScrapedJob {
  title: string;
  company: string;
  location: string;
  url: string;
  description?: string;
  postedDate?: string;
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { searchQuery, location = 'Pakistan' } = await req.json();
    
    console.log(`⚠️  ATTEMPTING LINKEDIN SCRAPING - HIGH RISK OPERATION`);
    console.log(`Search: ${searchQuery}, Location: ${location}`);
    
    // ⚠️ WARNING: This violates LinkedIn ToS and will likely get blocked/banned
    const browser = await launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      ]
    });

    const page = await browser.newPage();
    
    // Set viewport and headers to appear more human-like
    await page.setViewport({ width: 1366, height: 768 });
    await page.setExtraHTTPHeaders({
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    });

    // Construct LinkedIn jobs search URL
    const encodedQuery = encodeURIComponent(searchQuery);
    const encodedLocation = encodeURIComponent(location);
    const searchUrl = `https://www.linkedin.com/jobs/search/?keywords=${encodedQuery}&location=${encodedLocation}&f_TPR=r604800&position=1&pageNum=0`;
    
    console.log(`Navigating to: ${searchUrl}`);
    
    try {
      // Navigate to LinkedIn jobs page
      await page.goto(searchUrl, { 
        waitUntil: 'networkidle2',
        timeout: 30000 
      });

      // Wait for job cards to load
      await page.waitForSelector('.job-search-card', { timeout: 15000 });
      
      // Scroll to load more jobs
      console.log('Scrolling to load more jobs...');
      for (let i = 0; i < 3; i++) {
        await page.evaluate(() => {
          window.scrollTo(0, document.body.scrollHeight);
        });
        await page.waitForTimeout(2000);
      }

      // Extract job data
      const jobs = await page.evaluate(() => {
        const jobCards = document.querySelectorAll('.job-search-card');
        const extractedJobs: any[] = [];

        jobCards.forEach((card, index) => {
          if (index >= 10) return; // Limit to prevent long execution

          try {
            const titleElement = card.querySelector('.base-search-card__title');
            const companyElement = card.querySelector('.base-search-card__subtitle');
            const locationElement = card.querySelector('.job-search-card__location');
            const linkElement = card.querySelector('a.base-card__full-link');
            const dateElement = card.querySelector('.job-search-card__listdate');

            const job = {
              title: titleElement?.textContent?.trim() || 'N/A',
              company: companyElement?.textContent?.trim() || 'N/A',
              location: locationElement?.textContent?.trim() || 'N/A',
              url: linkElement?.href || '',
              postedDate: dateElement?.textContent?.trim() || dateElement?.getAttribute('datetime') || 'N/A'
            };

            if (job.title !== 'N/A' && job.company !== 'N/A') {
              extractedJobs.push(job);
            }
          } catch (err) {
            console.error('Error extracting job:', err);
          }
        });

        return extractedJobs;
      });

      await browser.close();

      console.log(`Successfully scraped ${jobs.length} jobs`);

      // Return results with serious warnings
      return new Response(
        JSON.stringify({
          success: true,
          jobs: jobs,
          warning: '🚨 CRITICAL WARNING: This scraping violates LinkedIn ToS and will likely result in account suspension!',
          risks: [
            'LinkedIn actively detects and blocks automated access',
            'Your IP and account will likely be banned',
            'Violates LinkedIn Terms of Service',
            'Legal action possible from LinkedIn',
            'This method will stop working soon due to anti-bot measures'
          ],
          count: jobs.length,
          searchQuery,
          location
        }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200,
        }
      );

    } catch (scrapeError) {
      await browser.close();
      console.error('Scraping failed (likely blocked by LinkedIn):', scrapeError);
      
      return new Response(
        JSON.stringify({
          success: false,
          error: 'LinkedIn blocked the scraping attempt',
          message: 'This is expected - LinkedIn actively blocks automated access',
          recommendations: [
            'Use LinkedIn Official API (limited but legal)',
            'Try job aggregator APIs (Indeed, Glassdoor)',
            'Use RSS feeds from company career pages',
            'Consider paid scraping services (still risky)',
            'Manual data collection'
          ]
        }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200,
        }
      );
    }

  } catch (error) {
    console.error('Edge function error:', error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
        warning: 'LinkedIn scraping is extremely difficult and risky'
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      }
    );
  }
});