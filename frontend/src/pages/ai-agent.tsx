import { useState, useEffect } from 'react';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Alert from '@/components/Alert';
import LoadingSpinner from '@/components/LoadingSpinner';
import api from '@/lib/api';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

interface WorkflowStep {
  step: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  result?: any;
  error?: string;
}

interface GmailStatus {
  authenticated: boolean;
  email?: string;
}

export default function AIAgentPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [workflow, setWorkflow] = useState<WorkflowStep[]>([]);
  const [gmailStatus, setGmailStatus] = useState<GmailStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkGmailStatus();
    
    // Add welcome message
    setMessages([{
      role: 'system',
      content: 'Welcome! I\'m your Email Brain AI Agent. 🤖\n\nI can help you with your emails in natural language. Just ask me anything!\n\n**Examples:**\n• "What emails did I get about the project?"\n• "Summarize my unread emails"\n• "Find emails from John"\n• "Who sent me the most emails?"\n• "Organize my emails by category"\n\nI\'ll automatically load emails from ' + (gmailStatus?.authenticated ? 'your Gmail account' : 'the dataset') + ' when needed. No need to explicitly ask me to load them!',
      timestamp: new Date()
    }]);
  }, []);

  const checkGmailStatus = async () => {
    try {
      const response = await api.get('/oauth/gmail/status');
      setGmailStatus(response.data);
    } catch (err) {
      console.error('Error checking Gmail status:', err);
    }
  };

  const addMessage = (role: 'user' | 'assistant' | 'system', content: string) => {
    setMessages(prev => [...prev, { role, content, timestamp: new Date() }]);
  };

  const updateWorkflow = (steps: WorkflowStep[]) => {
    setWorkflow(steps);
  };

  const executeWorkflow = async (userQuery: string) => {
    setLoading(true);
    setError(null);
    setWorkflow([]);

    try {
      // Analyze user intent
      const intent = analyzeIntent(userQuery);
      
      // Check if we need to load emails first
      const needsEmails = await checkIfNeedsEmails(intent);
      
      if (needsEmails && intent.action !== 'load_emails') {
        addMessage('assistant', '🤔 I need to load emails first to answer your question. Let me do that...');
        await loadEmailsWorkflow({
          action: 'load_emails',
          source: gmailStatus?.authenticated ? 'gmail' : 'file',
          maxResults: 50,
          query: ''
        });
      }
      
      if (intent.action === 'load_emails') {
        await loadEmailsWorkflow(intent);
      } else if (intent.action === 'search_emails') {
        await searchEmailsWorkflow(intent);
      } else if (intent.action === 'summarize_emails') {
        await summarizeEmailsWorkflow(intent);
      } else if (intent.action === 'classify_emails') {
        await classifyEmailsWorkflow(intent);
      } else if (intent.action === 'answer_question') {
        await answerQuestionWorkflow(intent);
      } else {
        addMessage('assistant', 'I\'m not sure how to help with that. Try asking me to:\n• Search emails\n• Summarize emails\n• Classify emails\n• Answer questions about emails\n\nI\'ll automatically load emails when needed!');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      addMessage('assistant', `Error: ${err.message || 'Something went wrong'}`);
    } finally {
      setLoading(false);
    }
  };

  const checkIfNeedsEmails = async (intent: any): Promise<boolean> => {
    // Actions that need emails to be loaded
    const needsEmailsActions = ['search_emails', 'summarize_emails', 'answer_question'];
    
    if (!needsEmailsActions.includes(intent.action)) {
      return false;
    }

    // Check if emails are already indexed
    try {
      const statsResponse = await api.get('/stats');
      const hasIndexedEmails = statsResponse.data.vector_db?.total_chunks > 0;
      return !hasIndexedEmails;
    } catch {
      return true; // If we can't check, assume we need to load
    }
  };

  const analyzeIntent = (query: string): any => {
    const lowerQuery = query.toLowerCase();
    
    // Search emails - prioritize this over load
    if (lowerQuery.includes('search') || lowerQuery.includes('find')) {
      return {
        action: 'search_emails',
        query: query.replace(/search|find/gi, '').trim()
      };
    }
    
    // Summarize emails
    if (lowerQuery.includes('summarize') || lowerQuery.includes('summary')) {
      return {
        action: 'summarize_emails',
        query: query
      };
    }
    
    // Classify emails
    if (lowerQuery.includes('classify') || lowerQuery.includes('categorize') || lowerQuery.includes('organize')) {
      return {
        action: 'classify_emails'
      };
    }
    
    // Explicit load request
    if (lowerQuery.includes('load') || lowerQuery.includes('fetch') || lowerQuery.includes('get my emails')) {
      const maxResults = extractNumber(query) || 50;
      const isUnread = lowerQuery.includes('unread');
      const isRecent = lowerQuery.includes('recent') || lowerQuery.includes('latest');
      
      return {
        action: 'load_emails',
        source: gmailStatus?.authenticated ? 'gmail' : 'file',
        maxResults,
        query: isUnread ? 'is:unread' : isRecent ? 'newer_than:7d' : ''
      };
    }
    
    // Default to answer question for any query
    // This makes the AI more conversational and intelligent
    return {
      action: 'answer_question',
      question: query
    };
  };

  const extractNumber = (text: string): number | null => {
    const match = text.match(/\d+/);
    return match ? parseInt(match[0]) : null;
  };

  const loadEmailsWorkflow = async (intent: any) => {
    const steps: WorkflowStep[] = [
      { step: 'Loading emails from ' + intent.source, status: 'running' },
      { step: 'Normalizing emails', status: 'pending' },
      { step: 'Indexing for search', status: 'pending' }
    ];
    updateWorkflow(steps);

    try {
      // Step 1: Load emails
      const loadResponse = await api.get('/tool/emails/load', {
        params: {
          source: intent.source,
          max_results: intent.maxResults,
          query: intent.query
        }
      });
      
      steps[0].status = 'completed';
      steps[0].result = `Loaded ${loadResponse.data.emails.length} emails`;
      updateWorkflow([...steps]);

      // Step 2: Normalize
      steps[1].status = 'running';
      updateWorkflow([...steps]);
      
      const normalizeResponse = await api.post('/tool/emails/normalize', {
        emails: loadResponse.data.emails
      });
      
      steps[1].status = 'completed';
      steps[1].result = `Normalized ${normalizeResponse.data.messages.length} messages`;
      updateWorkflow([...steps]);

      // Step 3: Index
      steps[2].status = 'running';
      updateWorkflow([...steps]);
      
      const indexResponse = await api.post('/tool/semantic/index', {
        messages: normalizeResponse.data.messages
      });
      
      steps[2].status = 'completed';
      steps[2].result = `Indexed ${indexResponse.data.chunks_indexed} chunks`;
      updateWorkflow([...steps]);

      addMessage('assistant', 
        `✅ Successfully processed ${loadResponse.data.emails.length} emails from ${intent.source}!\n\n` +
        `📊 Summary:\n` +
        `• Loaded: ${loadResponse.data.emails.length} emails\n` +
        `• Normalized: ${normalizeResponse.data.messages.length} messages\n` +
        `• Indexed: ${indexResponse.data.chunks_indexed} searchable chunks\n\n` +
        `You can now search or ask questions about your emails!`
      );
    } catch (err: any) {
      const failedStep = steps.findIndex(s => s.status === 'running');
      if (failedStep >= 0) {
        steps[failedStep].status = 'error';
        steps[failedStep].error = err.response?.data?.detail || err.message;
        updateWorkflow([...steps]);
      }
      throw err;
    }
  };

  const searchEmailsWorkflow = async (intent: any) => {
    const steps: WorkflowStep[] = [
      { step: 'Searching emails', status: 'running' }
    ];
    updateWorkflow(steps);

    try {
      const response = await api.post('/tool/semantic/search', {
        query: intent.query,
        top_k: 5
      });

      steps[0].status = 'completed';
      steps[0].result = `Found ${response.data.results.length} results`;
      updateWorkflow([...steps]);

      if (response.data.results.length === 0) {
        addMessage('assistant', 'No emails found matching your search. Try loading emails first or use a different query.');
      } else {
        let resultText = `🔍 Found ${response.data.results.length} relevant emails:\n\n`;
        response.data.results.forEach((result: any, idx: number) => {
          resultText += `${idx + 1}. **${result.subject}**\n`;
          resultText += `   From: ${result.date}\n`;
          resultText += `   Score: ${(result.score * 100).toFixed(1)}%\n`;
          resultText += `   ${result.snippet}\n\n`;
        });
        addMessage('assistant', resultText);
      }
    } catch (err: any) {
      steps[0].status = 'error';
      steps[0].error = err.response?.data?.detail || err.message;
      updateWorkflow([...steps]);
      throw err;
    }
  };

  const summarizeEmailsWorkflow = async (intent: any) => {
    const steps: WorkflowStep[] = [
      { step: 'Searching relevant emails', status: 'running' },
      { step: 'Generating summary', status: 'pending' }
    ];
    updateWorkflow(steps);

    try {
      // Search for relevant emails
      const searchResponse = await api.post('/tool/semantic/search', {
        query: intent.query.replace(/summarize|summary/gi, '').trim() || 'recent emails',
        top_k: 10
      });

      steps[0].status = 'completed';
      steps[0].result = `Found ${searchResponse.data.results.length} emails`;
      updateWorkflow([...steps]);

      // Generate summary using RAG
      steps[1].status = 'running';
      updateWorkflow([...steps]);

      const ragResponse = await api.post('/tool/rag/answer', {
        question: `Summarize these emails: ${intent.query}`,
        top_k: 10
      });

      steps[1].status = 'completed';
      steps[1].result = 'Summary generated';
      updateWorkflow([...steps]);

      addMessage('assistant', 
        `📝 **Email Summary:**\n\n${ragResponse.data.answer}\n\n` +
        `📎 Based on ${ragResponse.data.citations.length} emails`
      );
    } catch (err: any) {
      const failedStep = steps.findIndex(s => s.status === 'running');
      if (failedStep >= 0) {
        steps[failedStep].status = 'error';
        steps[failedStep].error = err.response?.data?.detail || err.message;
        updateWorkflow([...steps]);
      }
      throw err;
    }
  };

  const classifyEmailsWorkflow = async (intent: any) => {
    const steps: WorkflowStep[] = [
      { step: 'Loading emails', status: 'running' },
      { step: 'Classifying emails', status: 'pending' }
    ];
    updateWorkflow(steps);

    try {
      // Load emails
      const loadResponse = await api.get('/tool/emails/load', {
        params: { source: gmailStatus?.authenticated ? 'gmail' : 'file' }
      });

      steps[0].status = 'completed';
      steps[0].result = `Loaded ${loadResponse.data.emails.length} emails`;
      updateWorkflow([...steps]);

      // Classify
      steps[1].status = 'running';
      updateWorkflow([...steps]);

      const classifyResponse = await api.post('/tool/emails/classify', {
        emails: loadResponse.data.emails
      });

      steps[1].status = 'completed';
      steps[1].result = `Classified ${classifyResponse.data.classifications.length} emails`;
      updateWorkflow([...steps]);

      // Analyze classifications
      const categories: any = {};
      const priorities: any = {};
      classifyResponse.data.classifications.forEach((c: any) => {
        c.categories.forEach((cat: string) => {
          categories[cat] = (categories[cat] || 0) + 1;
        });
        priorities[c.priority] = (priorities[c.priority] || 0) + 1;
      });

      let resultText = `📊 **Email Classification Results:**\n\n`;
      resultText += `**Categories:**\n`;
      Object.entries(categories).forEach(([cat, count]) => {
        resultText += `• ${cat}: ${count} emails\n`;
      });
      resultText += `\n**Priorities:**\n`;
      Object.entries(priorities).forEach(([pri, count]) => {
        resultText += `• ${pri}: ${count} emails\n`;
      });

      addMessage('assistant', resultText);
    } catch (err: any) {
      const failedStep = steps.findIndex(s => s.status === 'running');
      if (failedStep >= 0) {
        steps[failedStep].status = 'error';
        steps[failedStep].error = err.response?.data?.detail || err.message;
        updateWorkflow([...steps]);
      }
      throw err;
    }
  };

  const answerQuestionWorkflow = async (intent: any) => {
    const steps: WorkflowStep[] = [
      { step: 'Searching relevant emails', status: 'running' },
      { step: 'Generating answer', status: 'pending' }
    ];
    updateWorkflow(steps);

    try {
      steps[1].status = 'running';
      updateWorkflow([...steps]);

      const response = await api.post('/tool/rag/answer', {
        question: intent.question,
        top_k: 5
      });

      steps[0].status = 'completed';
      steps[1].status = 'completed';
      steps[1].result = 'Answer generated';
      updateWorkflow([...steps]);

      let answerText = `💡 **Answer:**\n\n${response.data.answer}\n\n`;
      if (response.data.citations.length > 0) {
        answerText += `📎 **Sources:**\n`;
        response.data.citations.forEach((citation: any, idx: number) => {
          answerText += `${idx + 1}. ${citation.subject} (${citation.date})\n`;
        });
      }

      addMessage('assistant', answerText);
    } catch (err: any) {
      const failedStep = steps.findIndex(s => s.status === 'running');
      if (failedStep >= 0) {
        steps[failedStep].status = 'error';
        steps[failedStep].error = err.response?.data?.detail || err.message;
        updateWorkflow([...steps]);
      }
      throw err;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    addMessage('user', userMessage);

    await executeWorkflow(userMessage);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'running': return '⏳';
      case 'error': return '❌';
      default: return '⏸️';
    }
  };

  return (
    <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Email Agent</h1>
          <p className="mt-2 text-gray-600">
            Ask me anything about your emails - I'll execute the workflow and show you the results
          </p>
        </div>

        {/* Gmail Status Banner */}
        {gmailStatus && (
          <Card>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${gmailStatus.authenticated ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                <span className="text-sm font-medium">
                  {gmailStatus.authenticated 
                    ? `Gmail Connected: ${gmailStatus.email}` 
                    : 'Gmail Not Connected - Using mock data'}
                </span>
              </div>
              {!gmailStatus.authenticated && (
                <Button
                  onClick={() => window.location.href = '/gmail-oauth'}
                  variant="secondary"
                  className="text-sm"
                >
                  Connect Gmail
                </Button>
              )}
            </div>
          </Card>
        )}

        {error && (
          <Alert type="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Workflow Steps */}
        {workflow.length > 0 && (
          <Card>
            <h2 className="text-lg font-semibold mb-4">Workflow Execution</h2>
            <div className="space-y-3">
              {workflow.map((step, idx) => (
                <div key={idx} className="flex items-start space-x-3">
                  <span className="text-xl">{getStatusIcon(step.status)}</span>
                  <div className="flex-1">
                    <div className="font-medium">{step.step}</div>
                    {step.result && (
                      <div className="text-sm text-gray-600 mt-1">{step.result}</div>
                    )}
                    {step.error && (
                      <div className="text-sm text-red-600 mt-1">{step.error}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Chat Messages */}
        <Card>
          <div className="space-y-4 max-h-96 overflow-y-auto mb-4 custom-scrollbar">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-lg px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : msg.role === 'system'
                      ? 'bg-gray-100 text-gray-800'
                      : 'bg-gray-200 text-gray-900'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  <div className={`text-xs mt-2 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                    {msg.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 rounded-lg px-4 py-3">
                  <LoadingSpinner />
                </div>
              </div>
            )}
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything... (e.g., 'Load my recent emails' or 'Summarize unread emails')"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <Button type="submit" disabled={loading || !input.trim()}>
              {loading ? 'Processing...' : 'Send'}
            </Button>
          </form>
        </Card>

        {/* Quick Actions */}
        <Card>
          <h2 className="text-lg font-semibold mb-4">Try These Questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Button
              onClick={() => {
                setInput('What are my most recent emails about?');
              }}
              variant="secondary"
              className="text-sm text-left justify-start"
            >
              💬 What are my most recent emails about?
            </Button>
            <Button
              onClick={() => {
                setInput('Find emails about meetings');
              }}
              variant="secondary"
              className="text-sm text-left justify-start"
            >
              🔍 Find emails about meetings
            </Button>
            <Button
              onClick={() => {
                setInput('Summarize my unread emails');
              }}
              variant="secondary"
              className="text-sm text-left justify-start"
            >
              📝 Summarize my unread emails
            </Button>
            <Button
              onClick={() => {
                setInput('Who sends me the most emails?');
              }}
              variant="secondary"
              className="text-sm text-left justify-start"
            >
              👥 Who sends me the most emails?
            </Button>
            <Button
              onClick={() => {
                setInput('Organize my emails by category');
              }}
              variant="secondary"
              className="text-sm text-left justify-start"
            >
              📊 Organize my emails by category
            </Button>
            <Button
              onClick={() => {
                setInput('What important emails did I miss?');
              }}
              variant="secondary"
              className="text-sm text-left justify-start"
            >
              ⚠️ What important emails did I miss?
            </Button>
          </div>
        </Card>
      </div>
  );
}