/* Types for the AgriBot API */

export interface ChatRequest {
  query: string;
  input_mode?: string;
  trace_id?: string;
}

export interface DiagnosticsBlock {
  trace_id: string;
  timings_ms: Record<string, number>;
  mode_flags: string[];
  warnings: string[];
}

export interface VoiceBlock {
  transcript: string;
  asr_language: string;
  asr_confidence: number;
  asr_warnings: string[];
  needs_confirmation: boolean;
  transcript_suspected: string;
  suggested_actions: string[];
}

export interface ImageBlock {
  pipeline_used: string;
  analysis_summary: Record<string, unknown>;
  limitations: string[];
  possible_conditions: { label: string; confidence: number }[];
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
  grounding_action: string;
  follow_up_suggestions: string[];
  parsed_query?: string;
  diagnostics: DiagnosticsBlock;
  voice?: VoiceBlock | null;
  image?: ImageBlock | null;
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
  manifest: Record<string, unknown> | null;
  enabled_modules: Record<string, boolean>;
  grounding_mode: string;
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
  input_mode?: "text" | "voice" | "voice_confirmed" | "image";
  citations?: string[];
  kg_entities?: KGEntity[];
  evidence_grade?: string;
  is_verified?: boolean;
  verification_reason?: string;
  retry_count?: number;
  grounding_action?: string;
  follow_up_suggestions?: string[];
  diagnostics?: DiagnosticsBlock;
  voice?: VoiceBlock | null;
  image?: ImageBlock | null;
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
