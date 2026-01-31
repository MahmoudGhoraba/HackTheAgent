import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Alert from '@/components/Alert';
import LoadingSpinner from '@/components/LoadingSpinner';
import api from '@/lib/api';

interface AuthStatus {
  authenticated: boolean;
  email?: string;
}

interface GmailProfile {
  email: string;
  messages_total: number;
  threads_total: number;
  history_id: string;
}

interface GmailEmail {
  id: string;
  thread_id: string;
  subject: string;
  from: string;
  to: string;
  date: string;
  snippet: string;
  labels: string[];
}

export default function GmailOAuthPage() {
  const router = useRouter();
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [profile, setProfile] = useState<GmailProfile | null>(null);
  const [emails, setEmails] = useState<GmailEmail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [maxResults, setMaxResults] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    checkAuthStatus();
    
    // Handle OAuth callback
    const { code, state } = router.query;
    if (code && typeof code === 'string') {
      handleOAuthCallback(code, state as string);
    }
  }, [router.query]);

  const checkAuthStatus = async () => {
    try {
      const response = await api.get('/oauth/gmail/status');
      setAuthStatus(response.data);
      
      if (response.data.authenticated) {
        fetchProfile();
      }
    } catch (err: any) {
      console.error('Error checking auth status:', err);
    }
  };

  const handleOAuthCallback = async (code: string, state?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      await api.post('/oauth/gmail/callback', { code, state });
      setSuccess('Successfully authenticated with Gmail!');
      await checkAuthStatus();
      
      // Clear URL parameters
      router.replace('/gmail-oauth', undefined, { shallow: true });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to complete OAuth flow');
    } finally {
      setLoading(false);
    }
  };

  const startOAuthFlow = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/oauth/gmail/authorize');
      const { authorization_url } = response.data;
      
      // Redirect to Google OAuth
      window.location.href = authorization_url;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start OAuth flow');
      setLoading(false);
    }
  };

  const fetchProfile = async () => {
    try {
      const response = await api.get('/gmail/profile');
      setProfile(response.data);
    } catch (err: any) {
      console.error('Error fetching profile:', err);
    }
  };

  const fetchEmails = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/gmail/fetch', {
        max_results: maxResults,
        query: searchQuery
      });
      
      setEmails(response.data.emails);
      setSuccess(`Fetched ${response.data.count} emails successfully!`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch emails');
    } finally {
      setLoading(false);
    }
  };

  const revokeAccess = async () => {
    if (!confirm('Are you sure you want to revoke Gmail access?')) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await api.delete('/oauth/gmail/revoke');
      setSuccess('Gmail access revoked successfully');
      setAuthStatus(null);
      setProfile(null);
      setEmails([]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to revoke access');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gmail OAuth Integration</h1>
          <p className="mt-2 text-gray-600">
            Connect your Gmail account to fetch and analyze emails
          </p>
        </div>

        {error && (
          <Alert type="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert type="success" onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        {/* Authentication Status */}
        <Card>
          <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
          
          {authStatus === null ? (
            <LoadingSpinner />
          ) : authStatus.authenticated ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-green-700 font-medium">Connected</span>
              </div>
              
              {authStatus.email && (
                <p className="text-gray-600">
                  Authenticated as: <span className="font-medium">{authStatus.email}</span>
                </p>
              )}
              
              {profile && (
                <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                  <h3 className="font-semibold text-gray-900">Account Information</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Total Messages:</span>
                      <span className="ml-2 font-medium">{profile.messages_total.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Total Threads:</span>
                      <span className="ml-2 font-medium">{profile.threads_total.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              )}
              
              <Button
                onClick={revokeAccess}
                variant="secondary"
                disabled={loading}
              >
                Revoke Access
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-red-700 font-medium">Not Connected</span>
              </div>
              
              <p className="text-gray-600">
                Connect your Gmail account to start fetching emails
              </p>
              
              <Button
                onClick={startOAuthFlow}
                disabled={loading}
              >
                {loading ? 'Connecting...' : 'Connect Gmail Account'}
              </Button>
            </div>
          )}
        </Card>

        {/* Fetch Emails */}
        {authStatus?.authenticated && (
          <Card>
            <h2 className="text-xl font-semibold mb-4">Fetch Emails</h2>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Results
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="500"
                    value={maxResults}
                    onChange={(e) => setMaxResults(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Search Query (optional)
                  </label>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="e.g., is:unread, from:example@gmail.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              
              <Button
                onClick={fetchEmails}
                disabled={loading}
              >
                {loading ? 'Fetching...' : 'Fetch Emails'}
              </Button>
            </div>
          </Card>
        )}

        {/* Email List */}
        {emails.length > 0 && (
          <Card>
            <h2 className="text-xl font-semibold mb-4">
              Fetched Emails ({emails.length})
            </h2>
            
            <div className="space-y-3">
              {emails.map((email) => (
                <div
                  key={email.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-gray-900">{email.subject}</h3>
                    <span className="text-xs text-gray-500">{email.date}</span>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-2">
                    <span className="font-medium">From:</span> {email.from}
                  </div>
                  
                  <p className="text-sm text-gray-700 line-clamp-2">
                    {email.snippet}
                  </p>
                  
                  {email.labels.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {email.labels.slice(0, 5).map((label) => (
                        <span
                          key={label}
                          className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded"
                        >
                          {label}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Setup Instructions */}
        <Card>
          <h2 className="text-xl font-semibold mb-4">Setup Instructions</h2>
          
          <div className="prose prose-sm max-w-none">
            <ol className="space-y-3">
              <li>
                Go to <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Cloud Console</a>
              </li>
              <li>Create a new project or select an existing one</li>
              <li>Enable the Gmail API for your project</li>
              <li>Create OAuth 2.0 credentials:
                <ul className="mt-2 space-y-1">
                  <li>Application type: Web application</li>
                  <li>Authorized redirect URI: <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:3000/gmail-oauth</code></li>
                </ul>
              </li>
              <li>Copy the Client ID and Client Secret</li>
              <li>Add them to your <code className="bg-gray-100 px-2 py-1 rounded">.env</code> file:
                <pre className="mt-2 bg-gray-100 p-3 rounded text-xs overflow-x-auto">
{`GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost:3000/gmail-oauth`}
                </pre>
              </li>
              <li>Restart the backend server</li>
              <li>Click "Connect Gmail Account" above to start the OAuth flow</li>
            </ol>
          </div>
        </Card>
      </div>
    </Layout>
  );
}