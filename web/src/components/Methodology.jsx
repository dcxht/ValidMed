export default function Methodology({ onBack }) {
  return (
    <div className="methodology">
      <button className="back-btn" onClick={onBack}>
        &larr; Back to devices
      </button>

      <h2 className="methodology-title">About ValidMed</h2>

      <section className="methodology-section">
        <h3>What is ValidMed?</h3>
        <p>
          ValidMed (Verified AI Literature & Intelligence Database for Medical Devices) is an
          independent transparency tool that tracks the published evidence base for
          FDA-cleared AI/ML-enabled medical devices. The FDA maintains a list of authorized
          AI/ML devices but does not require manufacturers to publish peer-reviewed clinical
          evidence before clearance. ValidMed exists to make visible which devices have
          robust supporting research and which do not.
        </p>
        <p>
          This tool is not affiliated with or endorsed by the FDA. It is intended for
          researchers, clinicians, administrators, and policymakers who need to evaluate
          the evidence behind AI/ML devices used in patient care.
        </p>
      </section>

      <section className="methodology-section">
        <h3>Data Sources</h3>
        <table className="methodology-table">
          <thead>
            <tr>
              <th>Source</th>
              <th>What it provides</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>FDA AI/ML Device List</td>
              <td>
                Canonical list of cleared/authorized AI/ML-enabled devices, including device
                name, company, decision date, regulatory pathway (510(k), De Novo, PMA), and
                medical specialty panel.
              </td>
            </tr>
            <tr>
              <td>PubMed (NCBI)</td>
              <td>
                Peer-reviewed publications referencing the device or the manufacturer's
                research in the relevant clinical domain.
              </td>
            </tr>
            <tr>
              <td>openFDA MAUDE</td>
              <td>
                Manufacturer and User Facility Device Experience reports — adverse events
                including deaths, injuries, and malfunctions reported to the FDA.
              </td>
            </tr>
            <tr>
              <td>ClinicalTrials.gov</td>
              <td>
                Registered clinical trials involving the device, including trial status and
                whether results have been posted.
              </td>
            </tr>
            <tr>
              <td>Semantic Scholar</td>
              <td>
                Broader academic coverage including conference papers, preprints, and
                publications in venues not indexed by PubMed.
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="methodology-section">
        <h3>Evidence Search Methodology</h3>
        <p>
          Evidence is gathered through a multi-tier search strategy designed to balance
          precision (avoiding false matches) with recall (finding all relevant work):
        </p>
        <div className="tier-list">
          <div className="tier-item">
            <div className="tier-badge tier-direct">Tier 1: Direct Match</div>
            <p>
              The exact device name (cleaned of version numbers and model identifiers) is
              searched in PubMed title/abstract fields. Results at this tier have high
              confidence of relevance to the specific device.
            </p>
          </div>
          <div className="tier-item">
            <div className="tier-badge tier-direct">Tier 2: Company + Device</div>
            <p>
              When Tier 1 yields fewer than 5 results, a combined search is performed using
              the company name in the affiliation field and the device name in title/abstract.
              This captures papers where the device is referenced under a different name or
              abbreviation. Results are still tagged as "direct" evidence.
            </p>
          </div>
          <div className="tier-item">
            <div className="tier-badge tier-company">Tier 3: Company Research</div>
            <p>
              When fewer than 3 direct results are found, a broader search combines the
              company name with specialty-specific terms and AI/ML keywords. Results are
              tagged as "company-tier" evidence. These may not reference the specific device
              but represent the manufacturer's published research in the relevant domain.
              Post-filtering ensures titles contain AI/ML-related keywords.
            </p>
          </div>
          <div className="tier-item">
            <div className="tier-badge tier-conference">Tier 4: Conference / Preprint</div>
            <p>
              Semantic Scholar is queried to capture conference papers (e.g., MICCAI, RSNA,
              ISBI) and preprints (e.g., arXiv, medRxiv) that reference the device. These
              venues are important in medical AI but are not indexed by PubMed. Results are
              displayed separately and clearly labeled.
            </p>
          </div>
        </div>
      </section>

      <section className="methodology-section">
        <h3>Evidence Categorization</h3>
        <p>Each piece of evidence is categorized to help users assess its relevance:</p>
        <ul className="methodology-list">
          <li>
            <strong>Direct evidence</strong> — publications that explicitly mention the
            device by name. Highest confidence of relevance.
          </li>
          <li>
            <strong>Company-tier evidence</strong> — publications from the same manufacturer
            in the same clinical domain, involving AI/ML methods. May describe underlying
            algorithms or earlier versions. Displayed with reduced prominence.
          </li>
          <li>
            <strong>Conference / preprint evidence</strong> — academic work from Semantic
            Scholar that may not have undergone full peer review. Displayed separately with
            clear labeling.
          </li>
        </ul>
        <p>
          Study types are classified where possible (RCT, clinical trial, meta-analysis,
          systematic review, case report, etc.) based on PubMed publication type metadata.
        </p>
      </section>

      <section className="methodology-section">
        <h3>Scoring Methodology</h3>
        <p>
          Each device receives a transparent evidence score from 0 to 100, composed of five
          independently calculated components:
        </p>
        <table className="methodology-table">
          <thead>
            <tr>
              <th>Component</th>
              <th>Max Points</th>
              <th>How it is calculated</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Evidence Volume</td>
              <td>40</td>
              <td>
                Based on number of publications found: 0 publications = 0 pts, 1-2 = 10 pts,
                3-5 = 20 pts, 6-10 = 30 pts, 11+ = 40 pts.
              </td>
            </tr>
            <tr>
              <td>Study Quality</td>
              <td>20</td>
              <td>
                Based on the highest-quality study type found. RCTs score highest (10),
                followed by meta-analyses (8), clinical trials (7), systematic reviews (6).
                The best study type score is doubled, capped at 20.
              </td>
            </tr>
            <tr>
              <td>Independence</td>
              <td>15</td>
              <td>
                Whether evidence includes independent (non-manufacturer) validation. 3+
                independent studies = 15 pts, 1-2 = 8 pts, none = 0 pts.
              </td>
            </tr>
            <tr>
              <td>Safety Record</td>
              <td>15</td>
              <td>
                Starts at 15 and deducts for adverse events. Deaths: -5 each (max -10).
                Injuries: -2 each (max -5). Recalls: -3 each (max -6). Floor of 0.
              </td>
            </tr>
            <tr>
              <td>Clinical Trials</td>
              <td>10</td>
              <td>
                Registered trial with posted results = 10 pts. Completed trial without
                results = 6 pts. Registered but not completed = 3 pts. None = 0 pts.
              </td>
            </tr>
          </tbody>
        </table>
        <p className="methodology-note">
          The score is intended as a rough heuristic for evidence availability, not a
          definitive quality judgment. A low score may reflect a recently cleared device
          that has not yet accumulated published evidence, not necessarily a problematic one.
        </p>
      </section>

      <section className="methodology-section">
        <h3>Known Limitations</h3>
        <ul className="methodology-list">
          <li>
            <strong>PubMed coverage is incomplete.</strong> Many important medical AI
            publications appear exclusively at conferences (MICCAI, RSNA, ISBI, NeurIPS)
            or on preprint servers. Semantic Scholar helps bridge this gap but may still miss
            some work.
          </li>
          <li>
            <strong>Device name matching is imperfect.</strong> Some devices have generic
            names (e.g., "AI Suite") that produce noisy search results. Very short or
            common names are excluded from search. Manufacturer rebranding can cause
            missed matches.
          </li>
          <li>
            <strong>510(k) clearance does not require published evidence.</strong> Most
            AI/ML devices are cleared via the 510(k) pathway, which requires demonstration
            of substantial equivalence to a predicate device but does not mandate
            peer-reviewed clinical studies. A device with zero publications may still be
            legally marketed.
          </li>
          <li>
            <strong>Company-tier evidence may not be device-specific.</strong> Publications
            tagged as "company" match the manufacturer's research domain but may describe
            different products or general methodological work.
          </li>
          <li>
            <strong>Safety data depends on voluntary reporting.</strong> MAUDE reports are
            known to undercount actual adverse events. The absence of reports does not
            guarantee safety.
          </li>
          <li>
            <strong>Scoring is a simplification.</strong> No single number can capture the
            full nuance of a device's evidence base. The component breakdown is provided
            for transparency, and users should examine the underlying evidence directly.
          </li>
          <li>
            <strong>Data freshness.</strong> The pipeline runs periodically but is not
            real-time. Recently published studies or newly reported events may not yet be
            reflected.
          </li>
        </ul>
      </section>

      <section className="methodology-section">
        <h3>Citation</h3>
        <p>If referencing ValidMed in academic work, please cite:</p>
        <div className="citation-block">
          ValidMed: Verified AI Literature & Intelligence Database for Medical Devices.
          Available at: [URL]. Accessed: [date].
        </div>
      </section>

      <section className="methodology-section">
        <h3>Contact</h3>
        <p>
          For questions, corrections, or collaboration inquiries, reach out via the project
          repository or email. If you believe a device's evidence is miscategorized or
          missing, we welcome corrections.
        </p>
      </section>
    </div>
  );
}
