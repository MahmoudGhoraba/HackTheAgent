import Head from 'next/head';
import { useState } from 'react';
import Card from '@/components/Card';
import Button from '@/components/Button';
import LoadingSpinner from '@/components/LoadingSpinner';
import Alert from '@/components/Alert';

interface AgentStep {
  agent: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  startTime?: number;
  endTime?: number;
  result?: any;
  error?: string;
}

interface WorkflowState {
  status: 'idle' | 'running' | 'completed' | 'error';
  currentStep: number;
  steps: AgentStep[];
  totalTime?: number;
}

export default function OrchestratePage() {
  const [workflow, setWorkflow] = useState<WorkflowState>({
    status: 'idle',
    currentStep: 0,
    steps: [],
  });
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<any>(null);

  // Define the agent workflow
  const agentDefinitions = [
    {
      name: 'Supervisor Agent',
      icon: '🎯',
      description: 'Orchestrates the workflow and routes requests',
      color: 'bg-purple-500',
    },
    {
      name: 'Ingestion Agent',
      icon: '📥',
      description: 'Loads raw emails from dataset',
      color: 'bg-blue-500',
    },
    {
      name: 'Normalization Agent',
      icon: '🔄',
      description: 'Converts emails to structured format',
      color: 'bg-green-500',
    },
    {
      name: 'Indexing Agent',
      icon: '🔍',
      description: 'Creates embeddings and indexes messages',
      color: 'bg-yellow-500',
    },
    {
      name: 'Semantic Search Agent',
      icon: '🎯',
      description: 'Finds relevant emails by meaning',
      color: 'bg-red-500',
    },
    {
      name: 'RAG Answer Agent',
      icon: '🤖',
      description: 'Generates grounded answers with citations',
      color: 'bg-indigo-500',
    },
  ];

  const simulateWorkflow = async (queryText: string) => {
    const steps: AgentStep[] = agentDefinitions.map(agent => ({
      agent: agent.name,
      status: 'pending' as const,
    }));

    setWorkflow({
      status: 'running',
      currentStep: 0,
      steps,
    });

    const startTime = Date.now();

    try {
      // Step 1: Supervisor Agent
      await updateStep(0, 'running');
      await delay(500);
      await updateStep(0, 'completed', { message: 'Workflow initiated' });

      // Step 2: Ingestion Agent
      await updateStep(1, 'running');
      const loadResponse = await fetch('http://localhost:8000/tool/emails/load');
      const emails = await loadResponse.json();
      await updateStep(1, 'completed', { count: emails.emails.length });

      // Step 3: Normalization Agent
      await updateStep(2, 'running');
      const normalizeResponse = await fetch('http://localhost:8000/tool/emails/normalize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emails: emails.emails }),
      });
      const normalized = await normalizeResponse.json();
      await updateStep(2, 'completed', { count: normalized.messages.length });

      // Step 4: Indexing Agent
      await updateStep(3, 'running');
      const indexResponse = await fetch('http://localhost:8000/tool/semantic/index', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: normalized.messages }),
      });
      const indexed = await indexResponse.json();
      await updateStep(3, 'completed', { chunks: indexed.chunks_indexed });

      // Step 5: Semantic Search Agent
      await updateStep(4, 'running');
      const searchResponse = await fetch('http://localhost:8000/tool/semantic/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText, top_k: 5 }),
      });
      const searchResults = await searchResponse.json();
      await updateStep(4, 'completed', { results: searchResults.results.length });

      // Step 6: RAG Answer Agent
      await updateStep(5, 'running');
      const ragResponse = await fetch('http://localhost:8000/tool/rag/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryText, top_k: 5 }),
      });
      const ragResult = await ragResponse.json();
      await updateStep(5, 'completed', ragResult);

      const totalTime = Date.now() - startTime;
      setWorkflow(prev => ({
        ...prev,
        status: 'completed',
        totalTime,
      }));
      setResult(ragResult);
    } catch (error: any) {
      setWorkflow(prev => ({
        ...prev,
        status: 'error',
        steps: prev.steps.map((step, idx) =>
          idx === prev.currentStep ? { ...step, status: 'error', error: error.message } : step
        ),
      }));
    }
  };

  const updateStep = async (
    stepIndex: number,
    status: 'running' | 'completed' | 'error',
    result?: any
  ) => {
    setWorkflow(prev => ({
      ...prev,
      currentStep: stepIndex,
      steps: prev.steps.map((step, idx) =>
        idx === stepIndex
          ? {
              ...step,
              status,
              startTime: status === 'running' ? Date.now() : step.startTime,
              endTime: status === 'completed' ? Date.now() : step.endTime,
              result: status === 'completed' ? result : step.result,
            }
          : step
      ),
    }));
    await delay(800); // Simulate processing time
  };

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const handleRunWorkflow = () => {
    if (!query.trim()) return;
    setResult(null);
    simulateWorkflow(query);
  };

  const getStatusIcon = (status: AgentStep['status']) => {
    switch (status) {
      case 'pending':
        return '⏳';
      case 'running':
        return '⚡';
      case 'completed':
        return '✅';
      case 'error':
        return '❌';
    }
  };

  const getStatusColor = (status: AgentStep['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-200 text-gray-600';
      case 'running':
        return 'bg-blue-100 text-blue-700 animate-pulse';
      case 'completed':
        return 'bg-green-100 text-green-700';
      case 'error':
        return 'bg-red-100 text-red-700';
    }
  };

  const exampleQueries = [
    'What is the IBM Dev Day hackathon about?',
    'What are the urgent deadlines?',
    'Summarize security vulnerabilities',
    'What meetings are scheduled?',
  ];

  return (
    <>
      <Head>
        <title>Agent Orchestration - HackTheAgent</title>
        <meta name="description" content="Visualize watsonx Orchestrate agent workflow" />
      </Head>

      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🎭 Agent Orchestration Visualizer
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Watch watsonx Orchestrate agents work together in real-time
          </p>
        </div>

        {/* Query Input */}
        <Card className="mb-8">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Question
              </label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question to see the agent workflow in action..."
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg resize-none"
                disabled={workflow.status === 'running'}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex flex-wrap gap-2">
                {exampleQueries.map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => setQuery(example)}
                    className="text-sm px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
                    disabled={workflow.status === 'running'}
                  >
                    {example}
                  </button>
                ))}
              </div>

              <Button
                onClick={handleRunWorkflow}
                loading={workflow.status === 'running'}
                disabled={!query.trim() || workflow.status === 'running'}
                size="lg"
              >
                {workflow.status === 'running' ? 'Running...' : 'Run Workflow'}
              </Button>
            </div>
          </div>
        </Card>

        {/* Workflow Visualization */}
        {workflow.steps.length > 0 && (
          <div className="space-y-6">
            {/* Progress Bar */}
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">Workflow Progress</h2>
                {workflow.totalTime && (
                  <span className="text-sm text-gray-600">
                    Completed in {(workflow.totalTime / 1000).toFixed(2)}s
                  </span>
                )}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-primary-600 h-3 rounded-full transition-all duration-500"
                  style={{
                    width: `${((workflow.currentStep + 1) / workflow.steps.length) * 100}%`,
                  }}
                />
              </div>
            </Card>

            {/* Agent Steps */}
            <div className="space-y-4">
              {workflow.steps.map((step, index) => {
                const agent = agentDefinitions[index];
                const isActive = workflow.currentStep === index && workflow.status === 'running';

                return (
                  <Card
                    key={index}
                    className={`transition-all ${
                      isActive ? 'ring-2 ring-primary-500 shadow-lg scale-105' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-4">
                      {/* Agent Icon */}
                      <div
                        className={`flex-shrink-0 w-16 h-16 ${agent.color} rounded-full flex items-center justify-center text-3xl shadow-lg`}
                      >
                        {agent.icon}
                      </div>

                      {/* Agent Info */}
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-lg font-bold text-gray-900">{agent.name}</h3>
                          <span
                            className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                              step.status
                            )}`}
                          >
                            {getStatusIcon(step.status)} {step.status.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{agent.description}</p>

                        {/* Step Result */}
                        {step.result && (
                          <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                            <p className="text-sm text-green-800">
                              <strong>Result:</strong>{' '}
                              {typeof step.result === 'object'
                                ? JSON.stringify(step.result, null, 2).substring(0, 100) + '...'
                                : step.result}
                            </p>
                          </div>
                        )}

                        {/* Step Error */}
                        {step.error && (
                          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                            <p className="text-sm text-red-800">
                              <strong>Error:</strong> {step.error}
                            </p>
                          </div>
                        )}

                        {/* Loading Animation */}
                        {step.status === 'running' && (
                          <div className="mt-3">
                            <LoadingSpinner size="sm" text="Processing..." />
                          </div>
                        )}
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>

            {/* Final Result */}
            {result && workflow.status === 'completed' && (
              <Card className="border-2 border-green-500">
                <div className="flex items-start space-x-3 mb-4">
                  <span className="text-3xl">🎉</span>
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Final Answer</h2>
                    <div className="prose prose-lg max-w-none">
                      <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                        {result.answer}
                      </p>
                    </div>

                    {result.citations && result.citations.length > 0 && (
                      <div className="mt-6">
                        <h3 className="text-lg font-bold text-gray-900 mb-3">
                          📚 Sources ({result.citations.length})
                        </h3>
                        <div className="space-y-2">
                          {result.citations.map((citation: any, idx: number) => (
                            <div
                              key={idx}
                              className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                            >
                              <p className="text-sm font-medium text-gray-900">
                                {citation.subject}
                              </p>
                              <p className="text-xs text-gray-500 mt-1">{citation.date}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Info Card */}
        {workflow.steps.length === 0 && (
          <Card>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              ✨ How Agent Orchestration Works
            </h3>
            <div className="space-y-3 text-gray-700">
              {agentDefinitions.map((agent, idx) => (
                <div key={idx} className="flex items-start space-x-3">
                  <div className={`w-10 h-10 ${agent.color} rounded-full flex items-center justify-center text-xl flex-shrink-0`}>
                    {agent.icon}
                  </div>
                  <div>
                    <p className="font-medium">{agent.name}</p>
                    <p className="text-sm text-gray-600">{agent.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </>
  );
}