import Head from 'next/head';
import { useState } from 'react';
import { semanticSearch, SearchResult } from '@/lib/api';
import Card from '@/components/Card';
import Button from '@/components/Button';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topK, setTopK] = useState(5);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const searchResults = await semanticSearch(query, topK);
      setResults(searchResults);
    } catch (err: any) {
      setError(err.message || 'Failed to perform search. Make sure the backend is running.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const exampleQueries = [
    { text: 'urgent deadlines', icon: '⏰' },
    { text: 'IBM hackathon', icon: '🏆' },
    { text: 'invoice payment', icon: '💰' },
    { text: 'security vulnerabilities', icon: '🔒' },
    { text: 'meeting schedule', icon: '📅' },
  ];

  return (
    <>
      <Head>
        <title>Semantic Search - HackTheAgent</title>
        <meta name="description" content="Search emails by meaning, not just keywords" />
      </Head>

      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🔍 Semantic Email Search
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Find emails by meaning, not just keywords. Our AI understands context and intent.
          </p>
        </div>

        {/* Search Box */}
        <Card className="mb-8">
          <div className="space-y-4">
            <div className="flex gap-4">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search emails by meaning... (e.g., 'urgent deadlines')"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
              />
              <Button onClick={handleSearch} loading={loading} size="lg">
                Search
              </Button>
            </div>

            {/* Top K Selector */}
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Results to show:</label>
              <select
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={15}>15</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert type="error" onClose={() => setError(null)} className="mb-8">
            <p className="font-medium">Search Error</p>
            <p className="text-sm mt-1">{error}</p>
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <div className="py-12">
            <LoadingSpinner size="lg" text="Searching emails..." />
          </div>
        )}

        {/* Results */}
        {!loading && results.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                Found {results.length} relevant email{results.length !== 1 ? 's' : ''}
              </h2>
              <Button variant="secondary" size="sm" onClick={() => { setQuery(''); setResults([]); }}>
                Clear Results
              </Button>
            </div>
            
            <div className="space-y-4">
              {results.map((result, index) => (
                <Card key={result.id || index} hover>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-1">
                        {result.subject}
                      </h3>
                      <p className="text-sm text-gray-500">
                        📅 {result.date} • ID: {result.id}
                      </p>
                    </div>
                    <div className="ml-4">
                      <div className="px-4 py-2 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-full text-sm font-bold shadow-md">
                        {(result.score * 100).toFixed(1)}%
                      </div>
                      <p className="text-xs text-gray-500 text-center mt-1">relevance</p>
                    </div>
                  </div>
                  <p className="text-gray-700 leading-relaxed">{result.snippet}</p>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && query && !error && (
          <Card className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No results found</h3>
            <p className="text-gray-600">Try a different search query or check if emails are indexed.</p>
          </Card>
        )}

        {/* Example Queries */}
        {!query && !loading && (
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                💡 Try these example searches
              </h3>
              <div className="space-y-2">
                {exampleQueries.map((example) => (
                  <button
                    key={example.text}
                    onClick={() => setQuery(example.text)}
                    className="w-full flex items-center space-x-3 px-4 py-3 text-left text-primary-600 hover:bg-primary-50 rounded-lg transition-colors group"
                  >
                    <span className="text-2xl">{example.icon}</span>
                    <span className="font-medium group-hover:underline">{example.text}</span>
                  </button>
                ))}
              </div>
            </Card>

            <Card>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                ✨ How it works
              </h3>
              <div className="space-y-3 text-gray-700">
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">1️⃣</span>
                  <p><strong>Semantic Understanding:</strong> Searches by meaning, not just keywords</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">2️⃣</span>
                  <p><strong>AI Embeddings:</strong> Uses advanced ML models to understand context</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">3️⃣</span>
                  <p><strong>Ranked Results:</strong> Shows most relevant emails with confidence scores</p>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </>
  );
}