import { useState, useCallback } from "react";
import { getTTSAudio } from "../api/client";
import EvidencePanel from "./EvidencePanel";
import type { Message } from "../api/types";

interface ChatMessageProps {
    message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
    const { role, content, answer_bn, input_mode, evidence } = message;
    const [activeTab, setActiveTab] = useState<"en" | "bn">("en");
    const [ttsLoading, setTtsLoading] = useState<string | null>(null);

    const handleTTS = useCallback(
        async (text: string, language: "en" | "bn") => {
            const key = `${language}-${message.id}`;
            if (ttsLoading) return;
            setTtsLoading(key);
            try {
                const audioUrl = await getTTSAudio({ text, language });
                const audio = new Audio(audioUrl);
                audio.play();
                audio.onended = () => URL.revokeObjectURL(audioUrl);
            } catch (err) {
                console.error("TTS error:", err);
            } finally {
                setTtsLoading(null);
            }
        },
        [message.id, ttsLoading]
    );

    const modeLabel =
        input_mode === "voice"
            ? "🎤 Voice"
            : input_mode === "image"
                ? "📷 Image"
                : null;

    if (role === "user") {
        return (
            <div className="message user">
                <div className="message-avatar">👤</div>
                <div className="message-body">
                    {modeLabel && (
                        <div className="message-input-mode">{modeLabel}</div>
                    )}
                    <div className="message-bubble">{content}</div>
                </div>
            </div>
        );
    }

    // Assistant message
    const hasBengali = answer_bn && answer_bn.trim().length > 0;
    const displayContent = activeTab === "bn" && hasBengali ? answer_bn : content;

    return (
        <div className="message assistant">
            <div className="message-avatar">🌾</div>
            <div className="message-body">
                {hasBengali && (
                    <div className="lang-tabs">
                        <button
                            className={`lang-tab ${activeTab === "en" ? "active" : ""}`}
                            onClick={() => setActiveTab("en")}
                        >
                            🇬🇧 English
                        </button>
                        <button
                            className={`lang-tab ${activeTab === "bn" ? "active" : ""}`}
                            onClick={() => setActiveTab("bn")}
                        >
                            🇧🇩 বাংলা
                        </button>
                    </div>
                )}

                <div className="message-bubble">
                    {displayContent.split("\n").map((line, i) => (
                        <span key={i}>
                            {line}
                            {i < displayContent.split("\n").length - 1 && <br />}
                        </span>
                    ))}
                </div>

                {/* TTS Buttons */}
                <div className="message-actions">
                    <button
                        className="tts-btn"
                        onClick={() => handleTTS(content, "en")}
                        disabled={ttsLoading !== null}
                    >
                        🔊 {ttsLoading === `en-${message.id}` ? "Playing..." : "Read EN"}
                    </button>
                    {hasBengali && (
                        <button
                            className="tts-btn"
                            onClick={() => handleTTS(answer_bn!, "bn")}
                            disabled={ttsLoading !== null}
                        >
                            🔊{" "}
                            {ttsLoading === `bn-${message.id}` ? "Playing..." : "Read BN"}
                        </button>
                    )}
                </div>

                {/* Evidence Panel */}
                {evidence && <EvidencePanel evidence={evidence} />}
            </div>
        </div>
    );
}
