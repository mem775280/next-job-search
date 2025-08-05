import React from "react";
import { JobSearchForm } from "@/components/JobSearchForm";
import { JobResults } from "@/components/JobResults";
import { LinkedInAuth } from "@/components/LinkedInAuth";
import { LinkedInScraper } from "@/components/LinkedInScraper";
import { useJobSearch } from "@/hooks/useJobSearch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Index = () => {
  const { 
    jobs, 
    isLoading, 
    currentPage, 
    totalPages, 
    totalJobs,
    searchJobs, 
    loadMore, 
    sortJobs 
  } = useJobSearch();

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-center mb-2">Job Search Engine</h1>
          <p className="text-xl text-muted-foreground text-center">
            Find your next opportunity with our AI-powered job search
          </p>
        </div>
        
        <Tabs defaultValue="search" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="search">Job Search</TabsTrigger>
            <TabsTrigger value="linkedin">LinkedIn Scraper</TabsTrigger>
          </TabsList>
          
          <TabsContent value="search" className="space-y-8">
            <JobSearchForm onSearch={searchJobs} isLoading={isLoading} />
            <JobResults
              jobs={jobs}
              isLoading={isLoading}
              currentPage={currentPage}
              totalPages={totalPages}
              totalJobs={totalJobs}
              onPageChange={loadMore}
              onSortChange={sortJobs}
            />
          </TabsContent>
          
          <TabsContent value="linkedin" className="space-y-8">
            <LinkedInAuth />
            <LinkedInScraper />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Index;
