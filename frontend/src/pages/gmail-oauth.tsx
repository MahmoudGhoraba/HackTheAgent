import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Alert from '@/components/Alert';
import LoadingSpinner from '@/components/LoadingSpinner';
import api from '@/lib/api';
import { MailIcon, LockIcon, UserIcon, ChartIcon, InboxIcon, BookIcon, CheckIcon } from '@/components/Icons';

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
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="glass rounded-3xl p-8 hover-lift fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">Gmail Connection</h1>
            <p className="text-gray-600 dark:text-gray-300 text-lg">
              Connect your Gmail account to use real emails with the AI agent
            </p>
          </div>
          <MailIcon className="w-24 h-24 text-blue-600 dark:text-blue-400 float" />
        </div>
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
      <div className="glass rounded-2xl p-6 slide-in-left">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center space-x-2">
          <LockIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          <span>Authentication Status</span>
        </h2>
        
        {authStatus === null ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : authStatus.authenticated ? (
          <div className="space-y-6">
            <div className="flex items-center space-x-3 p-4 rounded-xl bg-green-50 border border-green-200">
              <div className="status-dot status-online"></div>
              <div>
                <span className="text-green-700 font-bold text-lg block">Connected</span>
                <span className="text-green-600 text-sm">Your Gmail account is successfully connected</span>
              </div>
            </div>
            
            {authStatus.email && (
              <div className="glass rounded-xl p-4">
                <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 mb-1">
                  <UserIcon className="w-4 h-4" />
                  <span className="text-sm font-medium">Authenticated as:</span>
                </div>
                <p className="text-lg font-bold text-gray-900 dark:text-white">{authStatus.email}</p>
              </div>
            )}
            
            {profile && (
              <div className="glass rounded-xl p-6">
                <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
                  <ChartIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span>Account Information</span>
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 rounded-xl bg-blue-50 dark:bg-blue-900/30">
                    <div className="text-3xl font-bold gradient-text">
                      {profile.messages_total.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">Total Messages</div>
                  </div>
                  <div className="text-center p-4 rounded-xl bg-blue-100 dark:bg-blue-800/30">
                    <div className="text-3xl font-bold gradient-text">
                      {profile.threads_total.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">Total Threads</div>
                  </div>
                </div>
              </div>
            )}
            
            <Button
              onClick={revokeAccess}
              variant="secondary"
              disabled={loading}
              className="glass px-6 py-3 rounded-xl hover-lift w-full sm:w-auto"
            >
              🔓 Revoke Access
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center space-x-3 p-4 rounded-xl bg-red-50 border border-red-200">
              <div className="status-dot status-offline"></div>
              <div>
                <span className="text-red-700 font-bold text-lg block">Not Connected</span>
                <span className="text-red-600 text-sm">Connect your Gmail account to get started</span>
              </div>
            </div>
            
            <div className="glass rounded-xl p-6">
              <h3 className="font-bold text-gray-900 dark:text-white mb-3">Why connect Gmail?</h3>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <li className="flex items-start space-x-2">
                  <CheckIcon className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Access your real emails in real-time</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckIcon className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Secure OAuth 2.0 authentication</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckIcon className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>No password storage - tokens only</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckIcon className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Revoke access anytime</span>
                </li>
              </ul>
            </div>
            
            <Button
              onClick={startOAuthFlow}
              disabled={loading}
              className="gradient-primary text-white px-8 py-4 rounded-xl hover-lift shadow-glow-blue w-full sm:w-auto text-lg font-semibold"
            >
              {loading ? '⏳ Connecting...' : '🔗 Connect Gmail Account'}
            </Button>
          </div>
        )}
      </div>

      {/* Fetch Emails */}
      {authStatus?.authenticated && (
        <div className="glass rounded-2xl p-6 slide-in-right">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center space-x-2">
            <InboxIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            <span>Fetch Emails</span>
          </h2>
          
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Max Results
                </label>
                <input
                  type="number"
                  min="1"
                  max="500"
                  value={maxResults}
                  onChange={(e) => setMaxResults(parseInt(e.target.value))}
                  className="w-full px-4 py-3 glass rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Search Query (optional)
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="e.g., is:unread, from:example@gmail.com"
                  className="w-full px-4 py-3 glass rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                />
              </div>
            </div>
            
            <Button
              onClick={fetchEmails}
              disabled={loading}
              className="gradient-primary text-white px-6 py-3 rounded-xl hover-lift shadow-glow-blue font-semibold"
            >
              {loading ? '⏳ Fetching...' : '🚀 Fetch Emails'}
            </Button>
          </div>
        </div>
      )}

      {/* Email List */}
      {emails.length > 0 && (
        <div className="glass rounded-2xl p-6 scale-in">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MailIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              <span>Fetched Emails</span>
            </div>
            <span className="text-sm font-normal glass px-3 py-1 rounded-full">
              {emails.length} emails
            </span>
          </h2>
          
          <div className="space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar pr-2">
            {emails.map((email, idx) => (
              <div
                key={email.id}
                className="glass rounded-xl p-4 hover-lift hover-glow transition-all fade-in"
                style={{ animationDelay: `${idx * 0.05}s` }}
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-bold text-gray-900 flex-1 pr-4">{email.subject}</h3>
                  <span className="text-xs text-gray-500 whitespace-nowrap glass px-2 py-1 rounded-lg">
                    {email.date}
                  </span>
                </div>
                
                <div className="text-sm text-gray-600 mb-2 flex items-center space-x-2">
                  <span className="font-semibold">From:</span>
                  <span className="glass px-2 py-1 rounded-lg text-xs">{email.from}</span>
                </div>
                
                <p className="text-sm text-gray-700 line-clamp-2 mb-3">
                  {email.snippet}
                </p>
                
                {email.labels.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {email.labels.slice(0, 5).map((label) => (
                      <span
                        key={label}
                        className="px-3 py-1 text-xs font-medium gradient-primary text-white rounded-full"
                      >
                        {label}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Setup Instructions */}
      <div className="glass rounded-2xl p-6 fade-in">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center space-x-2">
          <BookIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          <span>Setup Instructions</span>
        </h2>
        
        <div className="prose prose-sm max-w-none">
          <ol className="space-y-4">
            <li className="glass rounded-xl p-4">
              <span className="font-semibold text-gray-900">Step 1:</span> Go to{' '}
              <a
                href="https://console.cloud.google.com/apis/credentials"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 font-semibold underline"
              >
                Google Cloud Console
              </a>
            </li>
            <li className="glass rounded-xl p-4">
              <span className="font-semibold text-gray-900">Step 2:</span> Create a new project or select an existing one
            </li>
            <li className="glass rounded-xl p-4">
              <span className="font-semibold text-gray-900">Step 3:</span> Enable the Gmail API for your project
            </li>
            <li className="glass rounded-xl p-4">
              <span className="font-semibold text-gray-900">Step 4:</span> Create OAuth 2.0 credentials:
              <ul className="mt-2 ml-4 space-y-1">
                <li>• Application type: <code className="glass px-2 py-1 rounded text-xs">Web application</code></li>
                <li>• Authorized redirect URI: <code className="glass px-2 py-1 rounded text-xs">http://localhost:3000/gmail-oauth</code></li>
              </ul>
            </li>
            <li className="glass rounded-xl p-4">
              <span className="font-semibold text-gray-900">Step 5:</span> Copy the Client ID and Client Secret
            </li>
            <li className="glass rounded-xl p-4">
              <span className="font-semibold text-gray-900">Step 6:</span> Add them to your <code className="glass px-2 py-1 rounded text-xs">.env</code> file:
              <pre className="mt-3 glass p-4 rounded-xl text-xs overflow-x-auto">
{`GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost:3000/gmail-oauth`}
              </pre>
            </li>
            <li className="glass rounded-xl p-4">
              <span className="font-semibold text-gray-900">Step 7:</span> Restart the backend server
            </li>
            <li className="glass rounded-xl p-4">
              <span className="font-semibold text-gray-900">Step 8:</span> Click "Connect Gmail Account" above to start the OAuth flow
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}