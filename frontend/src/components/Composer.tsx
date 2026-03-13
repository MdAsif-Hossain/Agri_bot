import { useState, useRef, useEffect } from "react";

export default function Composer({ onText, onVoice, onImage, disabled }: {
    onText: (t: string) => void;
    onVoice: (b: Blob) => void;
    onImage: (f: File, q: string) => void;
    disabled: boolean;
}) {
    const [text, setText] = useState("");
    const [isRecording, setIsRecording] = useState(false);
    const [image, setImage] = useState<File | null>(null);
    const [imgUrl, setImgUrl] = useState<string | null>(null);
    const imageRef = useRef<HTMLInputElement>(null);
    const mediaRef = useRef<MediaRecorder | null>(null);
    const chunks = useRef<BlobPart[]>([]);

    useEffect(() => {
        if (image) { const u = URL.createObjectURL(image); setImgUrl(u); return () => URL.revokeObjectURL(u); }
        setImgUrl(null);
    }, [image]);

    const handleSubmit = () => {
        if (disabled) return;
        if (image) { onImage(image, text); setImage(null); setText(""); }
        else if (text.trim()) { onText(text.trim()); setText(""); }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
    };

    const toggleVoice = async () => {
        if (isRecording && mediaRef.current) { mediaRef.current.stop(); return; }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRef.current = new MediaRecorder(stream);
            chunks.current = [];
            mediaRef.current.ondataavailable = e => { if (e.data.size > 0) chunks.current.push(e.data); };
            mediaRef.current.onstop = () => {
                const blob = new Blob(chunks.current, { type: "audio/wav" });
                onVoice(blob);
                setIsRecording(false);
                stream.getTracks().forEach(t => t.stop());
            };
            mediaRef.current.start();
            setIsRecording(true);
        } catch (e) { console.error("Mic access denied", e); alert("Microphone access denied."); }
    };

    return (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-surface via-surface to-transparent pt-10 pb-6 px-4 lg:px-8">
            <div className="max-w-[860px] mx-auto bg-surface-3/90 backdrop-blur-xl border border-glass-border rounded-2xl shadow-[0_-10px_40px_rgba(4,120,87,0.06)] p-2 transition-all focus-within:border-emerald-500/50 focus-within:shadow-[0_-5px_30px_rgba(16,185,129,0.1)] relative">

                {/* Image Preview Area */}
                {imgUrl && (
                    <div className="p-3 border-b border-glass-border flex items-start gap-4">
                        <div className="relative group">
                            <img src={imgUrl} alt="Upload" className="h-20 w-20 object-cover rounded-lg border border-glass-border shadow-sm" />
                            <button onClick={() => setImage(null)} className="absolute -top-2 -right-2 w-6 h-6 bg-surface-2 border border-glass-border text-red-400 rounded-full text-xs flex items-center justify-center hover:bg-red-500/10 transition-colors">✕</button>
                        </div>
                        <div className="text-xs text-emerald-600 pt-2 flex-1">
                            Add a description or question about this image, or just press send to analyze it automatically.
                        </div>
                    </div>
                )}

                <div className="flex items-end gap-2 p-1">
                    {/* Add Image Button */}
                    <button onClick={() => imageRef.current?.click()} disabled={disabled || isRecording} className="p-3 shrink-0 text-emerald-600 hover:text-emerald-400 hover:bg-emerald-900/30 rounded-xl transition-colors disabled:opacity-50">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                        <input type="file" ref={imageRef} hidden accept="image/*" onChange={e => { if (e.target.files?.[0]) setImage(e.target.files[0]); e.target.value = ''; }} />
                    </button>

                    {/* Input/Recording Area */}
                    <div className="flex-1 min-w-0 relative flex items-center">
                        {isRecording ? (
                            <div className="w-full flex items-center justify-center h-10 gap-1.5 text-red-500 animate-pulse-rec bg-red-500/5 rounded-xl border border-red-500/10">
                                <span className="w-2 h-2 rounded-full bg-red-500 flex shrink-0" />
                                <span className="text-sm font-medium">Recording voice... click mic to send</span>
                                <div className="flex items-center gap-0.5 ml-4 h-4">
                                    {[...Array(5)].map((_, i) => <div key={i} className="w-1 bg-red-400/60 rounded-full animate-wave" style={{ animationDelay: `${i * 0.15}s` }} />)}
                                </div>
                            </div>
                        ) : (
                            <textarea
                                value={text}
                                onChange={e => setText(e.target.value)}
                                onKeyDown={handleKeyDown}
                                disabled={disabled}
                                placeholder={image ? "Add details..." : "Ask AgriBot any crop question (English বা বাংলা)..."}
                                className="w-full bg-transparent text-[#f0fdf4] placeholder-emerald-800 resize-none outline-none py-3 px-2 min-h-[44px] max-h-[160px] text-[15px] leading-relaxed block overflow-hidden"
                                style={{ height: '44px' }}
                                rows={1}
                                onInput={e => {
                                    const t = e.target as HTMLTextAreaElement;
                                    t.style.height = '44px';
                                    t.style.height = Math.min(t.scrollHeight, 160) + 'px';
                                }}
                            />
                        )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1 shrink-0 pb-1">
                        {(!text.trim() && !image) ? (
                            <button onClick={toggleVoice} disabled={disabled} className={`p-2.5 rounded-xl transition-all ${isRecording ? "bg-red-500 text-white shadow-[0_0_15px_rgba(239,68,68,0.4)]" : "bg-emerald-900/40 text-emerald-400 hover:bg-emerald-700/50 hover:text-emerald-300"} disabled:opacity-50`}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={isRecording ? "animate-pulse" : ""}><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
                            </button>
                        ) : (
                            <button onClick={handleSubmit} disabled={disabled} className="p-2.5 rounded-xl bg-emerald-600 text-white hover:bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all disabled:opacity-50 disabled:shadow-none translate-y-[-2px]">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                            </button>
                        )}
                    </div>
                </div>

                <div className="absolute -bottom-5 left-0 right-0 text-center text-[10px] text-emerald-800">
                    AgriBot can make mistakes. Verify critical advice.
                </div>
            </div>
        </div>
    );
}
