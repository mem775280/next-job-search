import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { Search, AlertTriangle, Download, Briefcase, MapPin, Calendar, DollarSign, Mail, ExternalLink, Loader2 } from 'lucide-react';

interface ScrapedJob {
  id: string;
  title: string;
  company: string;
  location: string;
  url: string;
  posted_date: string;
  description?: string;
  salary?: string;
  emails: string[];
  scraped_at: string;
}

interface ScrapingFilters {
  keywords: string;
  location: string;
  date_posted: string;
  experience_level?: string;
  job_type?: string;
  remote: boolean;
  salary_min?: string;
  max_jobs: number;
}

export const LinkedInScraper = () => {
  const { toast } = useToast();
  const [filters, setFilters] = useState<ScrapingFilters>({
    keywords: '',
    location: 'Pakistan',
    date_posted: '1w',
    remote: false,
    max_jobs: 50
  });
  
  const [jobs, setJobs] = useState<ScrapedJob[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [scrapingStatus, setScrapingStatus] = useState<string>('');

  const backendUrl = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  const handleFilterChange = (key: keyof ScrapingFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const scrapeJobs = async () => {
    if (!filters.keywords.trim()) {
      toast({
        title: "Error",
        description: "Please enter job keywords to search",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setScrapingStatus('Initializing scraper...');
    
    try {
      const response = await fetch(`${backendUrl}/api/linkedin/scrape-jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setJobs(result.jobs || []);
        setScrapingStatus('');
        
        toast({
          title: "Scraping Completed",
          description: `Successfully found ${result.total_found} jobs matching your criteria`,
        });
      } else {
        setScrapingStatus('');
        toast({
          title: "Scraping Failed",
          description: result.message || "Failed to scrape jobs",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Scraping error:', error);
      setScrapingStatus('');
      toast({
        title: "Connection Error",
        description: "Failed to connect to scraping service",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const exportToCSV = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/linkedin/jobs/export-csv`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `linkedin_jobs_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        toast({
          title: "Export Successful",
          description: "Job data exported to CSV file",
        });
      } else {
        toast({
          title: "Export Failed",
          description: "Failed to export job data",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: "Export Error",
        description: "Failed to download CSV file",
        variant: "destructive",
      });
    }
  };

  const clearJobs = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/linkedin/jobs`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setJobs([]);
        toast({
          title: "Jobs Cleared",
          description: "All scraped jobs have been removed",
        });
      } else {
        toast({
          title: "Clear Failed",
          description: "Failed to clear job data",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Clear error:', error);
      toast({
        title: "Clear Error",
        description: "Failed to clear jobs",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Warning Alert */}
      <Alert className="border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20">
        <AlertTriangle className="h-4 w-4 text-yellow-600" />
        <AlertTitle className="text-yellow-800 dark:text-yellow-200">Enterprise-Grade LinkedIn Scraper</AlertTitle>
        <AlertDescription className="text-yellow-700 dark:text-yellow-300">
          <strong>Professional job scraping with advanced anti-detection features:</strong>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Manual authentication with session persistence</li>
            <li>Enterprise-grade stealth technology</li>
            <li>Comprehensive data extraction including emails</li>
            <li>Advanced filtering and CSV export capabilities</li>
            <li>Respects rate limiting and human-like behavior</li>
          </ul>
        </AlertDescription>
      </Alert>

      {/* Scraping Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Advanced LinkedIn Job Scraper
          </CardTitle>
          <CardDescription>
            Scrape LinkedIn jobs with comprehensive filtering and data extraction
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Primary Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Job Keywords *</label>
              <Input
                placeholder="e.g., 'data analyst', 'software engineer'"
                value={filters.keywords}
                onChange={(e) => handleFilterChange('keywords', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Location</label>
              <Input
                placeholder="e.g., 'Pakistan', 'Karachi', 'Remote'"
                value={filters.location}
                onChange={(e) => handleFilterChange('location', e.target.value)}
              />
            </div>
          </div>

          {/* Advanced Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Date Posted</label>
              <Select value={filters.date_posted} onValueChange={(value) => handleFilterChange('date_posted', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="24h">Past 24 hours</SelectItem>
                  <SelectItem value="3d">Past 3 days</SelectItem>
                  <SelectItem value="1w">Past week</SelectItem>
                  <SelectItem value="2w">Past 2 weeks</SelectItem>
                  <SelectItem value="1m">Past month</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Experience Level</label>
              <Select value={filters.experience_level || ''} onValueChange={(value) => handleFilterChange('experience_level', value || undefined)}>
                <SelectTrigger>
                  <SelectValue placeholder="Any level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Any level</SelectItem>
                  <SelectItem value="internship">Internship</SelectItem>
                  <SelectItem value="entry">Entry level</SelectItem>
                  <SelectItem value="associate">Associate</SelectItem>
                  <SelectItem value="mid">Mid-Senior</SelectItem>
                  <SelectItem value="director">Director</SelectItem>
                  <SelectItem value="executive">Executive</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Job Type</label>
              <Select value={filters.job_type || ''} onValueChange={(value) => handleFilterChange('job_type', value || undefined)}>
                <SelectTrigger>
                  <SelectValue placeholder="Any type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Any type</SelectItem>
                  <SelectItem value="full-time">Full-time</SelectItem>
                  <SelectItem value="part-time">Part-time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                  <SelectItem value="temporary">Temporary</SelectItem>
                  <SelectItem value="volunteer">Volunteer</SelectItem>
                  <SelectItem value="internship">Internship</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Max Jobs</label>
              <Input
                type="number"
                min="1"
                max="200"
                value={filters.max_jobs}
                onChange={(e) => handleFilterChange('max_jobs', parseInt(e.target.value) || 50)}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-4">
            <Button 
              onClick={scrapeJobs} 
              disabled={isLoading}
              className="flex-1"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Scraping...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Start Scraping
                </>
              )}
            </Button>
            
            {jobs.length > 0 && (
              <>
                <Button onClick={exportToCSV} variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
                <Button onClick={clearJobs} variant="outline">
                  Clear Jobs
                </Button>
              </>
            )}
          </div>

          {/* Scraping Status */}
          {scrapingStatus && (
            <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p className="text-sm text-blue-700 dark:text-blue-300">{scrapingStatus}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Section */}
      {jobs.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold">Scraped Jobs ({jobs.length} found)</h3>
            <Badge variant="secondary" className="px-3 py-1">
              <Briefcase className="h-3 w-3 mr-1" />
              Latest Results
            </Badge>
          </div>

          <div className="grid gap-4">
            {jobs.map((job) => (
              <Card key={job.id} className="w-full hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg font-semibold text-primary">
                        {job.title}
                      </CardTitle>
                      <CardDescription className="text-base font-medium mt-1">
                        <div className="flex items-center gap-4 flex-wrap">
                          <span className="flex items-center gap-1">
                            <Briefcase className="h-4 w-4" />
                            {job.company}
                          </span>
                          <span className="flex items-center gap-1">
                            <MapPin className="h-4 w-4" />
                            {job.location}
                          </span>
                          {job.posted_date && job.posted_date !== 'N/A' && (
                            <span className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {new Date(job.posted_date).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </CardDescription>
                    </div>
                    <div className="flex flex-col gap-2 ml-4">
                      {job.salary && job.salary !== 'N/A' && (
                        <Badge variant="secondary" className="flex items-center gap-1">
                          <DollarSign className="h-3 w-3" />
                          {job.salary}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-3">
                  {/* Job Description */}
                  {job.description && job.description !== 'N/A' && (
                    <div className="space-y-1">
                      <h4 className="text-sm font-medium">Description:</h4>
                      <p className="text-sm text-muted-foreground line-clamp-3">
                        {job.description}
                      </p>
                    </div>
                  )}

                  {/* Extracted Emails */}
                  {job.emails && job.emails.length > 0 && (
                    <div className="space-y-1">
                      <h4 className="text-sm font-medium flex items-center gap-1">
                        <Mail className="h-4 w-4" />
                        Contact Emails:
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {job.emails.map((email, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {email}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Job Link */}
                  {job.url && job.url !== 'N/A' && (
                    <div className="pt-2">
                      <a 
                        href={job.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm underline"
                      >
                        <ExternalLink className="h-3 w-3" />
                        View on LinkedIn
                      </a>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* No Results State */}
      {!isLoading && jobs.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Briefcase className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No Jobs Scraped Yet</h3>
            <p className="text-muted-foreground">
              Enter your search criteria and click "Start Scraping" to find LinkedIn jobs
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};