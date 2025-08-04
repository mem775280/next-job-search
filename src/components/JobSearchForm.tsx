import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, MapPin, Calendar } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface JobSearchFormProps {
  onSearch: (filters: SearchFilters) => void;
  isLoading: boolean;
}

export interface SearchFilters {
  jobTitle: string;
  location: string;
  timeRange: string;
}

export const JobSearchForm = ({ onSearch, isLoading }: JobSearchFormProps) => {
  const [jobTitle, setJobTitle] = useState("");
  const [location, setLocation] = useState("");
  const [timeRange, setTimeRange] = useState("7");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({ jobTitle, location, timeRange });
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-center flex items-center justify-center gap-2">
          <Search className="h-6 w-6" />
          Find Your Next Job
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Job Title</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="e.g. Data Analyst"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="pl-10"
                  required
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Location</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="City, Country"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="pl-10"
                  required
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Posted Within</label>
              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger>
                  <Calendar className="h-4 w-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Past 24 hours</SelectItem>
                  <SelectItem value="3">Past 3 days</SelectItem>
                  <SelectItem value="7">Past week</SelectItem>
                  <SelectItem value="14">Past 2 weeks</SelectItem>
                  <SelectItem value="30">Past month</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading}
          >
            {isLoading ? "Searching..." : "Search Jobs"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};