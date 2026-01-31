import Head from 'next/head';
import { useState } from 'react';
import { ragAnswer, RAGResponse } from '@/lib/api';
import Card from '@/components/Card';
import Button from '@/components/Button';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';

export default function RAGPage() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topK, setTopK] = useState(5);

  const handleAsk = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const result = await ragAnswer(question, topK);
      setResponse(result);
    } catch (err: any) {
      setError(err.message || 'Failed to get answer. Make sure the backend is running.');
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const exampleQuestions = [
    { text: 'What is the IBM Dev Day hackathon about?', icon: '🏆' },
    { text: 'What are the urgent deadlines mentioned?', icon: '⏰' },
    { text: 'Summarize the invoice payment details', icon: '💰' },
    { text: 'What security issues were reported?', icon: '🔒' },
    { text: 'What meetings are scheduled?', icon: '📅' },
  ];

  return (
    <>
      <Head>
        <title>RAG Q&A - HackTheAgent</title>
        <meta name="description" content="Ask questions and get AI-powered answers with citations" />
      </Head>

      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🤖 AI-Powered Q&A
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Ask questions about your emails and get grounded answers with citations. No hallucinations!
          </p>
        </div>

        {/* Question Input */}
        <Card className="mb-8">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Question
              </label>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about your emails... (e.g., 'What is the IBM hackathon about?')"
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg resize-none"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <label className="text-sm font-medium text-gray-700">Context emails:</label>
                <select
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value))}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value={3}>3</option>
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                </select>
              </div>

              <Button onClick={handleAsk} loading={loading} size="lg">
                Ask AI
              </Button>
            </div>
          </div>
        </Card>

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
            <LoadingSpinner size="lg" text="Generating answer..." />
          </div>
        )}

        {/* Answer */}
        {!loading && response && (
          <div className="space-y-6">
            {/* AI Answer */}
            <Card>
              <div className="flex items-start space-x-3 mb-4">
                <span className="text-3xl">💡</span>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Answer</h2>
                  <div className="prose prose-lg max-w-none">
                    <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                      {response.answer}
                    </p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Citations */}
            {response.citations && response.citations.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                  <span>📚</span>
                  <span>Sources ({response.citations.length})</span>
                </h3>
                <div className="space-y-3">
                  {response.citations.map((citation, index) => (
                    <Card key={citation.id || index} hover>
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900 mb-1">
                            {citation.subject}
                          </h4>
                          <p className="text-sm text-gray-500 mb-2">
                            📅 {citation.date} • ID: {citation.id}
                          </p>
                          <p className="text-gray-700 text-sm">{citation.snippet}</p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Clear Button */}
            <div className="text-center">
              <Button 
                variant="secondary" 
                onClick={() => { setQuestion(''); setResponse(null); }}
              >
                Ask Another Question
              </Button>
            </div>
          </div>
        )}

        {/* Example Questions */}
        {!question && !loading && !response && (
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                💡 Try these example questions
              </h3>
              <div className="space-y-2">
                {exampleQuestions.map((example) => (
                  <button
                    key={example.text}
                    onClick={() => setQuestion(example.text)}
                    className="w-full flex items-start space-x-3 px-4 py-3 text-left text-primary-600 hover:bg-primary-50 rounded-lg transition-colors group"
                  >
                    <span className="text-2xl flex-shrink-0">{example.icon}</span>
                    <span className="font-medium group-hover:underline">{example.text}</span>
                  </button>
                ))}
              </div>
            </Card>

            <Card>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                ✨ How RAG works
              </h3>
              <div className="space-y-3 text-gray-700">
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">1️⃣</span>
                  <p><strong>Retrieval:</strong> Finds relevant emails using semantic search</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">2️⃣</span>
                  <p><strong>Augmentation:</strong> Builds context from retrieved emails</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">3️⃣</span>
                  <p><strong>Generation:</strong> AI generates answer using ONLY the context</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">4️⃣</span>
                  <p><strong>Citations:</strong> Shows source emails for transparency</p>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </>
  );
}