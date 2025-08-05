import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/components/ui/use-toast';
import { LogIn, LogOut, User, CheckCircle, AlertTriangle } from 'lucide-react';

interface UserInfo {
  name: string;
  logged_in: boolean;
}

interface AuthState {
  isLoggedIn: boolean;
  user: UserInfo | null;
  loading: boolean;
}

export const LinkedInAuth = () => {
  const { toast } = useToast();
  const [authState, setAuthState] = useState<AuthState>({
    isLoggedIn: false,
    user: null,
    loading: true
  });

  const backendUrl = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));

      const response = await fetch(`${backendUrl}/api/linkedin/auth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'check_status' }),
      });

      const result = await response.json();

      if (result.success) {
        setAuthState({
          isLoggedIn: result.logged_in,
          user: result.user || null,
          loading: false
        });
      } else {
        setAuthState({
          isLoggedIn: false,
          user: null,
          loading: false
        });
      }
    } catch (error) {
      console.error('Auth status check failed:', error);
      setAuthState({
        isLoggedIn: false,
        user: null,
        loading: false
      });
      toast({
        title: "Connection Error",
        description: "Failed to check authentication status",
        variant: "destructive",
      });
    }
  };

  const signInWithLinkedIn = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));

      const response = await fetch(`${backendUrl}/api/linkedin/auth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'login' }),
      });

      const result = await response.json();

      if (result.success) {
        setAuthState({
          isLoggedIn: true,
          user: result.user || null,
          loading: false
        });

        toast({
          title: "Login Successful",
          description: result.message,
        });
      } else {
        setAuthState(prev => ({ ...prev, loading: false }));
        toast({
          title: "Login Failed",
          description: result.message,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Login failed:', error);
      setAuthState(prev => ({ ...prev, loading: false }));
      toast({
        title: "Login Error",
        description: "Failed to connect to authentication service",
        variant: "destructive",
      });
    }
  };

  const signOut = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));

      const response = await fetch(`${backendUrl}/api/linkedin/auth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'logout' }),
      });

      const result = await response.json();

      if (result.success) {
        setAuthState({
          isLoggedIn: false,
          user: null,
          loading: false
        });

        toast({
          title: "Logout Successful",
          description: result.message,
        });
      } else {
        setAuthState(prev => ({ ...prev, loading: false }));
        toast({
          title: "Logout Failed",
          description: result.message,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Logout failed:', error);
      setAuthState(prev => ({ ...prev, loading: false }));
      toast({
        title: "Logout Error",
        description: "Failed to logout",
        variant: "destructive",
      });
    }
  };

  if (authState.loading) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <span className="ml-2">Checking authentication...</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Login Instructions Alert */}
      <Alert className="border-blue-500 bg-blue-50 dark:bg-blue-950/20">
        <AlertTriangle className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-700 dark:text-blue-300">
          <strong>Manual Login Required:</strong> When you click "Sign in with LinkedIn", 
          a browser window will open. Please log in manually with your LinkedIn credentials. 
          Your session will be saved for future use.
        </AlertDescription>
      </Alert>

      <Card className="w-full max-w-md mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <LogIn className="h-5 w-5" />
            LinkedIn Authentication
          </CardTitle>
          <CardDescription>
            {authState.isLoggedIn 
              ? 'You are connected to LinkedIn with saved session' 
              : 'Connect your LinkedIn account to scrape job posts'
            }
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {authState.isLoggedIn ? (
            <div className="space-y-4">
              {/* User Info Display */}
              <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-200 dark:border-green-800">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="text-sm font-medium text-green-800 dark:text-green-200">
                      Connected as: {authState.user?.name || 'LinkedIn User'}
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400">
                      Session active - ready to scrape jobs
                    </p>
                  </div>
                </div>
              </div>

              {/* User Actions */}
              <div className="flex gap-2">
                <Button 
                  onClick={checkAuthStatus} 
                  variant="outline" 
                  size="sm"
                  className="flex-1"
                >
                  <User className="h-4 w-4 mr-2" />
                  Refresh Status
                </Button>
                <Button 
                  onClick={signOut} 
                  variant="outline" 
                  size="sm"
                  className="flex-1"
                  disabled={authState.loading}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <Button 
                onClick={signInWithLinkedIn} 
                className="w-full"
                disabled={authState.loading}
              >
                <LogIn className="h-4 w-4 mr-2" />
                {authState.loading ? 'Connecting...' : 'Sign in with LinkedIn'}
              </Button>
              
              <div className="text-xs text-muted-foreground text-center">
                Your LinkedIn credentials are handled securely through the browser.
                We don't store your LinkedIn password.
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};