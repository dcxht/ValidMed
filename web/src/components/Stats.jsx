export default function Stats({ devices }) {
  if (!devices || devices.length === 0) return null;

  const total = devices.length;
  const noPublished = devices.filter((d) => (d.evidence_total ?? d.evidence_count) === 0).length;
  const noAnyEvidence = devices.filter((d) => !d.any_evidence).length;
  const hasEvents = devices.filter((d) => d.safety_event_count > 0).length;
  const hasRecalls = devices.filter((d) => d.recall_count > 0).length;

  // Temporal: devices cleared 2+ years ago with no evidence
  const mature = devices.filter((d) => d.years_since_clearance >= 2);
  const matureNoPublished = mature.filter((d) => (d.evidence_total ?? d.evidence_count) === 0).length;

  const stats = [
    { label: "FDA-Cleared AI Devices", value: total },
    { label: "No Published Evidence", value: `${noPublished} (${((noPublished / total) * 100).toFixed(0)}%)`, alert: true },
    { label: "No Evidence (Any Source)", value: `${noAnyEvidence} (${((noAnyEvidence / total) * 100).toFixed(0)}%)`, alert: noAnyEvidence / total > 0.2 },
    { label: "Safety Events / Recalls", value: `${hasEvents} / ${hasRecalls}` },
  ];

  if (mature.length > 0) {
    stats.push({
      label: "Cleared 2+ Yrs, No Published Evidence",
      value: `${matureNoPublished}/${mature.length} (${((matureNoPublished / mature.length) * 100).toFixed(0)}%)`,
      alert: matureNoPublished / mature.length > 0.2,
    });
  }

  return (
    <div className="stats-bar">
      {stats.map((s) => (
        <div key={s.label} className={`stat-card ${s.alert ? "stat-alert" : ""}`}>
          <div className="stat-value">{s.value}</div>
          <div className="stat-label">{s.label}</div>
        </div>
      ))}
    </div>
  );
}
