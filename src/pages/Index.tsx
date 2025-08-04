import React from "react";
import { JobSearchForm } from "@/components/JobSearchForm";
import { JobResults } from "@/components/JobResults";
import { useJobSearch } from "@/hooks/useJobSearch";

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
        
        <div className="mb-8">
          <JobSearchForm onSearch={searchJobs} isLoading={isLoading} />
        </div>
        
        <JobResults
          jobs={jobs}
          isLoading={isLoading}
          currentPage={currentPage}
          totalPages={totalPages}
          totalJobs={totalJobs}
          onPageChange={loadMore}
          onSortChange={sortJobs}
        />
      </div>
    </div>
  );
};

export default Index;
