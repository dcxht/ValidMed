const CLAIM_CONFIG = {
  enhancement:    { bg: "#dcfce7", text: "#166534", border: "#86efac", label: "Enhancement" },
  quantification: { bg: "#dbeafe", text: "#1e40af", border: "#93c5fd", label: "Quantification" },
  detection:      { bg: "#fef9c3", text: "#854d0e", border: "#fde047", label: "Detection" },
  triage:         { bg: "#ffedd5", text: "#9a3412", border: "#fdba74", label: "Triage" },
  diagnosis:      { bg: "#fee2e2", text: "#991b1b", border: "#fca5a5", label: "Diagnosis" },
  treatment:      { bg: "#fee2e2", text: "#991b1b", border: "#fca5a5", label: "Treatment" },
};

const EVIDENCE_CONFIG = {
  none:                 { bg: "#fee2e2", text: "#991b1b", border: "#fca5a5", label: "No Evidence" },
  bench_only:           { bg: "#ffedd5", text: "#9a3412", border: "#fdba74", label: "Bench Only" },
  retrospective_single: { bg: "#fef9c3", text: "#854d0e", border: "#fde047", label: "Retro (Single)" },
  retrospective_multi:  { bg: "#fef9c3", text: "#854d0e", border: "#fde047", label: "Retro (Multi)" },
  prospective_single:   { bg: "#dcfce7", text: "#166534", border: "#86efac", label: "Prospective" },
  prospective_multi:    { bg: "#dcfce7", text: "#166534", border: "#86efac", label: "Prospective (Multi)" },
  rct:                  { bg: "#dcfce7", text: "#166534", border: "#86efac", label: "RCT" },
};

const BADGE_STYLE = {
  display: "inline-block",
  padding: "2px 10px",
  borderRadius: "9999px",
  fontSize: "12px",
  fontWeight: 600,
  whiteSpace: "nowrap",
};

export function ClaimBadge({ claimCategory }) {
  if (!claimCategory || claimCategory === "no_pdf" || claimCategory === "assistive") return <span style={{ ...BADGE_STYLE, background: "#f3f4f6", color: "#6b7280", border: "1px solid #d1d5db" }}>{claimCategory === "no_pdf" ? "No PDF" : claimCategory === "assistive" ? "Assistive" : "N/A"}</span>;
  const c = CLAIM_CONFIG[claimCategory] || CLAIM_CONFIG.enhancement;
  return (
    <span style={{ ...BADGE_STYLE, background: c.bg, color: c.text, border: `1px solid ${c.border}` }}>
      {c.label}
    </span>
  );
}

export function EvidenceBadge({ validationDesign }) {
  if (!validationDesign || validationDesign === "no_pdf") return <span style={{ ...BADGE_STYLE, background: "#f3f4f6", color: "#6b7280", border: "1px solid #d1d5db" }}>{validationDesign === "no_pdf" ? "No PDF" : "N/A"}</span>;
  const c = EVIDENCE_CONFIG[validationDesign] || EVIDENCE_CONFIG.none;
  return (
    <span style={{ ...BADGE_STYLE, background: c.bg, color: c.text, border: `1px solid ${c.border}` }}>
      {c.label}
    </span>
  );
}

// Default export for backward compat (not used anymore but safe)
export default function ScoreBadge({ claimCategory, validationDesign }) {
  return (
    <span style={{ display: "inline-flex", gap: "6px", alignItems: "center" }}>
      <ClaimBadge claimCategory={claimCategory} />
      <EvidenceBadge validationDesign={validationDesign} />
    </span>
  );
}
