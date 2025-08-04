-- Create jobs table for storing scraped job listings
CREATE TABLE public.jobs (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  company_name TEXT NOT NULL,
  location TEXT NOT NULL,
  job_description TEXT,
  posting_date DATE NOT NULL,
  job_url TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- Create policy for public read access (no authentication required for job search)
CREATE POLICY "Jobs are publicly readable" 
ON public.jobs 
FOR SELECT 
USING (true);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER update_jobs_updated_at
BEFORE UPDATE ON public.jobs
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Create index on job_url for faster duplicate checking
CREATE INDEX idx_jobs_url ON public.jobs(job_url);

-- Create indexes for search performance
CREATE INDEX idx_jobs_title ON public.jobs(title);
CREATE INDEX idx_jobs_location ON public.jobs(location);
CREATE INDEX idx_jobs_posting_date ON public.jobs(posting_date DESC);