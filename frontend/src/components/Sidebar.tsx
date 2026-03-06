import { useState, useEffect } from "react";
import { getHealth } from "../api/client";
import type { HealthResponse } from "../api/types";

const FEATURES = [
    { icon: "🔍", label: "Hybrid Retrieval (FAISS + BM25)" },
    { icon: "⚖️", label: "Cross-Encoder Reranking" },
    { icon: "🌿", label: "Dialect Knowledge Graph" },
    { icon: "🔄", label: "Self-Correcting Agent Loop" },
    { icon: "✅", label: "Answer Verification" },
    { icon: "🎤", label: "Voice Input (Whisper ASR)" },
    { icon: "🔊", label: "Voice Output (TTS)" },
    { icon: "📷", label: "Image Analysis (VLM)" },
];

interface SidebarProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
    const [health, setHealth] = useState<HealthResponse | null>(null);
    const [healthStatus, setHealthStatus] = useState<
        "loading" | "online" | "offline"
    >("loading");

    useEffect(() => {
        let mounted = true;

        async function checkHealth() {
            try {
                const data = await getHealth();
                if (mounted) {
                    setHealth(data);
                    setHealthStatus("online");
                }
            } catch {
                if (mounted) setHealthStatus("offline");
            }
        }

        checkHealth();
        const interval = setInterval(checkHealth, 30_000);

        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, []);

    return (
        <>
            {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
            <aside className={`sidebar ${isOpen ? "open" : ""}`}>
                {/* Brand */}
                <div className="sidebar-brand">
                    <div className="sidebar-brand-icon">🌾</div>
                    <div>
                        <h1>AgriBot</h1>
                        <p>Agricultural Advisory</p>
                    </div>
                </div>

                {/* Health */}
                <div className="sidebar-section">
                    <div className="sidebar-section-title">System Status</div>
                    <div className={`health-badge ${healthStatus}`}>
                        <span className="health-dot" />
                        {healthStatus === "loading"
                            ? "Connecting..."
                            : healthStatus === "online"
                                ? "Online"
                                : "Offline"}
                    </div>
                </div>

                {/* Stats */}
                {health && (
                    <div className="sidebar-section">
                        <div className="sidebar-section-title">Knowledge Base</div>
                        <div className="stats-grid">
                            <div className="stat-card">
                                <div className="stat-value">{health.chunk_count}</div>
                                <div className="stat-label">📄 Chunks</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">{health.kg_entities}</div>
                                <div className="stat-label">🔗 Entities</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">{health.kg_aliases}</div>
                                <div className="stat-label">📝 Aliases</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">{health.kg_relations}</div>
                                <div className="stat-label">🔀 Relations</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Features */}
                <div className="sidebar-section" style={{ flex: 1 }}>
                    <div className="sidebar-section-title">Capabilities</div>
                    <ul className="feature-list">
                        {FEATURES.map((f) => (
                            <li key={f.label} className="feature-item">
                                <span className="feature-icon">{f.icon}</span>
                                {f.label}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Footer */}
                <div
                    style={{
                        fontSize: "0.7rem",
                        color: "var(--text-muted)",
                        textAlign: "center",
                    }}
                >
                    Offline-first • RTX 3050 Optimized
                </div>
            </aside>
        </>
    );
}
