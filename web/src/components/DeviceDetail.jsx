import { useDevice } from "../hooks/useStaticDevices";
import ScoreBadge from "./ScoreBadge";

export default function DeviceDetail({ deviceId, onBack }) {
  const { device, evidence, safetyEvents, recalls, trials, loading } = useDevice(deviceId);

  if (loading) return <div className="detail-loading">Loading device...</div>;
  if (!device) return <div className="detail-loading">Device not found</div>;

  const directEvidence = evidence.filter((e) => e.match_tier === "direct");
  const companyEvidence = evidence.filter((e) => e.match_tier === "company");
  const ssEvidence = device.evidence_semantic_scholar || [];
  const oaEvidence = device.evidence_openalex || [];
  const regEvidence = device.regulatory_evidence || {};
  const familyEvidence = device.family_evidence || {};
  const denovoSummary = device.denovo_summary || {};
  const clearance = device.clearance_details || {};

  return (
    <div className="device-detail">
      <button onClick={onBack} className="back-btn">&larr; Back to all devices</button>

      <div className="detail-header">
        <h2>{device.device_name}</h2>
        <ScoreBadge score={device.evidence_score} trustLevel={device.trust_level} />
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
        {device.fda_summary_url && (
          <div>
            <a href={device.fda_summary_url} target="_blank" rel="noopener noreferrer" className="fda-link">
              View FDA Summary (PDF)
            </a>
          </div>
        )}
      </div>

      <section className="detail-section">
        <h3>Published Evidence - Direct ({directEvidence.length})</h3>
        <p className="section-note">Studies that directly reference this device by name.</p>
        {directEvidence.length === 0 ? (
          <p className="empty-note">No direct published evidence found.</p>
        ) : (
          <ul className="evidence-list">
            {directEvidence.map((e) => (
              <li key={e.pmid}>
                <a href={`https://pubmed.ncbi.nlm.nih.gov/${e.pmid}/`} target="_blank" rel="noopener noreferrer">
                  {e.title}
                </a>
                <span className="evidence-meta">
                  {e.journal} &middot; {e.pub_date} &middot; {e.study_type}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {companyEvidence.length > 0 && (
        <section className="detail-section">
          <h3>Related Company Research ({companyEvidence.length})</h3>
          <p className="section-note">AI/ML publications by {device.company} in {device.specialty_panel}. May not validate this specific device.</p>
          <ul className="evidence-list evidence-indirect-list">
            {companyEvidence.map((e) => (
              <li key={e.pmid}>
                <a href={`https://pubmed.ncbi.nlm.nih.gov/${e.pmid}/`} target="_blank" rel="noopener noreferrer">
                  {e.title}
                </a>
                <span className="evidence-meta">
                  {e.journal} &middot; {e.pub_date} &middot; {e.study_type}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {ssEvidence.length > 0 && (
        <section className="detail-section">
          <h3>Conference & Preprint Evidence ({ssEvidence.length})</h3>
          <p className="section-note">Found via Semantic Scholar. Includes conference papers, preprints, and non-PubMed sources.</p>
          <ul className="evidence-list">
            {ssEvidence.map((e, idx) => (
              <li key={idx}>
                <span>{e.title}</span>
                <span className="evidence-meta">
                  {e.venue} &middot; {e.year}
                  {e.is_preprint && " (preprint)"}
                  {e.is_conference && " (conference)"}
                  {e.citation_count > 0 && ` \u00B7 ${e.citation_count} citations`}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {oaEvidence.length > 0 && (
        <section className="detail-section">
          <h3>Additional Evidence - OpenAlex ({oaEvidence.length})</h3>
          <p className="section-note">Conferences, preprints, and non-PubMed journals found via OpenAlex.</p>
          <ul className="evidence-list">
            {oaEvidence.map((e, idx) => (
              <li key={idx}>
                <span>{e.title}</span>
                <span className="evidence-meta">
                  {e.venue} &middot; {e.year} &middot; {e.venue_type}
                  {e.citation_count > 0 && ` \u00B7 ${e.citation_count} citations`}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {regEvidence.has_clinical_data && (
        <section className="detail-section">
          <h3>FDA Regulatory Evidence (510(k) Summary)</h3>
          <p className="section-note">Clinical performance data extracted from the FDA 510(k) summary document.</p>
          <div className="reg-evidence">
            {regEvidence.sensitivity && <div><strong>Sensitivity:</strong> {regEvidence.sensitivity}</div>}
            {regEvidence.specificity && <div><strong>Specificity:</strong> {regEvidence.specificity}</div>}
            {regEvidence.auc && <div><strong>AUC:</strong> {regEvidence.auc}</div>}
            {regEvidence.sample_size && <div><strong>Sample Size:</strong> {regEvidence.sample_size}</div>}
            {regEvidence.study_design && <div><strong>Study Design:</strong> {regEvidence.study_design}</div>}
            {regEvidence.ground_truth && <div><strong>Reference Standard:</strong> {regEvidence.ground_truth}</div>}
          </div>
        </section>
      )}

      {familyEvidence.inherited_publication_count > 0 && (
        <section className="detail-section">
          <h3>Related Device Family Evidence</h3>
          <p className="section-note">
            Other devices in the same FDA product code family ({familyEvidence.product_code || device.product_code}) have published evidence.
            These devices share the same intended use classification.
          </p>
          <div className="reg-evidence">
            <div><strong>Family size:</strong> {familyEvidence.family_size} devices</div>
            <div><strong>Siblings with evidence:</strong> {familyEvidence.siblings_with_evidence?.length || 0}</div>
            <div><strong>Inherited publications:</strong> {familyEvidence.inherited_publication_count}</div>
          </div>
        </section>
      )}

      {denovoSummary.indications_for_use && (
        <section className="detail-section">
          <h3>De Novo Decision Summary</h3>
          <p className="section-note">This device was authorized via the De Novo pathway, which requires more evidence than a standard 510(k).</p>
          <div className="reg-evidence">
            <div><strong>Indications:</strong> {denovoSummary.indications_for_use}</div>
            {denovoSummary.sensitivity && <div><strong>Sensitivity:</strong> {denovoSummary.sensitivity}</div>}
            {denovoSummary.specificity && <div><strong>Specificity:</strong> {denovoSummary.specificity}</div>}
            {denovoSummary.sample_size && <div><strong>Sample Size:</strong> {denovoSummary.sample_size}</div>}
            {denovoSummary.clinical_study_summary && <div><strong>Summary:</strong> {denovoSummary.clinical_study_summary}</div>}
          </div>
        </section>
      )}

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

      <section className="detail-section">
        <h3>Clinical Trials ({trials.length})</h3>
        {trials.length === 0 ? (
          <p className="empty-note">No registered clinical trials found.</p>
        ) : (
          <ul className="trial-list">
            {trials.map((t) => (
              <li key={t.nct_id}>
                <a href={`https://clinicaltrials.gov/study/${t.nct_id}`} target="_blank" rel="noopener noreferrer">
                  {t.title}
                </a>
                <span className="trial-meta">
                  {t.status} &middot; {t.sponsor}
                  {t.has_results && " \u2705 Results posted"}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
