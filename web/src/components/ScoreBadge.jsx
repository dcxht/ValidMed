const TRUST_CONFIG = {
  strong:   { bg: "#dcfce7", text: "#166534", border: "#86efac", label: "Strong Evidence" },
  moderate: { bg: "#dbeafe", text: "#1e40af", border: "#93c5fd", label: "Some Evidence" },
  limited:  { bg: "#fef9c3", text: "#854d0e", border: "#fde047", label: "Limited Evidence" },
  none:     { bg: "#fee2e2", text: "#991b1b", border: "#fca5a5", label: "No Evidence" },
};

export default function ScoreBadge({ score, trustLevel }) {
  const level = trustLevel || "none";
  const c = TRUST_CONFIG[level] || TRUST_CONFIG.none;

  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 10px",
        borderRadius: "9999px",
        fontSize: "12px",
        fontWeight: 600,
        background: c.bg,
        color: c.text,
        border: `1px solid ${c.border}`,
        whiteSpace: "nowrap",
      }}
    >
      {c.label}
    </span>
  );
}
