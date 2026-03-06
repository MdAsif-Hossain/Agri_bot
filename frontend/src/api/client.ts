/**
 * AgriBot API Client
 *
 * Typed fetch-based client for all backend endpoints.
 * Works with both local dev (proxy) and production (same-origin).
 */

import type { ChatResponse, HealthResponse, TTSRequest } from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(
    path: string,
    options?: RequestInit
): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API error: ${res.status}`);
    }

    return res.json();
}

/** Send a text chat query */
export async function sendChat(query: string): Promise<ChatResponse> {
    return request<ChatResponse>("/chat", {
        method: "POST",
        body: JSON.stringify({ query }),
    });
}

/** Send a voice audio file */
export async function sendVoice(audioBlob: Blob): Promise<ChatResponse> {
    const form = new FormData();
    form.append("audio", audioBlob, "recording.wav");

    const res = await fetch(`${API_BASE}/chat/voice`, {
        method: "POST",
        body: form,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API error: ${res.status}`);
    }

    return res.json();
}

/** Send an image with optional text query */
export async function sendImage(
    imageFile: File,
    query?: string
): Promise<ChatResponse> {
    const form = new FormData();
    form.append("image", imageFile);
    if (query) form.append("query", query);

    const res = await fetch(`${API_BASE}/chat/image`, {
        method: "POST",
        body: form,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API error: ${res.status}`);
    }

    return res.json();
}

/** Get system health status */
export async function getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>("/health");
}

/** Request TTS audio and return a playable blob URL */
export async function getTTSAudio(req: TTSRequest): Promise<string> {
    const res = await fetch(`${API_BASE}/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `TTS error: ${res.status}`);
    }

    const blob = await res.blob();
    return URL.createObjectURL(blob);
}
