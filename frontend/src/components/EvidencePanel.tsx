import { useState } from "react";
import type { EvidenceData } from "../api/types";

interface EvidencePanelProps {
    evidence: EvidenceData;
}

export default function EvidencePanel({ evidence }: EvidencePanelProps) {
    const [isOpen, setIsOpen] = useState(false);

    const {
        citations,
        kg_entities,
        evidence_grade,
        is_verified,
        verification_reason,
        retry_count,
    } = evidence;

    const hasCitations = citations && citations.length > 0;
    const hasEntities = kg_entities && kg_entities.length > 0;

    if (!hasCitations && !hasEntities && evidence_grade === "N/A") {
        return null;
    }

    return (
        <div className="evidence-panel">
            <div className="evidence-header" onClick={() => setIsOpen(!isOpen)}>
                <div className="evidence-header-left">
                    <span>📋</span>
                    <span>Evidence & Citations</span>
                    {hasCitations && (
                        <span className="badge neutral">{citations.length} sources</span>
                    )}
                </div>
                <span className={`evidence-chevron ${isOpen ? "open" : ""}`}>▼</span>
            </div>

            {isOpen && (
                <div className="evidence-body">
                    {/* Badges row */}
                    <div className="evidence-badges">
                        <span
                            className={`badge ${evidence_grade === "SUFFICIENT" ? "sufficient" : "insufficient"
                                }`}
                        >
                            {evidence_grade === "SUFFICIENT" ? "✓" : "⚠"} Evidence:{" "}
                            {evidence_grade}
                        </span>
                        <span
                            className={`badge ${is_verified ? "verified" : "unverified"}`}
                        >
                            {is_verified ? "✓ Verified" : "✗ Unverified"}
                        </span>
                        {retry_count > 0 && (
                            <span className="badge neutral">
                                🔄 {retry_count} {retry_count === 1 ? "retry" : "retries"}
                            </span>
                        )}
                    </div>

                    {/* Verification */}
                    {verification_reason && (
                        <div
                            style={{
                                fontSize: "0.8rem",
                                color: "var(--text-muted)",
                                fontStyle: "italic",
                            }}
                        >
                            {verification_reason}
                        </div>
                    )}

                    {/* Citations */}
                    {hasCitations && (
                        <div>
                            <div
                                style={{
                                    fontSize: "0.75rem",
                                    color: "var(--text-muted)",
                                    marginBottom: "var(--space-sm)",
                                    textTransform: "uppercase",
                                    letterSpacing: "0.5px",
                                    fontWeight: 600,
                                }}
                            >
                                Sources Cited
                            </div>
                            <ul className="citation-list">
                                {citations.map((cit, i) => (
                                    <li key={i} className="citation-item">
                                        <span className="citation-icon">📄</span>
                                        <span>{cit}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* KG Entities */}
                    {hasEntities && (
                        <div>
                            <div
                                style={{
                                    fontSize: "0.75rem",
                                    color: "var(--text-muted)",
                                    marginBottom: "var(--space-sm)",
                                    textTransform: "uppercase",
                                    letterSpacing: "0.5px",
                                    fontWeight: 600,
                                }}
                            >
                                Knowledge Graph
                            </div>
                            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-sm)" }}>
                                {kg_entities.map((ent, i) => (
                                    <div key={i} className="kg-entity">
                                        <span>
                                            <span className="kg-entity-name">{ent.en}</span>
                                            {ent.bn && (
                                                <span style={{ color: "var(--text-muted)", marginLeft: "var(--space-sm)" }}>
                                                    ({ent.bn})
                                                </span>
                                            )}
                                        </span>
                                        <span className="kg-entity-type">{ent.type}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
