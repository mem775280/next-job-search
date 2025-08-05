import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Building2, MapPin, Calendar, ExternalLink } from "lucide-react";

export interface Job {
  id: string;
  title: string;
  company_name: string;
  location: string;
  job_description: string | null;
  posting_date: string;
  job_url: string;
  created_at: string;
}

interface JobCardProps {
  job: Job;
}

export const JobCard = ({ job }: JobCardProps) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  const truncateDescription = (text: string | null, maxLength: number = 150) => {
    if (!text) return "No description available";
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
  };

  return (
    <Card className="h-full hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold line-clamp-2">
            {job.title}
          </CardTitle>
          <Badge variant="secondary" className="ml-2 shrink-0">
            {formatDate(job.posting_date)}
          </Badge>
        </div>
        
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Building2 className="h-4 w-4" />
          <span className="font-medium">{job.company_name}</span>
        </div>
        
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <MapPin className="h-4 w-4" />
          <span>{job.location}</span>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
          {truncateDescription(job.job_description)}
        </p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            <span>Found {formatDate(job.created_at)}</span>
          </div>
          
          <Button 
            size="sm" 
            onClick={() => window.open(job.job_url, '_blank')}
            className="gap-2"
          >
            <ExternalLink className="h-4 w-4" />
            View Job
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};