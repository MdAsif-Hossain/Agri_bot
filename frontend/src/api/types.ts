/* Types for the AgriBot API */

export interface ChatRequest {
  query: string;
}

export interface ChatResponse {
  answer: string;
  answer_bn: string;
  citations: string[];
  kg_entities: KGEntity[];
  evidence_grade: string;
  is_verified: boolean;
  verification_reason: string;
  retry_count: number;
  input_mode: string;
}

export interface KGEntity {
  bn: string;
  en: string;
  type: string;
  id?: number;
  canonical_bn?: string;
  canonical_en?: string;
  entity_type?: string;
  aliases?: string[];
}

export interface HealthResponse {
  status: string;
  chunk_count: number;
  kg_entities: number;
  kg_aliases: number;
  kg_relations: number;
}

export interface TTSRequest {
  text: string;
  language: "en" | "bn";
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  answer_bn?: string;
  input_mode?: "text" | "voice" | "image";
  evidence?: EvidenceData;
  timestamp: number;
}

export interface EvidenceData {
  citations: string[];
  kg_entities: KGEntity[];
  evidence_grade: string;
  is_verified: boolean;
  verification_reason: string;
  retry_count: number;
}
