export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_admin: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type DocumentStatus = "pending" | "processing" | "ready" | "failed";
export type DocumentType = "pdf" | "docx" | "txt";

export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  file_type: DocumentType;
  file_size_bytes: number;
  status: DocumentStatus;
  chunk_count: number;
  error_message: string | null;
  created_at: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
}

export interface SourceReference {
  chunk_id: string;
  document_id: string;
  filename: string;
  chunk_index: number;
  excerpt: string;
  score: number;
}

export type MessageRole = "user" | "assistant";

export interface Message {
  id: string;
  session_id: string;
  role: MessageRole;
  content: string;
  sources: SourceReference[];
  latency_ms: number | null;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail {
  session: ChatSession;
  messages: Message[];
}

export interface AdminStats {
  total_users: number;
  total_documents: number;
  total_chunks: number;
  total_messages: number;
}

export interface StreamEvent {
  type: "start" | "token" | "done" | "error";
  content?: string;
  session_id?: string;
  sources?: SourceReference[];
  latency_ms?: number;
}
