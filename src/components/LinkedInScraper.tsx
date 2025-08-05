import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { supabase } from '@/integrations/supabase/client';
import { Search, AlertTriangle, Heart, MessageCircle, Briefcase } from 'lucide-react';

interface LinkedInPost {
  id: string;
  author: string;
  content: string;
  timestamp: string;
  likes: number;
  comments: number;
  isJobPost: boolean;
  url: string;
}

export const LinkedInScraper = () => {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [posts, setPosts] = useState<LinkedInPost[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const scrapePosts = async () => {
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
        body: { searchQuery: searchQuery.trim() }
      });

      if (error) throw error;

      setPosts(data.posts || []);
      
      if (data.warning) {
        toast({
          title: "Important Warning",
          description: data.warning,
          variant: "destructive",
          duration: 10000,
        });
      }

    } catch (error) {
      console.error('Scraping error:', error);
      toast({
        title: "Error",
        description: "Failed to scrape LinkedIn posts",
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
            LinkedIn Post Search (Demo)
          </CardTitle>
          <CardDescription>
            Search for posts and job listings (showing simulated data only)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter search keywords (e.g., 'software engineer jobs')"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && scrapePosts()}
            />
            <Button onClick={scrapePosts} disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Search'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {posts.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Search Results ({posts.length} posts)</h3>
          {posts.map((post) => (
            <Card key={post.id} className="w-full">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base">{post.author}</CardTitle>
                    <CardDescription>
                      {new Date(post.timestamp).toLocaleDateString()}
                    </CardDescription>
                  </div>
                  {post.isJobPost && (
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Briefcase className="h-3 w-3" />
                      Job Post
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="whitespace-pre-wrap text-sm">{post.content}</p>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Heart className="h-4 w-4" />
                    {post.likes} likes
                  </div>
                  <div className="flex items-center gap-1">
                    <MessageCircle className="h-4 w-4" />
                    {post.comments} comments
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};