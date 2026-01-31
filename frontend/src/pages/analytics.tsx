import Head from 'next/head';
import { useState, useEffect } from 'react';
import Card from '@/components/Card';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';
import api from '@/lib/api';

interface EmailAnalytics {
  overview: {
    total_emails: number;
    date_range: { start: string; end: string } | null;
    avg_length: number;
    with_attachments: number;
  };
  senders: Array<{ sender: string; count: number; percentage: number }>;
  categories: Record<string, number>;
  timeline: {
    daily: Record<string, number>;
    total_days: number;
    avg_per_day: number;
  };
  priorities: Record<string, number>;
  sentiments: Record<string, number>;
  keywords: Array<{ word: string; count: number }>;
  threads: {
    total: number;
    replies: number;
    forwards: number;
    original: number;
  };
}

interface SearchAnalytics {
  total_searches: number;
  avg_latency_ms: number;
  avg_results: number;
  popular_queries: Array<{ query: string; count: number }>;
  zero_result_queries: string[];
}

export default function AnalyticsPage() {
  const [emailAnalytics, setEmailAnalytics] = useState<EmailAnalytics | null>(null);
  const [searchAnalytics, setSearchAnalytics] = useState<SearchAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [emailData, searchData] = await Promise.all([
        api.get('/analytics/emails').then(r => r.data),
        api.get('/analytics/search').then(r => r.data),
      ]);
      setEmailAnalytics(emailData);
      setSearchAnalytics(searchData);
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (index: number) => {
    const colors = [
      'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-red-500',
      'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-teal-500'
    ];
    return colors[index % colors.length];
  };

  return (
    <>
      <Head>
        <title>Analytics - HackTheAgent</title>
        <meta name="description" content="Email and search analytics dashboard" />
      </Head>

      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            📊 Analytics Dashboard
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Insights and statistics about your emails and search patterns
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert type="error" onClose={() => setError(null)} className="mb-8">
            <p className="font-medium">Error</p>
            <p className="text-sm mt-1">{error}</p>
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <div className="py-12">
            <LoadingSpinner size="lg" text="Loading analytics..." />
          </div>
        )}

        {/* Analytics Content */}
        {!loading && emailAnalytics && searchAnalytics && (
          <div className="space-y-8">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <div className="text-center">
                  <div className="text-4xl mb-2">📧</div>
                  <div className="text-3xl font-bold text-primary-600">
                    {emailAnalytics.overview.total_emails}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Total Emails</div>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="text-4xl mb-2">🔍</div>
                  <div className="text-3xl font-bold text-primary-600">
                    {searchAnalytics.total_searches}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Total Searches</div>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="text-4xl mb-2">⚡</div>
                  <div className="text-3xl font-bold text-primary-600">
                    {searchAnalytics.avg_latency_ms.toFixed(0)}ms
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Avg Search Time</div>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="text-4xl mb-2">💬</div>
                  <div className="text-3xl font-bold text-primary-600">
                    {emailAnalytics.threads.total}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Email Threads</div>
                </div>
              </Card>
            </div>

            {/* Top Senders */}
            <Card>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                👥 Top Senders
              </h2>
              <div className="space-y-3">
                {emailAnalytics.senders.slice(0, 10).map((sender, index) => (
                  <div key={index} className="flex items-center">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">
                          {sender.sender}
                        </span>
                        <span className="text-sm text-gray-500">
                          {sender.count} emails ({sender.percentage.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all"
                          style={{ width: `${sender.percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Categories and Priorities */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Categories */}
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  🏷️ Categories
                </h2>
                <div className="space-y-3">
                  {Object.entries(emailAnalytics.categories).map(([category, count], index) => (
                    <div key={category} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded ${getCategoryColor(index)}`} />
                        <span className="text-sm font-medium text-gray-700 capitalize">
                          {category}
                        </span>
                      </div>
                      <span className="text-sm font-bold text-gray-900">{count}</span>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Priorities */}
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  ⚠️ Priority Distribution
                </h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                    <span className="font-medium text-red-800">High Priority</span>
                    <span className="text-2xl font-bold text-red-600">
                      {emailAnalytics.priorities.high || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
                    <span className="font-medium text-yellow-800">Medium Priority</span>
                    <span className="text-2xl font-bold text-yellow-600">
                      {emailAnalytics.priorities.medium || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                    <span className="font-medium text-green-800">Low Priority</span>
                    <span className="text-2xl font-bold text-green-600">
                      {emailAnalytics.priorities.low || 0}
                    </span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Sentiments */}
            <Card>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                😊 Sentiment Analysis
              </h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-6 bg-green-50 rounded-lg">
                  <div className="text-4xl mb-2">😊</div>
                  <div className="text-3xl font-bold text-green-600">
                    {emailAnalytics.sentiments.positive || 0}
                  </div>
                  <div className="text-sm text-green-800 mt-1">Positive</div>
                </div>
                <div className="text-center p-6 bg-gray-50 rounded-lg">
                  <div className="text-4xl mb-2">😐</div>
                  <div className="text-3xl font-bold text-gray-600">
                    {emailAnalytics.sentiments.neutral || 0}
                  </div>
                  <div className="text-sm text-gray-800 mt-1">Neutral</div>
                </div>
                <div className="text-center p-6 bg-red-50 rounded-lg">
                  <div className="text-4xl mb-2">😟</div>
                  <div className="text-3xl font-bold text-red-600">
                    {emailAnalytics.sentiments.negative || 0}
                  </div>
                  <div className="text-sm text-red-800 mt-1">Negative</div>
                </div>
              </div>
            </Card>

            {/* Keywords and Popular Searches */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Top Keywords */}
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  🔤 Top Keywords
                </h2>
                <div className="flex flex-wrap gap-2">
                  {emailAnalytics.keywords.slice(0, 20).map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium"
                    >
                      {keyword.word} ({keyword.count})
                    </span>
                  ))}
                </div>
              </Card>

              {/* Popular Searches */}
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  🔥 Popular Searches
                </h2>
                <div className="space-y-2">
                  {searchAnalytics.popular_queries.slice(0, 10).map((query, index) => (
                    <div key={index} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">{query.query}</span>
                      <span className="text-sm font-bold text-primary-600">{query.count}x</span>
                    </div>
                  ))}
                  {searchAnalytics.popular_queries.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-4">
                      No search history yet
                    </p>
                  )}
                </div>
              </Card>
            </div>

            {/* Thread Statistics */}
            <Card>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                💬 Conversation Threads
              </h2>
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {emailAnalytics.threads.total}
                  </div>
                  <div className="text-sm text-blue-800 mt-1">Total Threads</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {emailAnalytics.threads.original}
                  </div>
                  <div className="text-sm text-green-800 mt-1">Original</div>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {emailAnalytics.threads.replies}
                  </div>
                  <div className="text-sm text-yellow-800 mt-1">Replies</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {emailAnalytics.threads.forwards}
                  </div>
                  <div className="text-sm text-purple-800 mt-1">Forwards</div>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </>
  );
}