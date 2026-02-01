import { useState, useEffect } from 'react';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Alert from '@/components/Alert';
import LoadingSpinner from '@/components/LoadingSpinner';
import api from '@/lib/api';
import { RobotIcon, MailIcon, LightningIcon, LightBulbIcon, ChatIcon, SearchIcon, DocumentIcon, UsersIcon, ChartIcon, ExclamationIcon, ClockIcon, CheckIcon, XIcon } from '@/components/Icons';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  sources?: Array<{subject: string; date: string}>;
}

interface WorkflowStep {
  step: string;
  agent?: string;
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
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());

  useEffect(() => {
    checkGmailStatus();
    
    // Add welcome message
    setMessages([{
      role: 'system',
      content: 'Welcome! I\'m your Email Brain AI Agent.\n\nI can help you with your emails in natural language. Just ask me anything!\n\n**Examples:**\n• "What emails did I get about the project?"\n• "Summarize my unread emails"\n• "Find emails from John"\n• "Who sent me the most emails?"\n• "Organize my emails by category"\n\nI\'ll automatically load emails from ' + (gmailStatus?.authenticated ? 'your Gmail account' : 'the dataset') + ' when needed. No need to explicitly ask me to load them!',
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

  const addMessage = (role: 'user' | 'assistant' | 'system', content: string, sources?: Array<{subject: string; date: string}>) => {
    setMessages(prev => [...prev, { role, content, timestamp: new Date(), sources }]);
  };

  const updateWorkflow = (steps: WorkflowStep[]) => {
    setWorkflow(steps);
  };

  const toggleSources = (messageIndex: number) => {
    setExpandedSources(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageIndex)) {
        newSet.delete(messageIndex);
      } else {
        newSet.add(messageIndex);
      }
      return newSet;
    });
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
        addMessage('assistant', 'I need to load emails first to answer your question. Let me do that...');
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
      { step: 'Loading emails from ' + intent.source, agent: 'Load Agent', status: 'running' },
      { step: 'Normalizing emails', agent: 'Normalize Agent', status: 'pending' },
      { step: 'Indexing for search', agent: 'Semantic Agent', status: 'pending' }
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
        `Successfully processed ${loadResponse.data.emails.length} emails from ${intent.source}!\n\n` +
        `Summary:\n` +
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
      { step: 'Searching emails', agent: 'Semantic Agent', status: 'running' }
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
        let resultText = `Found ${response.data.results.length} relevant emails:\n\n`;
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
      { step: 'Searching relevant emails', agent: 'Semantic Agent', status: 'running' },
      { step: 'Generating summary', agent: 'RAG Agent', status: 'pending' }
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

      addMessage('assistant', ragResponse.data.answer, ragResponse.data.citations);
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
      { step: 'Loading emails', agent: 'Load Agent', status: 'running' },
      { step: 'Classifying emails', agent: 'Classify Agent', status: 'pending' }
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

      let resultText = `**Email Classification Results:**\n\n`;
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
      { step: 'Searching relevant emails', agent: 'Semantic Agent', status: 'running' },
      { step: 'Generating answer', agent: 'RAG Agent', status: 'pending' }
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

      // Send answer with sources separately for expandable UI
      addMessage('assistant', response.data.answer, response.data.citations);
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


  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="glass rounded-3xl p-8 hover-lift fade-in">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">AI Email Agent</h1>
            <p className="text-gray-600 dark:text-gray-300 text-lg">
              Ask me anything about your emails - I'll execute the workflow and show you the results
            </p>
          </div>
          <RobotIcon className="w-24 h-24 text-blue-600 dark:text-blue-400 float" />
        </div>
      </div>

      {/* Gmail Status Banner */}
      {gmailStatus && (
        <div className="glass rounded-2xl p-4 slide-in-left">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`status-dot ${gmailStatus.authenticated ? 'status-online' : 'status-offline'}`}></div>
              <div>
                <span className="text-sm font-semibold text-gray-900 dark:text-white block">
                  {gmailStatus.authenticated ? 'Gmail Connected' : 'Gmail Not Connected'}
                </span>
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  {gmailStatus.authenticated
                    ? gmailStatus.email
                    : 'Using mock data - Connect for real emails'}
                </span>
              </div>
            </div>
            {!gmailStatus.authenticated && (
              <Button
                onClick={() => window.location.href = '/gmail-oauth'}
                className="gradient-primary text-white px-6 py-2 rounded-xl hover-lift shadow-glow-blue flex items-center space-x-2"
              >
                <MailIcon className="w-4 h-4" />
                <span>Connect Gmail</span>
              </Button>
            )}
          </div>
        </div>
      )}

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chat Area - Takes 2 columns */}
        <div className="lg:col-span-2 space-y-6">
          {/* Workflow Steps */}
          {workflow.length > 0 && (
            <div className="glass rounded-2xl p-6 scale-in border-2 border-blue-200 dark:border-blue-800">
              <div className="flex items-center space-x-2 mb-6">
                <LightningIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                <h2 className="text-xl font-bold gradient-text">Multi-Agent Workflow</h2>
              </div>
              <div className="space-y-4">
                {workflow.map((step, idx) => (
                  <div key={idx} className="relative">
                    {/* Connection Line */}
                    {idx < workflow.length - 1 && (
                      <div className="absolute left-6 top-16 w-0.5 h-8 bg-gradient-to-b from-blue-400 to-blue-600 dark:from-blue-500 dark:to-blue-700"></div>
                    )}
                    
                    <div className="flex items-start space-x-4 p-4 rounded-xl bg-gradient-to-r from-white/80 to-blue-50/50 dark:from-gray-700/80 dark:to-blue-900/20 hover-lift border border-blue-100 dark:border-blue-800">
                      {/* Status Icon */}
                      <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                        step.status === 'completed' ? 'bg-green-100 dark:bg-green-900/30' :
                        step.status === 'running' ? 'bg-blue-100 dark:bg-blue-900/30 animate-pulse' :
                        step.status === 'error' ? 'bg-red-100 dark:bg-red-900/30' :
                        'bg-gray-100 dark:bg-gray-700'
                      }`}>
                        {step.status === 'completed' && <CheckIcon className="w-6 h-6 text-green-600 dark:text-green-400" />}
                        {step.status === 'running' && <LoadingSpinner />}
                        {step.status === 'error' && <XIcon className="w-6 h-6 text-red-600 dark:text-red-400" />}
                        {step.status === 'pending' && <ClockIcon className="w-6 h-6 text-gray-400" />}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        {/* Agent Name Badge */}
                        {step.agent && (
                          <div className="inline-flex items-center space-x-1 px-3 py-1 rounded-full bg-blue-600 dark:bg-blue-500 text-white text-xs font-semibold mb-2">
                            <RobotIcon className="w-3 h-3" />
                            <span>{step.agent}</span>
                          </div>
                        )}
                        
                        {/* Step Description */}
                        <div className="font-semibold text-gray-900 dark:text-white text-base">
                          {step.step}
                        </div>
                        
                        {/* Result */}
                        {step.result && (
                          <div className="text-sm text-green-600 dark:text-green-400 mt-2 flex items-center space-x-2 bg-green-50 dark:bg-green-900/20 px-3 py-1.5 rounded-lg">
                            <CheckIcon className="w-4 h-4" />
                            <span className="font-medium">{step.result}</span>
                          </div>
                        )}
                        
                        {/* Error */}
                        {step.error && (
                          <div className="text-sm text-red-600 dark:text-red-400 mt-2 flex items-center space-x-2 bg-red-50 dark:bg-red-900/20 px-3 py-1.5 rounded-lg">
                            <ExclamationIcon className="w-4 h-4" />
                            <span className="font-medium">{step.error}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <div className="glass rounded-2xl p-6 fade-in">
            <div className="space-y-4 max-h-[500px] overflow-y-auto mb-4 custom-scrollbar pr-2">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} fade-in`}
                  style={{ animationDelay: `${idx * 0.05}s` }}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-5 py-3 shadow-lg ${
                      msg.role === 'user'
                        ? 'message-user'
                        : msg.role === 'system'
                        ? 'message-system'
                        : 'message-assistant'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-sm leading-relaxed break-words overflow-hidden">{msg.content}</div>
                    
                    {/* Sources Section - Expandable */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                        <button
                          onClick={() => toggleSources(idx)}
                          className="flex items-center space-x-2 text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                        >
                          <DocumentIcon className="w-4 h-4" />
                          <span>{expandedSources.has(idx) ? 'Hide' : 'View'} Sources ({msg.sources.length})</span>
                          <span className={`transform transition-transform ${expandedSources.has(idx) ? 'rotate-180' : ''}`}>▼</span>
                        </button>
                        
                        {expandedSources.has(idx) && (
                          <div className="mt-2 space-y-2 animate-fade-in">
                            {msg.sources.map((source, sourceIdx) => (
                              <div key={sourceIdx} className="text-xs bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 flex items-start space-x-2">
                                <span className="text-blue-600 dark:text-blue-400 font-semibold">{sourceIdx + 1}.</span>
                                <div className="flex-1">
                                  <div className="font-medium text-gray-900 dark:text-white">{source.subject}</div>
                                  <div className="text-gray-600 dark:text-gray-400 mt-0.5">{source.date}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                    
                    <div className={`text-xs mt-2 flex items-center space-x-1 ${
                      msg.role === 'user' ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
                    }`}>
                      <ClockIcon className="w-3 h-3" />
                      <span>{msg.timestamp.toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start fade-in">
                  <div className="glass rounded-2xl px-5 py-3 flex items-center space-x-2">
                    <LoadingSpinner />
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              )}
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="flex space-x-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me anything..."
                className="flex-1 px-5 py-3 glass rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                disabled={loading}
              />
              <Button
                type="submit"
                disabled={loading || !input.trim()}
                className="gradient-primary text-white px-6 py-3 rounded-xl hover-lift shadow-glow-blue font-semibold"
              >
                {loading ? 'Processing' : 'Send'}
              </Button>
            </form>
          </div>
        </div>

        {/* Sidebar - Quick Actions */}
        <div className="space-y-6">
          <div className="glass rounded-2xl p-6 slide-in-right">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
              <LightningIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span>Quick Actions</span>
            </h2>
            <div className="space-y-2">
              {[
                { Icon: ChatIcon, text: 'What are my most recent emails about?', query: 'What are my most recent emails about?' },
                { Icon: SearchIcon, text: 'Find emails about meetings', query: 'Find emails about meetings' },
                { Icon: DocumentIcon, text: 'Summarize my unread emails', query: 'Summarize my unread emails' },
                { Icon: UsersIcon, text: 'Who sends me the most emails?', query: 'Who sends me the most emails?' },
                { Icon: ChartIcon, text: 'Organize by category', query: 'Organize my emails by category' },
                { Icon: ExclamationIcon, text: 'Important emails I missed', query: 'What important emails did I miss?' },
              ].map((action, idx) => {
                const Icon = action.Icon;
                return (
                  <button
                    key={idx}
                    onClick={() => setInput(action.query)}
                    className="w-full text-left px-4 py-3 rounded-xl bg-white/50 dark:bg-gray-700/50 hover:bg-white dark:hover:bg-gray-600 hover-lift transition-all text-sm font-medium text-gray-700 dark:text-gray-200 flex items-center space-x-3"
                    style={{ animationDelay: `${idx * 0.1}s` }}
                  >
                    <Icon className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                    <span>{action.text}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tips Card */}
          <div className="glass rounded-2xl p-6 slide-in-right" style={{ animationDelay: '0.2s' }}>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-3 flex items-center space-x-2">
              <LightBulbIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span>Pro Tips</span>
            </h2>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
              <li className="flex items-start space-x-2">
                <span className="text-blue-500 mt-0.5">•</span>
                <span>Ask questions in natural language</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-400 mt-0.5">•</span>
                <span>I'll automatically load emails when needed</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-600 mt-0.5">•</span>
                <span>Use specific keywords for better results</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-green-500 mt-0.5">•</span>
                <span>Connect Gmail for real-time data</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}