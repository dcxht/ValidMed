import { useDevice } from "../hooks/useStaticDevices";
import { ClaimBadge, EvidenceBadge } from "./ScoreBadge";

const VALIDATION_LABELS = {
  none: "no validation",
  bench_only: "bench-only",
  retrospective_single: "single-site retrospective",
  retrospective_multi: "multi-site retrospective",
  prospective_single: "single-site prospective",
  prospective_multi: "multi-site prospective",
  rct: "RCT",
};

export default function DeviceDetail({ deviceId, onBack }) {
  const { device, safetyEvents, recalls, loading } = useDevice(deviceId);

  if (loading) return <div className="detail-loading">Loading device...</div>;
  if (!device) return <div className="detail-loading">Device not found</div>;

  const clearance = device.clearance_details || {};

  return (
    <div className="device-detail">
      <button onClick={onBack} className="back-btn">&larr; Back to all devices</button>

      <div className="detail-header">
        <h2>{device.device_name}</h2>
        <span style={{ display: "inline-flex", gap: "6px", alignItems: "center" }}>
          <ClaimBadge claimCategory={device.claim_category} />
          <EvidenceBadge validationDesign={device.validation_design} />
        </span>
      </div>

      <div className="detail-meta">
        <div><strong>Company:</strong> {device.company}</div>
        {device.clinical_use_case && <div><strong>Use Case:</strong> {device.clinical_use_case}</div>}
        <div><strong>Submission:</strong> {device.fda_submission_number}</div>
        <div><strong>Cleared:</strong> {device.decision_date}
          {device.years_since_clearance != null && (
            <span className="meta-note"> ({device.years_since_clearance} yrs ago)</span>
          )}
        </div>
        <div><strong>Specialty:</strong> {device.specialty_panel}</div>
        <div><strong>Product Code:</strong> {device.product_code}</div>
        {device.device_class && <div><strong>Device Class:</strong> {device.device_class}</div>}
        {clearance.clearance_type && <div><strong>Clearance Type:</strong> {clearance.clearance_type}</div>}
        {device.autonomous_or_assistive && <div><strong>Mode:</strong> {device.autonomous_or_assistive === "autonomous" ? "Autonomous" : "Assistive"}</div>}
        {device.fda_summary_url && (
          <div>
            <a href={device.fda_summary_url} target="_blank" rel="noopener noreferrer" className="fda-link">
              View FDA Summary (PDF)
            </a>
          </div>
        )}
      </div>

      {/* Concern Zone Warning */}
      {device.is_concern_zone && (
        <div className="concern-banner">
          This device makes <strong>{device.claim_category}</strong> claims with only <strong>{VALIDATION_LABELS[device.validation_design] || device.validation_design}</strong> validation data.
        </div>
      )}

      {/* FDA Submission Claims Section */}
      <section className="detail-section">
        <h3>FDA Submission Claims</h3>
        <p className="section-note">Clinical claims and validation evidence extracted from the 510(k) summary PDF.</p>

        {(device.intended_use_full || device.intended_use) && (
          <div style={{ marginBottom: "12px" }}>
            <strong style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Intended Use</strong>
            <p style={{ fontSize: "14px", marginTop: "4px", lineHeight: "1.6" }}>
              {device.intended_use_full || device.intended_use}
            </p>
          </div>
        )}

        <div className="reg-evidence">
          {device.claim_category && <div><strong>Claim Category:</strong> <ClaimBadge claimCategory={device.claim_category} /></div>}
          {device.validation_design && <div><strong>Validation Design:</strong> <EvidenceBadge validationDesign={device.validation_design} /></div>}
          {device.sensitivity != null && <div><strong>Sensitivity:</strong> {device.sensitivity}</div>}
          {device.specificity != null && <div><strong>Specificity:</strong> {device.specificity}</div>}
          {device.auc != null && <div><strong>AUC:</strong> {device.auc}</div>}
          {device.sample_size != null && <div><strong>Sample Size:</strong> {device.sample_size.toLocaleString()}</div>}
          {device.num_sites != null && <div><strong>Number of Sites:</strong> {device.num_sites}</div>}
          {device.autonomous_or_assistive && <div><strong>Mode:</strong> {device.autonomous_or_assistive === "autonomous" ? "Autonomous" : "Assistive"}</div>}
        </div>

        {device.target_condition && (
          <div style={{ marginTop: "12px" }}>
            <strong style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Target Condition</strong>
            <p style={{ fontSize: "14px", marginTop: "4px" }}>{device.target_condition}</p>
          </div>
        )}

        {device.ground_truth && (
          <div style={{ marginTop: "12px" }}>
            <strong style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Reference Standard</strong>
            <p style={{ fontSize: "14px", marginTop: "4px" }}>{device.ground_truth}</p>
          </div>
        )}

        {device.other_metrics && (
          <div style={{ marginTop: "12px" }}>
            <strong style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Other Metrics</strong>
            <p style={{ fontSize: "14px", marginTop: "4px" }}>{device.other_metrics}</p>
          </div>
        )}
      </section>

      <section className="detail-section">
        <h3>Safety Events ({safetyEvents.length})</h3>
        {safetyEvents.length === 0 ? (
          <p className="empty-note">No adverse events reported in MAUDE.</p>
        ) : (
          <ul className="safety-list">
            {safetyEvents.map((e) => (
              <li key={e.report_number}>
                <span className={`event-type event-${e.event_type?.toLowerCase()}`}>
                  {e.event_type}
                </span>
                <span className="event-date">{e.date_of_event}</span>
                <p className="event-narrative">{e.narrative_text?.slice(0, 300)}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="detail-section">
        <h3>Recalls ({recalls.length})</h3>
        {recalls.length === 0 ? (
          <p className="empty-note">No recalls on record.</p>
        ) : (
          <ul className="recall-list">
            {recalls.map((r) => (
              <li key={r.recall_number}>
                <strong>{r.status}</strong> &middot; {r.date_initiated}
                <p>{r.reason}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
