import { useState, useCallback } from "react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";
import type { Job } from "@/components/JobCard";
import type { SearchFilters } from "@/components/JobSearchForm";

interface UseJobSearchResult {
  jobs: Job[];
  isLoading: boolean;
  currentPage: number;
  totalPages: number;
  totalJobs: number;
  searchJobs: (filters: SearchFilters) => Promise<void>;
  loadMore: (page: number) => Promise<void>;
  sortJobs: (sort: string) => Promise<void>;
}

const JOBS_PER_PAGE = 12;

export const useJobSearch = (): UseJobSearchResult => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);
  const [currentFilters, setCurrentFilters] = useState<SearchFilters | null>(null);
  const [currentSort, setCurrentSort] = useState("date_desc");

  const totalPages = Math.ceil(totalJobs / JOBS_PER_PAGE);

  const buildQuery = useCallback((filters: SearchFilters, page: number, sort: string) => {
    let query = supabase
      .from('jobs')
      .select('*', { count: 'exact' });

    // Apply filters
    if (filters.jobTitle) {
      query = query.ilike('title', `%${filters.jobTitle}%`);
    }
    
    if (filters.location) {
      query = query.ilike('location', `%${filters.location}%`);
    }

    // Time range filter
    const daysAgo = new Date();
    daysAgo.setDate(daysAgo.getDate() - parseInt(filters.timeRange));
    query = query.gte('posting_date', daysAgo.toISOString().split('T')[0]);

    // Apply sorting
    switch (sort) {
      case 'date_desc':
        query = query.order('posting_date', { ascending: false });
        break;
      case 'date_asc':
        query = query.order('posting_date', { ascending: true });
        break;
      case 'company':
        query = query.order('company_name', { ascending: true });
        break;
      case 'title':
        query = query.order('title', { ascending: true });
        break;
      default:
        query = query.order('posting_date', { ascending: false });
    }

    // Apply pagination
    const from = (page - 1) * JOBS_PER_PAGE;
    const to = from + JOBS_PER_PAGE - 1;
    query = query.range(from, to);

    return query;
  }, []);

  const searchJobs = useCallback(async (filters: SearchFilters) => {
    setIsLoading(true);
    setCurrentFilters(filters);
    setCurrentPage(1);

    try {
      // First, trigger scraping
      const { error: scrapeError } = await supabase.functions.invoke('scrape-jobs', {
        body: filters
      });

      if (scrapeError) {
        console.warn('Scraping failed:', scrapeError);
        // Continue with existing jobs even if scraping fails
      }

      // Then fetch existing jobs from database
      const query = buildQuery(filters, 1, currentSort);
      const { data, error, count } = await query;

      if (error) {
        throw error;
      }

      setJobs(data || []);
      setTotalJobs(count || 0);
      
      if (data && data.length > 0) {
        toast({
          title: "Search completed",
          description: `Found ${count} jobs matching your criteria`,
        });
      } else {
        toast({
          title: "No jobs found",
          description: "Try adjusting your search criteria",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Search error:', error);
      toast({
        title: "Search failed",
        description: "Please try again",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [buildQuery, currentSort]);

  const loadMore = useCallback(async (page: number) => {
    if (!currentFilters) return;

    setIsLoading(true);
    setCurrentPage(page);

    try {
      const query = buildQuery(currentFilters, page, currentSort);
      const { data, error } = await query;

      if (error) {
        throw error;
      }

      setJobs(data || []);
    } catch (error) {
      console.error('Load more error:', error);
      toast({
        title: "Failed to load jobs",
        description: "Please try again",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [currentFilters, buildQuery, currentSort]);

  const sortJobs = useCallback(async (sort: string) => {
    if (!currentFilters) return;

    setCurrentSort(sort);
    setIsLoading(true);

    try {
      const query = buildQuery(currentFilters, currentPage, sort);
      const { data, error } = await query;

      if (error) {
        throw error;
      }

      setJobs(data || []);
    } catch (error) {
      console.error('Sort error:', error);
      toast({
        title: "Failed to sort jobs",
        description: "Please try again",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [currentFilters, currentPage, buildQuery]);

  return {
    jobs,
    isLoading,
    currentPage,
    totalPages,
    totalJobs,
    searchJobs,
    loadMore,
    sortJobs,
  };
};