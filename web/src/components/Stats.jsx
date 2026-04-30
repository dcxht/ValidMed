export default function Stats({ devices }) {
  if (!devices || devices.length === 0) return null;

  const total = devices.length;
  const concernZone = devices.filter((d) => d.is_concern_zone).length;
  const benchOnly = devices.filter((d) => d.validation_design === "none" || d.validation_design === "bench_only").length;
  const hasMetrics = devices.filter((d) => d.sensitivity != null || d.specificity != null || d.auc != null).length;
  const hasEvents = devices.filter((d) => d.safety_event_count > 0).length;
  const hasRecalls = devices.filter((d) => d.recall_count > 0).length;

  const stats = [
    { label: "Total FDA-Cleared AI Devices", value: total.toLocaleString() },
    { label: "In Concern Zone", value: `${concernZone} (${((concernZone / total) * 100).toFixed(1)}%)`, alert: true },
    { label: "Bench Testing Only", value: `${benchOnly} (${((benchOnly / total) * 100).toFixed(0)}%)` },
    { label: "Has Performance Metrics", value: `${hasMetrics} (${((hasMetrics / total) * 100).toFixed(0)}%)` },
    { label: "Adverse Events / Recalls", value: `${hasEvents} / ${hasRecalls}` },
  ];

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
