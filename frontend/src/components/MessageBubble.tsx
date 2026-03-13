import { useState, useRef, useEffect } from "react";
import type { Message } from "../lib/api";
import { getTTSAudio } from "../lib/api";

type Tab = "en" | "bn";

export default function MessageBubble({ message: m, onFollowUp }: { message: Message; onFollowUp?: (q: string) => void }) {
    const [tab, setTab] = useState<Tab>("en");
    const [showDiagnostics, setShowDiagnostics] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    const isAssistant = m.role === "assistant";
    const content = tab === "en" ? m.content : (m.answer_bn || m.content);

    const toggleDiagnostic = () => setShowDiagnostics(p => !p);

    const handleTTS = async () => {
        if (isPlaying && audioRef.current) {
            audioRef.current.pause();
            setIsPlaying(false);
            return;
        }
        try {
            if (!audioRef.current || audioRef.current.dataset.lang !== tab) {
                const url = await getTTSAudio(content, tab);
                if (audioRef.current) URL.revokeObjectURL(audioRef.current.src);
                audioRef.current = new Audio(url);
                audioRef.current.dataset.lang = tab;
                audioRef.current.onended = () => setIsPlaying(false);
            }
            setIsPlaying(true);
            await audioRef.current.play();
        } catch (e) {
            console.error("TTS failed", e);
            setIsPlaying(false);
        }
    };

    useEffect(() => {
        return () => { if (audioRef.current) URL.revokeObjectURL(audioRef.current.src); };
    }, []);

    if (!isAssistant) {
        return (
            <div className="flex justify-end animate-fadeInUp">
                <div className="max-w-[80%] bg-gradient-to-br from-emerald-600 to-emerald-800 text-white px-5 py-3.5 rounded-2xl rounded-tr-sm shadow-sm">
                    {m.input_mode === "voice" && <span className="mr-2 opacity-70">🎤</span>}
                    {m.input_mode === "image" && <span className="mr-2 opacity-70">📷</span>}
                    {m.content}
                </div>
            </div>
        );
    }

    // Handle errors
    if (m.content.startsWith("⚠️")) {
        return (
            <div className="flex gap-4 animate-fadeInUp">
                <div className="w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 flex items-center justify-center text-lg shrink-0">⚠️</div>
                <div className="bg-red-500/5 border border-red-500/10 px-5 py-3.5 rounded-2xl rounded-tl-sm text-red-400 text-sm">{m.content.slice(2)}</div>
            </div>
        );
    }

    const verifColor = m.is_verified ? "text-green-400 bg-green-500/10 border-green-500/20" : "text-yellow-400 bg-yellow-500/10 border-yellow-500/20";
    const groundColor = m.grounding_action === "pass" ? "text-emerald-400" : m.grounding_action === "refuse" ? "text-red-400" : "text-yellow-400";

    return (
        <div className="flex gap-4 animate-fadeInUp group">
            {/* Avatar */}
            <div className="relative shrink-0">
                <div className="w-10 h-10 rounded-xl bg-surface-3 border border-glass-border flex items-center justify-center text-lg shadow-sm">🌾</div>
                {m.input_mode === "image" && <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-600 border-2 border-surface flex items-center justify-center text-[8px]">📷</div>}
            </div>

            <div className="flex-1 min-w-0">
                <div className="bg-surface-2 border border-glass-border rounded-2xl rounded-tl-sm shadow-sm overflow-hidden">

                    {/* Tabs & Controls */}
                    {m.answer_bn && (
                        <div className="flex items-center justify-between border-b border-glass-border px-4 py-2 bg-surface-3/50 text-xs">
                            <div className="flex gap-4">
                                <button onClick={() => setTab("en")} className={`font-medium transition-colors ${tab === "en" ? "text-emerald-400" : "text-emerald-700 hover:text-emerald-500"}`}>English</button>
                                <button onClick={() => setTab("bn")} className={`font-medium transition-colors ${tab === "bn" ? "text-emerald-400" : "text-emerald-700 hover:text-emerald-500"}`}>বাংলা</button>
                            </div>
                            <div className="flex gap-2">
                                <button onClick={handleTTS} className={`w-6 h-6 rounded-full flex items-center justify-center transition-colors ${isPlaying ? "bg-emerald-500/20 text-emerald-400" : "text-emerald-700 hover:bg-emerald-900/30 hover:text-emerald-500"}`} title="Listen">
                                    {isPlaying ? "⏸" : "🔊"}
                                </button>
                                <button onClick={toggleDiagnostic} className={`flex items-center gap-1.5 px-2 py-1 rounded transition-colors ${showDiagnostics ? "bg-emerald-900/40 text-emerald-300" : "text-emerald-700 hover:text-emerald-500"}`}>
                                    <span className="text-[10px]">⚖️</span> Eval
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Content */}
                    <div className="p-5 text-[15px] leading-relaxed whitespace-pre-wrap">
                        {content}
                    </div>

                    {/* Citations */}
                    {m.citations && m.citations.length > 0 && (
                        <div className="px-5 pb-4">
                            <div className="flex flex-wrap gap-2 text-[11px]">
                                <span className="text-emerald-700 my-auto mr-1">Sources:</span>
                                {m.citations.map((c, i) => (
                                    <span key={i} className="px-2 py-0.5 rounded border border-glass-border bg-emerald-900/10 text-emerald-300/80 max-w-[200px] truncate" title={c}>{c}</span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Diagnostics Drawer */}
                    {showDiagnostics && (
                        <div className="px-5 py-4 bg-surface-3/80 border-t border-glass-border text-xs text-emerald-200/70 space-y-3">
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                                <div>
                                    <div className="text-[10px] text-emerald-700 uppercase tracking-wide mb-1">Verification</div>
                                    <div className={`inline-block px-2 py-0.5 rounded border ${verifColor}`}>{m.is_verified ? "Verified" : "Failed / Unverified"}</div>
                                </div>
                                <div>
                                    <div className="text-[10px] text-emerald-700 uppercase tracking-wide mb-1">Grounding Policy</div>
                                    <div className={`font-medium ${groundColor}`}>{m.grounding_action}</div>
                                </div>
                                <div>
                                    <div className="text-[10px] text-emerald-700 uppercase tracking-wide mb-1">Evidence Grade</div>
                                    <div>{m.evidence_grade} (Retries: {m.retry_count})</div>
                                </div>
                                <div>
                                    <div className="text-[10px] text-emerald-700 uppercase tracking-wide mb-1">Trace ID</div>
                                    <div className="font-mono text-[10px] truncate" title={m.diagnostics?.trace_id}>{m.diagnostics?.trace_id?.split('-')[0]}...</div>
                                </div>
                            </div>

                            {m.verification_reason && (
                                <div>
                                    <div className="text-[10px] text-emerald-700 uppercase tracking-wide mb-1">LLM Verification Reason</div>
                                    <div className="bg-surface border border-glass-border/50 rounded p-2 text-[11px] leading-snug">{m.verification_reason}</div>
                                </div>
                            )}

                            {m.diagnostics?.timings_ms && Object.keys(m.diagnostics.timings_ms).length > 0 && (
                                <div>
                                    <div className="text-[10px] text-emerald-700 uppercase tracking-wide mb-2">Node Latency (ms)</div>
                                    <div className="flex flex-wrap gap-2 text-[10px]">
                                        {Object.entries(m.diagnostics.timings_ms).map(([k, v]) => (
                                            <span key={k} className={`px-1.5 py-0.5 rounded ${k === 'total' ? 'bg-emerald-900/30 text-emerald-400 font-bold' : 'bg-surface border border-glass-border text-emerald-500/60'}`}>
                                                {k}: {Number(v)}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {m.kg_entities && m.kg_entities.length > 0 && (
                                <div>
                                    <div className="text-[10px] text-emerald-700 uppercase tracking-wide mb-1">Linked Entities ({m.kg_entities.length})</div>
                                    <div className="flex flex-wrap gap-1">
                                        {m.kg_entities.slice(0, 5).map((e, i) => (
                                            <span key={i} className="text-[10px] px-1.5 py-0.5 bg-emerald-600/10 text-emerald-400 rounded">{e.en}</span>
                                        ))}
                                        {m.kg_entities.length > 5 && <span className="text-[10px] px-1.5 py-0.5 text-emerald-700">+{m.kg_entities.length - 5} more</span>}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Follow-up Suggestions */}
                {m.follow_up_suggestions && m.follow_up_suggestions.length > 0 && onFollowUp && (
                    <div className="flex flex-wrap gap-2 mt-3 ml-2">
                        <span className="text-[11px] text-emerald-700 my-auto">Suggestions:</span>
                        {m.follow_up_suggestions.map(s => (
                            <button key={s} onClick={() => onFollowUp(s)} className="text-[11px] px-3 py-1 rounded-full border border-emerald-900/50 text-emerald-400/80 hover:bg-emerald-900/20 hover:text-emerald-300 transition-colors">
                                {s}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
