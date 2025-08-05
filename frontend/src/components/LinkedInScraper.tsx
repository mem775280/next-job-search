import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { supabase } from '@/integrations/supabase/client';
import { Search, AlertTriangle, Heart, MessageCircle, Briefcase } from 'lucide-react';

interface ScrapedJob {
  title: string;
  company: string;
  location: string;
  url: string;
  description?: string;
  postedDate?: string;
}

export const LinkedInScraper = () => {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('Pakistan');
  const [jobs, setJobs] = useState<ScrapedJob[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const scrapeJobs = async () => {
    if (!searchQuery.trim()) {
      toast({
        title: "Error",
        description: "Please enter a search query",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke('linkedin-scraper', {
        body: { 
          searchQuery: searchQuery.trim(),
          location: location.trim()
        }
      });

      if (error) throw error;

      setJobs(data.jobs || []);
      
      if (data.warning) {
        toast({
          title: "🚨 Critical Warning",
          description: data.warning,
          variant: "destructive",
          duration: 15000,
        });
      }

      if (data.risks) {
        console.warn('LinkedIn Scraping Risks:', data.risks);
      }

    } catch (error) {
      console.error('Scraping error:', error);
      toast({
        title: "Scraping Failed",
        description: "LinkedIn likely blocked the request. This is expected behavior.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Alert className="border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20">
        <AlertTriangle className="h-4 w-4 text-yellow-600" />
        <AlertTitle className="text-yellow-800 dark:text-yellow-200">Legal & Technical Warning</AlertTitle>
        <AlertDescription className="text-yellow-700 dark:text-yellow-300">
          <strong>LinkedIn scraping violates their Terms of Service and will result in account suspension.</strong>
          <br />This demo shows simulated data only. For production use:
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Use LinkedIn's official API (limited access)</li>
            <li>Check company RSS feeds</li>
            <li>Use public job boards</li>
            <li>Consider manual content curation</li>
          </ul>
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            LinkedIn Job Scraper (⚠️ REAL SCRAPING)
          </CardTitle>
          <CardDescription>
            Real LinkedIn job scraping with browser automation - VIOLATES ToS!
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter job title (e.g., 'data analyst')"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && scrapeJobs()}
            />
            <Input
              placeholder="Location (e.g., 'Pakistan')"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="max-w-48"
            />
            <Button onClick={scrapeJobs} disabled={isLoading}>
              {isLoading ? 'Scraping...' : 'Scrape Jobs'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {jobs.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Scraped Jobs ({jobs.length} found)</h3>
          {jobs.map((job, index) => (
            <Card key={index} className="w-full">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base">{job.title}</CardTitle>
                    <CardDescription className="text-sm font-medium">
                      {job.company} • {job.location}
                    </CardDescription>
                    {job.postedDate && (
                      <CardDescription className="text-xs">
                        Posted: {job.postedDate}
                      </CardDescription>
                    )}
                  </div>
                  <Badge variant="secondary" className="flex items-center gap-1">
                    <Briefcase className="h-3 w-3" />
                    Job
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {job.description && (
                  <p className="text-sm text-muted-foreground">{job.description}</p>
                )}
                {job.url && (
                  <a 
                    href={job.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm underline"
                  >
                    View Job on LinkedIn
                  </a>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};