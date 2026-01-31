import Head from 'next/head';
import { useState, useEffect } from 'react';
import { getStats, healthCheck, StatsResponse } from '@/lib/api';
import Card from '@/components/Card';
import Button from '@/components/Button';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';

export default function StatsPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [health, setHealth] = useState<{ status: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, healthData] = await Promise.all([
        getStats(),
        healthCheck()
      ]);
      setStats(statsData);
      setHealth(healthData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <>
      <Head>
        <title>Statistics - HackTheAgent</title>
        <meta name="description" content="System statistics and health" />
      </Head>

      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="flex items-center justify-between mb-12">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              📊 System Statistics
            </h1>
            <p className="text-xl text-gray-600">
              Monitor your email brain's performance and configuration
            </p>
          </div>
          <Button onClick={fetchData} loading={loading}>
            Refresh
          </Button>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert type="error" onClose={() => setError(null)} className="mb-6">
            <p className="font-medium">Error</p>
            <p className="text-sm mt-1">{error}</p>
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <Card className="py-12">
            <LoadingSpinner size="lg" text="Loading statistics..." />
          </Card>
        )}

        {/* Stats Display */}
        {!loading && stats && (
          <div className="space-y-6">
            {/* Health Status */}
            <Card>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${health?.status === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">System Health</h2>
                    <p className="text-gray-600">Backend API Status</p>
                  </div>
                </div>
                <div className={`px-6 py-3 rounded-full font-bold text-lg ${
                  health?.status === 'healthy' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {health?.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy'}
                </div>
              </div>
            </Card>

            {/* Vector Database Stats */}
            <div className="grid md:grid-cols-3 gap-6">
              <Card>
                <div className="text-center">
                  <div className="text-5xl mb-3">🗄️</div>
                  <div className="text-4xl font-bold text-primary-600 mb-2">
                    {stats.vector_db.total_chunks.toLocaleString()}
                  </div>
                  <p className="text-gray-600 font-medium">Total Chunks</p>
                  <p className="text-sm text-gray-500 mt-1">Indexed in vector DB</p>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="text-5xl mb-3">📦</div>
                  <div className="text-2xl font-bold text-gray-900 mb-2">
                    {stats.vector_db.collection_name}
                  </div>
                  <p className="text-gray-600 font-medium">Collection Name</p>
                  <p className="text-sm text-gray-500 mt-1">Vector store collection</p>
                </div>
              </Card>

              <Card>
                <div className="text-center">
                  <div className="text-5xl mb-3">🤖</div>
                  <div className="text-lg font-bold text-gray-900 mb-2">
                    {stats.vector_db.embedding_model}
                  </div>
                  <p className="text-gray-600 font-medium">Embedding Model</p>
                  <p className="text-sm text-gray-500 mt-1">AI model for embeddings</p>
                </div>
              </Card>
            </div>

            {/* Configuration */}
            <Card>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">⚙️ Configuration</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <span className="text-gray-700 font-medium">Embedding Model</span>
                    <span className="text-gray-900 font-mono text-sm">{stats.config.embedding_model}</span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <span className="text-gray-700 font-medium">LLM Provider</span>
                    <span className="text-gray-900 font-mono text-sm">{stats.config.llm_provider}</span>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <span className="text-gray-700 font-medium">Chunk Size</span>
                    <span className="text-gray-900 font-mono text-sm">{stats.config.chunk_size} chars</span>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <span className="text-gray-700 font-medium">Chunk Overlap</span>
                    <span className="text-gray-900 font-mono text-sm">{stats.config.chunk_overlap} chars</span>
                  </div>
                </div>
              </div>
            </Card>

            {/* Performance Metrics */}
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <h3 className="text-xl font-bold text-gray-900 mb-4">📈 Performance</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Search Latency</span>
                    <span className="font-bold text-green-600">{'< 2s'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">RAG Latency</span>
                    <span className="font-bold text-green-600">{'< 5s'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Indexing Speed</span>
                    <span className="font-bold text-blue-600">~50 chunks/s</span>
                  </div>
                </div>
              </Card>

              <Card>
                <h3 className="text-xl font-bold text-gray-900 mb-4">🔧 System Info</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Vector DB</span>
                    <span className="font-bold text-gray-900">ChromaDB</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Similarity Metric</span>
                    <span className="font-bold text-gray-900">Cosine</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">API Framework</span>
                    <span className="font-bold text-gray-900">FastAPI</span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <h3 className="text-xl font-bold text-gray-900 mb-4">🚀 Quick Actions</h3>
              <div className="grid md:grid-cols-4 gap-4">
                <Button onClick={() => window.location.href = '/'} variant="primary" className="w-full">
                  Search Emails
                </Button>
                <Button onClick={() => window.location.href = '/rag'} variant="primary" className="w-full">
                  Ask Questions
                </Button>
                <Button onClick={() => window.location.href = '/manage'} variant="secondary" className="w-full">
                  Manage Emails
                </Button>
                <Button onClick={() => window.open('http://localhost:8000/docs', '_blank')} variant="secondary" className="w-full">
                  API Docs
                </Button>
              </div>
            </Card>
          </div>
        )}
      </div>
    </>
  );
}