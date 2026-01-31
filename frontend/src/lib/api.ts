import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Email {
  id: string;
  from: string;
  to: string;
  subject: string;
  date: string;
  body: string;
}

export interface NormalizedMessage {
  id: string;
  text: string;
  metadata: {
    from_: string;
    to: string;
    subject: string;
    date: string;
  };
}

export interface SearchResult {
  id: string;
  subject: string;
  date: string;
  score: number;
  snippet: string;
}

export interface Citation {
  id: string;
  subject: string;
  date: string;
  snippet: string;
}

export interface RAGResponse {
  answer: string;
  citations: Citation[];
}

export interface IndexResponse {
  status: string;
  chunks_indexed: number;
}

export interface StatsResponse {
  vector_db: {
    total_chunks: number;
    collection_name: string;
    embedding_model: string;
  };
  config: {
    embedding_model: string;
    llm_provider: string;
    chunk_size: number;
    chunk_overlap: number;
  };
}

// API Functions

/**
 * Load raw emails from dataset
 */
export const loadEmails = async (): Promise<Email[]> => {
  const response = await api.get('/tool/emails/load');
  return response.data.emails;
};

/**
 * Normalize raw emails into structured messages
 */
export const normalizeEmails = async (emails: Email[]): Promise<NormalizedMessage[]> => {
  const response = await api.post('/tool/emails/normalize', { emails });
  return response.data.messages;
};

/**
 * Index normalized messages for semantic search
 */
export const indexMessages = async (messages: NormalizedMessage[]): Promise<IndexResponse> => {
  const response = await api.post('/tool/semantic/index', { messages });
  return response.data;
};

/**
 * Perform semantic search
 */
export const semanticSearch = async (query: string, topK: number = 5): Promise<SearchResult[]> => {
  const response = await api.post('/tool/semantic/search', {
    query,
    top_k: topK,
  });
  return response.data.results;
};

/**
 * Get RAG answer with citations
 */
export const ragAnswer = async (question: string, topK: number = 5): Promise<RAGResponse> => {
  const response = await api.post('/tool/rag/answer', {
    question,
    top_k: topK,
  });
  return response.data;
};

/**
 * Get system statistics
 */
export const getStats = async (): Promise<StatsResponse> => {
  const response = await api.get('/stats');
  return response.data;
};

/**
 * Health check
 */
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await api.get('/health');
  return response.data;
};

export default api;