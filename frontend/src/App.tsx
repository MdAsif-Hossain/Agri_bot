import { useState, useRef, useCallback, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import MessageBubble from "./components/MessageBubble";
import VoiceConfirmBanner from "./components/VoiceConfirmBanner";
import Composer from "./components/Composer";
import { sendChat, sendVoice, sendVoiceConfirm, sendImage, exportCaseReport } from "./lib/api";
import type { Message, ChatResponse, VoiceBlock } from "./lib/api";

const SUGGESTIONS = [
  "What causes rice blast disease?",
  "How to treat leaf blight in wheat?",
  "ধানের পোকা দমনের উপায় কী?",
  "Best fertilizer schedule for tomato",
  "How to identify pest damage on crops?",
];

let _id = 0;
const uid = () => `msg-${Date.now()}-${++_id}`;

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [pendingVoiceConfirm, setPendingVoiceConfirm] = useState<{ voice: VoiceBlock; traceId: string } | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isLoading]);

  const addResponse = useCallback((r: ChatResponse, mode: "text" | "voice" | "voice_confirmed" | "image", userMsgId: string) => {
    setMessages(prev => {
      const newMessages = [...prev];
      if (r.parsed_query) {
        const uIdx = newMessages.findIndex(m => m.id === userMsgId);
        if (uIdx >= 0) {
          const prefix = mode === "voice" || mode === "voice_confirmed" ? "🎤 " : mode === "image" ? "📷 " : "";
          newMessages[uIdx] = { ...newMessages[uIdx], content: `${prefix}${r.parsed_query}` };
        }
      }
      return [...newMessages, {
        id: uid(), role: "assistant", content: r.answer, answer_bn: r.answer_bn,
        input_mode: mode, citations: r.citations, kg_entities: r.kg_entities,
        evidence_grade: r.evidence_grade, is_verified: r.is_verified,
        verification_reason: r.verification_reason, retry_count: r.retry_count,
        diagnostics: r.diagnostics, voice: r.voice, image: r.image,
        grounding_action: r.grounding_action, follow_up_suggestions: r.follow_up_suggestions,
        timestamp: Date.now(),
      }];
    });
  }, []);

  const addError = useCallback((msg: string) => {
    setMessages(prev => [...prev, { id: uid(), role: "assistant", content: `⚠️ ${msg}`, timestamp: Date.now() }]);
  }, []);

  const handleText = useCallback(async (q: string) => {
    const uId = uid();
    setMessages(prev => [...prev, { id: uId, role: "user", content: q, input_mode: "text", timestamp: Date.now() }]);
    setIsLoading(true);
    try { addResponse(await sendChat(q), "text", uId); } catch (e: any) { addError(e.message); } finally { setIsLoading(false); }
  }, [addResponse, addError]);

  const handleVoice = useCallback(async (blob: Blob) => {
    const uId = uid();
    setMessages(prev => [...prev, { id: uId, role: "user", content: "🎤 Transcribing voice...", input_mode: "voice", timestamp: Date.now() }]);
    setIsLoading(true);
    try {
      const r = await sendVoice(blob);
      // Check if voice needs confirmation
      if (r.voice?.needs_confirmation) {
        setPendingVoiceConfirm({
          voice: r.voice,
          traceId: r.diagnostics?.trace_id || "",
        });
        // Update user message to show transcript
        setMessages(prev => {
          const msgs = [...prev];
          const idx = msgs.findIndex(m => m.id === uId);
          if (idx >= 0) msgs[idx] = { ...msgs[idx], content: `🎤 "${r.voice!.transcript_suspected || r.voice!.transcript}" (needs confirmation)` };
          return msgs;
        });
      } else {
        addResponse(r, "voice", uId);
      }
    } catch (e: any) { addError(e.message); } finally { setIsLoading(false); }
  }, [addResponse, addError]);

  const handleVoiceConfirm = useCallback(async (editedText: string, traceId: string) => {
    setPendingVoiceConfirm(null);
    const uId = uid();
    setMessages(prev => [...prev, { id: uId, role: "user", content: `🎤✓ ${editedText}`, input_mode: "voice_confirmed", timestamp: Date.now() }]);
    setIsLoading(true);
    try { addResponse(await sendVoiceConfirm(editedText, traceId), "voice_confirmed", uId); } catch (e: any) { addError(e.message); } finally { setIsLoading(false); }
  }, [addResponse, addError]);

  const handleVoiceCancel = useCallback(() => {
    setPendingVoiceConfirm(null);
  }, []);

  const handleImage = useCallback(async (file: File, q: string) => {
    const uId = uid();
    setMessages(prev => [...prev, { id: uId, role: "user", content: q ? `📷 ${q}` : `📷 Analyzing: ${file.name}`, input_mode: "image", timestamp: Date.now() }]);
    setIsLoading(true);
    try { addResponse(await sendImage(file, q), "image", uId); } catch (e: any) { addError(e.message); } finally { setIsLoading(false); }
  }, [addResponse, addError]);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="flex-1 flex flex-col min-w-0 h-screen relative">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-6 bg-glass/40 backdrop-blur-xl border-b border-glass-border shrink-0">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="lg:hidden text-emerald-400 text-xl p-1" aria-label="Toggle menu">☰</button>
            <div>
              <h2 className="text-sm font-semibold text-white">AgriBot Chat</h2>
              <p className="text-xs text-emerald-700">Agricultural Advisory — Bengali & English</p>
            </div>
          </div>
          <div className="flex gap-2">
            {messages.length > 0 && (
              <>
                <button onClick={() => exportCaseReport(messages)} className="text-xs px-3 py-1.5 rounded-full border border-glass-border text-emerald-500 hover:bg-emerald-900/30 transition-colors">📄 Export</button>
                <button onClick={() => setMessages([])} className="text-xs px-3 py-1.5 rounded-full border border-glass-border text-red-400/60 hover:text-red-400 hover:border-red-500/30 transition-colors">🗑 Clear</button>
              </>
            )}
          </div>
        </header>

        {/* Chat */}
        <div className="flex-1 overflow-y-auto px-4 lg:px-8 pb-36 pt-6 scroll-smooth">
          <div className="max-w-[860px] mx-auto flex flex-col gap-5">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center py-16 min-h-[50vh] animate-fadeInUp">
                <div className="text-5xl mb-6 animate-float">🌾</div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-emerald-300 to-emerald-100 bg-clip-text text-transparent mb-2">Welcome to AgriBot</h2>
                <p className="text-emerald-700 max-w-md text-sm">Ask questions about crops, diseases, pests, and fertilizers. Get evidence-based answers with full citations.</p>
                <div className="flex flex-wrap gap-2 mt-8 justify-center">
                  {SUGGESTIONS.map(s => (
                    <button key={s} onClick={() => handleText(s)} className="text-xs px-4 py-2 rounded-full border border-glass-border text-emerald-400/80 hover:border-emerald-500 hover:text-emerald-300 bg-surface-3 hover:shadow-[0_0_15px_rgba(16,185,129,0.1)] transition-all">{s}</button>
                  ))}
                </div>
              </div>
            ) : messages.map(m => (
              <MessageBubble key={m.id} message={m} onFollowUp={handleText} />
            ))}

            {isLoading && (
              <div className="flex gap-3 animate-fadeInUp">
                <div className="w-9 h-9 rounded-lg bg-surface-3 border border-glass-border flex items-center justify-center text-sm shrink-0">🌾</div>
                <div className="flex items-center gap-2 px-4 py-3">
                  {[0, 1, 2].map(i => <div key={i} className="w-2 h-2 rounded-full bg-emerald-500 animate-typing" style={{ animationDelay: `${i * 0.2}s` }} />)}
                  <span className="text-xs text-emerald-700 ml-2">Searching & reasoning…</span>
                </div>
              </div>
            )}

            {/* Voice confirmation banner */}
            {pendingVoiceConfirm && (
              <VoiceConfirmBanner
                transcript={pendingVoiceConfirm.voice.transcript_suspected || pendingVoiceConfirm.voice.transcript}
                confidence={pendingVoiceConfirm.voice.asr_confidence}
                language={pendingVoiceConfirm.voice.asr_language}
                warnings={pendingVoiceConfirm.voice.asr_warnings}
                suggestedActions={pendingVoiceConfirm.voice.suggested_actions}
                traceId={pendingVoiceConfirm.traceId}
                onConfirm={handleVoiceConfirm}
                onCancel={handleVoiceCancel}
              />
            )}

            <div ref={endRef} />
          </div>
        </div>

        <Composer onText={handleText} onVoice={handleVoice} onImage={handleImage} disabled={isLoading} />
      </main>
    </div>
  );
}
