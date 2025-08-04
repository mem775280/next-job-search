import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface SearchFilters {
  jobTitle: string;
  location: string;
  timeRange: string;
}

interface ScrapedJob {
  title: string;
  company_name: string;
  location: string;
  job_description: string;
  posting_date: string;
  job_url: string;
}

Deno.serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    );

    const { jobTitle, location, timeRange }: SearchFilters = await req.json();
    
    console.log(`Starting job scraping for: ${jobTitle} in ${location} (${timeRange} days)`);

    // Mock job data - In a real implementation, you would scrape LinkedIn here
    // Due to anti-scraping measures, this simulates realistic job data
    const mockJobs: ScrapedJob[] = generateMockJobs(jobTitle, location, parseInt(timeRange));

    console.log(`Generated ${mockJobs.length} mock jobs`);

    // Insert jobs into database, avoiding duplicates
    let insertedCount = 0;
    let duplicateCount = 0;

    for (const job of mockJobs) {
      try {
        const { error } = await supabase
          .from('jobs')
          .insert({
            title: job.title,
            company_name: job.company_name,
            location: job.location,
            job_description: job.job_description,
            posting_date: job.posting_date,
            job_url: job.job_url
          });

        if (error) {
          if (error.code === '23505') { // Unique constraint violation
            duplicateCount++;
          } else {
            console.error('Insert error:', error);
          }
        } else {
          insertedCount++;
        }
      } catch (error) {
        console.error('Error inserting job:', error);
      }
    }

    console.log(`Inserted ${insertedCount} new jobs, ${duplicateCount} duplicates skipped`);

    return new Response(
      JSON.stringify({
        success: true,
        inserted: insertedCount,
        duplicates: duplicateCount,
        total: mockJobs.length
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    );

  } catch (error) {
    console.error('Scraping error:', error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      }
    );
  }
});

function generateMockJobs(jobTitle: string, location: string, timeRange: number): ScrapedJob[] {
  const companies = [
    'TechCorp', 'DataFlow Inc', 'Analytics Pro', 'CloudTech', 'InnovateLab',
    'Digital Solutions', 'SmartData Co', 'FutureTech', 'DataDriven LLC', 'TechVision'
  ];

  const jobTitleVariations = [
    jobTitle,
    `Senior ${jobTitle}`,
    `Junior ${jobTitle}`,
    `Lead ${jobTitle}`,
    `${jobTitle} Specialist`,
    `${jobTitle} Manager`,
    `${jobTitle} Consultant`
  ];

  const jobs: ScrapedJob[] = [];
  const jobCount = Math.floor(Math.random() * 15) + 5; // 5-20 jobs

  for (let i = 0; i < jobCount; i++) {
    const daysAgo = Math.floor(Math.random() * timeRange);
    const postingDate = new Date();
    postingDate.setDate(postingDate.getDate() - daysAgo);

    const company = companies[Math.floor(Math.random() * companies.length)];
    const title = jobTitleVariations[Math.floor(Math.random() * jobTitleVariations.length)];
    
    jobs.push({
      title,
      company_name: company,
      location,
      job_description: generateJobDescription(title, company),
      posting_date: postingDate.toISOString().split('T')[0],
      job_url: `https://linkedin.com/jobs/view/${Math.floor(Math.random() * 9000000000) + 1000000000}`
    });
  }

  return jobs;
}

function generateJobDescription(title: string, company: string): string {
  const descriptions = [
    `Join ${company} as a ${title}! We're looking for a passionate professional to drive data-driven insights and support our growing business. You'll work with cutting-edge tools and collaborate with cross-functional teams.`,
    `Exciting opportunity at ${company}! As a ${title}, you'll be responsible for analyzing complex datasets, creating actionable recommendations, and presenting findings to stakeholders. Competitive salary and benefits included.`,
    `${company} is seeking a talented ${title} to join our dynamic team. You'll work on challenging projects, utilize advanced analytics tools, and contribute to strategic decision-making processes.`,
    `We're hiring a ${title} at ${company}! This role offers the chance to work with big data, machine learning algorithms, and business intelligence platforms. Remote work options available.`,
    `Join our innovative team at ${company} as a ${title}. You'll be at the forefront of data analysis, helping drive business growth through insights and recommendations. Excellent growth opportunities.`
  ];
  
  return descriptions[Math.floor(Math.random() * descriptions.length)];
}