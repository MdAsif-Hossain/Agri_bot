/**
 * VoiceConfirmBanner — inline confirmation UI for low-confidence voice transcription.
 *
 * Shown when the voice endpoint returns needs_confirmation=true.
 * Users can edit the transcript and confirm, or cancel and re-record.
 */

import { useState } from "react";

interface Props {
    transcript: string;
    confidence: number;
    language: string;
    warnings: string[];
    suggestedActions: string[];
    traceId: string;
    onConfirm: (editedText: string, traceId: string) => void;
    onCancel: () => void;
}

export default function VoiceConfirmBanner({
    transcript,
    confidence,
    language,
    warnings,
    suggestedActions,
    traceId,
    onConfirm,
    onCancel,
}: Props) {
    const [editedText, setEditedText] = useState(transcript);

    const confidencePercent = Math.round(confidence * 100);
    const confidenceColor =
        confidence >= 0.6
            ? "var(--color-success, #4caf50)"
            : confidence >= 0.4
              ? "var(--color-warning, #ff9800)"
              : "var(--color-error, #f44336)";

    return (
        <div
            style={{
                background: "var(--color-surface, #fff3cd)",
                border: "1px solid var(--color-border-warning, #ffc107)",
                borderRadius: "12px",
                padding: "16px",
                margin: "8px 0",
                animation: "slideIn 0.3s ease-out",
            }}
        >
            {/* Header */}
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                <span style={{ fontSize: "18px" }}>🎤</span>
                <strong style={{ flex: 1 }}>Voice Transcription — Please Review</strong>
                {/* Confidence pill */}
                <span
                    style={{
                        background: confidenceColor,
                        color: "white",
                        borderRadius: "12px",
                        padding: "2px 10px",
                        fontSize: "12px",
                        fontWeight: 600,
                    }}
                >
                    {confidencePercent}% confidence
                </span>
            </div>

            {/* Language indicator */}
            <div style={{ fontSize: "12px", color: "var(--color-text-muted, #666)", marginBottom: "8px" }}>
                Detected language: <strong>{language === "bn" ? "Bengali 🇧🇩" : language === "en" ? "English" : language}</strong>
                {warnings.length > 0 && (
                    <span style={{ marginLeft: "8px", color: "var(--color-warning, #ff9800)" }}>
                        ⚠ {warnings.join(", ")}
                    </span>
                )}
            </div>

            {/* Editable transcript */}
            <textarea
                id="voice-confirm-transcript"
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                style={{
                    width: "100%",
                    minHeight: "60px",
                    padding: "10px",
                    borderRadius: "8px",
                    border: "1px solid var(--color-border, #ddd)",
                    fontFamily: "inherit",
                    fontSize: "14px",
                    resize: "vertical",
                    marginBottom: "12px",
                    boxSizing: "border-box",
                }}
                placeholder="Edit the transcribed text if needed..."
            />

            {/* Suggested actions */}
            {suggestedActions.length > 0 && (
                <div style={{ fontSize: "12px", color: "var(--color-text-muted, #666)", marginBottom: "12px" }}>
                    💡 {suggestedActions.join(" · ")}
                </div>
            )}

            {/* Action buttons */}
            <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
                <button
                    id="voice-confirm-cancel"
                    onClick={onCancel}
                    style={{
                        padding: "8px 16px",
                        borderRadius: "8px",
                        border: "1px solid var(--color-border, #ccc)",
                        background: "transparent",
                        cursor: "pointer",
                        fontSize: "13px",
                    }}
                >
                    ✕ Cancel
                </button>
                <button
                    id="voice-confirm-submit"
                    onClick={() => onConfirm(editedText, traceId)}
                    disabled={!editedText.trim()}
                    style={{
                        padding: "8px 16px",
                        borderRadius: "8px",
                        border: "none",
                        background: "var(--color-primary, #2196f3)",
                        color: "white",
                        cursor: editedText.trim() ? "pointer" : "not-allowed",
                        fontWeight: 600,
                        fontSize: "13px",
                        opacity: editedText.trim() ? 1 : 0.5,
                    }}
                >
                    ✓ Confirm & Send
                </button>
            </div>
        </div>
    );
}
