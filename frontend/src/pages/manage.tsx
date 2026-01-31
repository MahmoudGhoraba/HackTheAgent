import Head from 'next/head';
import { useState, useEffect } from 'react';
import { loadEmails, normalizeEmails, indexMessages, Email, NormalizedMessage } from '@/lib/api';
import Card from '@/components/Card';
import Button from '@/components/Button';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';

export default function ManagePage() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [normalizedMessages, setNormalizedMessages] = useState<NormalizedMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [step, setStep] = useState<'load' | 'normalize' | 'index' | 'complete'>('load');

  const handleLoadEmails = async () => {
    setLoading(true);
    setError(null);
    try {
      const loadedEmails = await loadEmails();
      setEmails(loadedEmails);
      setSuccess(`Successfully loaded ${loadedEmails.length} emails`);
      setStep('normalize');
    } catch (err: any) {
      setError(err.message || 'Failed to load emails');
    } finally {
      setLoading(false);
    }
  };

  const handleNormalizeEmails = async () => {
    setLoading(true);
    setError(null);
    try {
      const normalized = await normalizeEmails(emails);
      setNormalizedMessages(normalized);
      setSuccess(`Successfully normalized ${normalized.length} messages`);
      setStep('index');
    } catch (err: any) {
      setError(err.message || 'Failed to normalize emails');
    } finally {
      setLoading(false);
    }
  };

  const handleIndexMessages = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await indexMessages(normalizedMessages);
      setSuccess(`Successfully indexed ${result.chunks_indexed} chunks`);
      setStep('complete');
    } catch (err: any) {
      setError(err.message || 'Failed to index messages');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setEmails([]);
    setNormalizedMessages([]);
    setStep('load');
    setSuccess(null);
    setError(null);
  };

  const steps = [
    { id: 'load', label: 'Load Emails', icon: '📥', description: 'Load raw emails from dataset' },
    { id: 'normalize', label: 'Normalize', icon: '🔄', description: 'Convert to structured format' },
    { id: 'index', label: 'Index', icon: '🔍', description: 'Create embeddings for search' },
    { id: 'complete', label: 'Complete', icon: '✅', description: 'Ready to search!' },
  ];

  const currentStepIndex = steps.findIndex(s => s.id === step);

  return (
    <>
      <Head>
        <title>Manage Emails - HackTheAgent</title>
        <meta name="description" content="Load, normalize, and index emails" />
      </Head>

      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            📧 Email Management
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Load, normalize, and index your emails for semantic search
          </p>
        </div>

        {/* Progress Steps */}
        <Card className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((s, index) => (
              <div key={s.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl mb-2 transition-all ${
                      index <= currentStepIndex
                        ? 'bg-primary-600 text-white shadow-lg scale-110'
                        : 'bg-gray-200 text-gray-400'
                    }`}
                  >
                    {s.icon}
                  </div>
                  <p className={`text-sm font-medium ${index <= currentStepIndex ? 'text-primary-600' : 'text-gray-500'}`}>
                    {s.label}
                  </p>
                  <p className="text-xs text-gray-500 text-center mt-1">{s.description}</p>
                </div>
                {index < steps.length - 1 && (
                  <div className={`h-1 flex-1 mx-4 rounded ${index < currentStepIndex ? 'bg-primary-600' : 'bg-gray-200'}`} />
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* Alerts */}
        {error && (
          <Alert type="error" onClose={() => setError(null)} className="mb-6">
            <p className="font-medium">Error</p>
            <p className="text-sm mt-1">{error}</p>
          </Alert>
        )}

        {success && (
          <Alert type="success" onClose={() => setSuccess(null)} className="mb-6">
            <p className="font-medium">Success!</p>
            <p className="text-sm mt-1">{success}</p>
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <Card className="py-12">
            <LoadingSpinner size="lg" text="Processing..." />
          </Card>
        )}

        {/* Step Content */}
        {!loading && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Action Card */}
            <Card>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                {step === 'load' && '📥 Step 1: Load Emails'}
                {step === 'normalize' && '🔄 Step 2: Normalize Emails'}
                {step === 'index' && '🔍 Step 3: Index Messages'}
                {step === 'complete' && '✅ All Done!'}
              </h3>

              {step === 'load' && (
                <div className="space-y-4">
                  <p className="text-gray-700">
                    Load raw emails from the dataset file. This will fetch all available emails.
                  </p>
                  <Button onClick={handleLoadEmails} size="lg" className="w-full">
                    Load Emails from Dataset
                  </Button>
                </div>
              )}

              {step === 'normalize' && (
                <div className="space-y-4">
                  <p className="text-gray-700">
                    Convert raw emails into structured messages with metadata for better processing.
                  </p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-800">
                      ✓ Loaded {emails.length} emails
                    </p>
                  </div>
                  <Button onClick={handleNormalizeEmails} size="lg" className="w-full">
                    Normalize {emails.length} Emails
                  </Button>
                </div>
              )}

              {step === 'index' && (
                <div className="space-y-4">
                  <p className="text-gray-700">
                    Create embeddings and index messages in the vector database for semantic search.
                  </p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
                    <p className="text-sm text-blue-800">
                      ✓ Loaded {emails.length} emails
                    </p>
                    <p className="text-sm text-blue-800">
                      ✓ Normalized {normalizedMessages.length} messages
                    </p>
                  </div>
                  <Button onClick={handleIndexMessages} size="lg" className="w-full">
                    Index {normalizedMessages.length} Messages
                  </Button>
                </div>
              )}

              {step === 'complete' && (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                    <div className="text-6xl mb-4">🎉</div>
                    <p className="text-lg font-semibold text-green-800 mb-2">
                      All emails are indexed!
                    </p>
                    <p className="text-sm text-green-700">
                      You can now search and ask questions about your emails.
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Button onClick={() => window.location.href = '/'} variant="primary">
                      Go to Search
                    </Button>
                    <Button onClick={() => window.location.href = '/rag'} variant="primary">
                      Ask Questions
                    </Button>
                  </div>
                  <Button onClick={handleReset} variant="secondary" className="w-full">
                    Start Over
                  </Button>
                </div>
              )}
            </Card>

            {/* Info Card */}
            <Card>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                📊 Current Status
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-700">Emails Loaded</span>
                  <span className="font-bold text-gray-900">{emails.length}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-700">Messages Normalized</span>
                  <span className="font-bold text-gray-900">{normalizedMessages.length}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-700">Current Step</span>
                  <span className="font-bold text-primary-600">{currentStepIndex + 1} of {steps.length}</span>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3">💡 What happens in each step?</h4>
                <div className="space-y-3 text-sm text-gray-700">
                  <div>
                    <strong>1. Load:</strong> Fetches raw emails from the JSON dataset
                  </div>
                  <div>
                    <strong>2. Normalize:</strong> Extracts metadata and structures the content
                  </div>
                  <div>
                    <strong>3. Index:</strong> Creates AI embeddings and stores in vector DB
                  </div>
                  <div>
                    <strong>4. Complete:</strong> Ready for semantic search and RAG!
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </>
  );
}