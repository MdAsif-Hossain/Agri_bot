import { useState, useRef, useCallback, useEffect } from "react";

interface ChatInputProps {
    onSendText: (query: string) => void;
    onSendVoice: (audioBlob: Blob) => void;
    onSendImage: (file: File, query: string) => void;
    disabled: boolean;
}

export default function ChatInput({
    onSendText,
    onSendVoice,
    onSendImage,
    disabled,
}: ChatInputProps) {
    const [text, setText] = useState("");
    const [imageFile, setImageFile] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [isRecording, setIsRecording] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);

    // Auto-resize textarea
    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = "auto";
            textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
        }
    }, [text]);

    // Handle form submit
    const handleSubmit = useCallback(() => {
        if (disabled) return;

        if (imageFile) {
            onSendImage(imageFile, text.trim());
            setImageFile(null);
            setImagePreview(null);
            setText("");
            return;
        }

        const trimmed = text.trim();
        if (!trimmed) return;
        onSendText(trimmed);
        setText("");
    }, [text, imageFile, disabled, onSendText, onSendImage]);

    // Handle Enter key
    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
            }
        },
        [handleSubmit]
    );

    // Handle image selection
    const handleImageSelect = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const file = e.target.files?.[0];
            if (!file) return;

            setImageFile(file);
            const reader = new FileReader();
            reader.onload = () => setImagePreview(reader.result as string);
            reader.readAsDataURL(file);

            // Reset file input
            e.target.value = "";
        },
        []
    );

    // Remove image
    const removeImage = useCallback(() => {
        setImageFile(null);
        setImagePreview(null);
    }, []);

    // Voice recording
    const startRecording = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
                    ? "audio/webm;codecs=opus"
                    : "audio/webm",
            });

            chunksRef.current = [];
            mediaRecorderRef.current = mediaRecorder;

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) chunksRef.current.push(e.data);
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: "audio/webm" });
                onSendVoice(blob);
                stream.getTracks().forEach((t) => t.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            console.error("Microphone access error:", err);
            alert(
                "Could not access microphone. Please allow microphone permissions."
            );
        }
    }, [onSendVoice]);

    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current?.state === "recording") {
            mediaRecorderRef.current.stop();
        }
        setIsRecording(false);
    }, []);

    const toggleRecording = useCallback(() => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }, [isRecording, startRecording, stopRecording]);

    const hasContent = text.trim().length > 0 || imageFile !== null;

    return (
        <div className="chat-input-area">
            <div className="chat-input-container">
                {/* Image preview */}
                {imagePreview && imageFile && (
                    <div className="image-preview">
                        <img src={imagePreview} alt="Upload preview" />
                        <div className="image-preview-info">
                            <div className="image-preview-name">{imageFile.name}</div>
                            <div className="image-preview-size">
                                {(imageFile.size / 1024).toFixed(1)} KB
                            </div>
                        </div>
                        <button
                            className="image-preview-remove"
                            onClick={removeImage}
                            title="Remove image"
                        >
                            ✕
                        </button>
                    </div>
                )}

                {/* Voice recording indicator */}
                {isRecording && (
                    <div className="voice-indicator">
                        <span className="voice-indicator-dot" />
                        <span>Recording — tap mic to stop</span>
                        <div className="voice-waveform">
                            {[...Array(5)].map((_, i) => (
                                <div key={i} className="voice-bar" />
                            ))}
                        </div>
                    </div>
                )}

                {/* Input row */}
                <div className="chat-input-box">
                    <textarea
                        ref={textareaRef}
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={
                            imageFile
                                ? "Add a question about this image (optional)..."
                                : "Ask about crops, diseases, pests, fertilizers..."
                        }
                        rows={1}
                        disabled={disabled || isRecording}
                    />

                    {/* Voice button */}
                    <button
                        className={`input-action-btn voice-btn ${isRecording ? "recording" : ""
                            }`}
                        onClick={toggleRecording}
                        disabled={disabled}
                        title={isRecording ? "Stop recording" : "Start voice recording"}
                    >
                        {isRecording ? "⏹" : "🎤"}
                    </button>

                    {/* Image button */}
                    <button
                        className="input-action-btn image-btn"
                        disabled={disabled || isRecording}
                        title="Upload crop photo"
                    >
                        📷
                        <input
                            type="file"
                            accept="image/jpeg,image/png,image/jpg"
                            onChange={handleImageSelect}
                            disabled={disabled || isRecording}
                        />
                    </button>

                    {/* Send button */}
                    <button
                        className="input-action-btn send-btn"
                        onClick={handleSubmit}
                        disabled={disabled || (!hasContent && !isRecording)}
                        title="Send message"
                    >
                        ▶
                    </button>
                </div>
            </div>
        </div>
    );
}
