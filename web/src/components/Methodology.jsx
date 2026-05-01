export default function Methodology({ onBack }) {
  return (
    <div className="methodology">
      <button className="back-btn" onClick={onBack}>
        &larr; Back to devices
      </button>

      <h2 className="methodology-title">About ValidMed</h2>

      <section className="methodology-section">
        <h3>What is VALIDMed?</h3>
        <p>
          ValidMed is an independent transparency tool that analyzes the clinical
          claims and validation evidence reported in FDA 510(k) submissions for
          AI/ML-enabled medical devices. For each of 1,430 FDA-cleared devices,
          we extract what the manufacturer claims the device does and what evidence
          they provided to support those claims.
        </p>
        <p>
          The core question: <strong>Is the evidence proportional to the claims?</strong> A
          device that claims to triage stroke patients should have stronger evidence
          than one that enhances image quality. ValidMed makes this relationship visible.
        </p>
        <p>
          This tool is not affiliated with or endorsed by the FDA. It is intended for
          researchers, clinicians, hospital administrators, and policymakers evaluating
          AI/ML device adoption.
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
                Official catalog of 1,430 AI/ML-enabled devices authorized for
                marketing in the US, including device name, company, clearance date,
                specialty panel, and product code.
              </td>
            </tr>
            <tr>
              <td>510(k) Summary PDFs</td>
              <td>
                Manufacturer-submitted documents describing device intended use,
                clinical claims, validation study design, and performance metrics.
                Downloaded from FDA AccessData for 1,301 devices.
              </td>
            </tr>
            <tr>
              <td>openFDA MAUDE</td>
              <td>
                Adverse event reports including deaths, injuries, and malfunctions
                reported to the FDA by manufacturers and users.
              </td>
            </tr>
            <tr>
              <td>openFDA Recalls</td>
              <td>
                Device recall records including reason, status, and root cause.
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="methodology-section">
        <h3>Claims Extraction Methodology</h3>
        <p>
          For each device with an available 510(k) summary PDF, we use an LLM
          (Claude Haiku, Anthropic) to extract structured data from the document text.
          The extraction is supplemented by regex-based pattern matching to capture
          performance metrics the LLM may miss in longer documents.
        </p>

        <h4 style={{fontSize: "14px", marginTop: "16px", marginBottom: "8px"}}>What we extract:</h4>
        <ul className="methodology-list">
          <li>
            <strong>Intended use statement</strong> -- the verbatim regulatory language
            describing what the device is cleared to do.
          </li>
          <li>
            <strong>Claim category</strong> -- classified into six tiers of increasing
            clinical impact: Enhancement, Quantification, Detection, Triage, Diagnosis,
            Treatment. Classification is based on the highest applicable function
            described in the intended use.
          </li>
          <li>
            <strong>Validation design</strong> -- the strongest study design described
            in the submission: None, Bench Testing Only, Retrospective Single-Site,
            Retrospective Multi-Site, Prospective Single-Site, Prospective Multi-Site, or RCT.
          </li>
          <li>
            <strong>Performance metrics</strong> -- sensitivity, specificity, AUC, PPV, NPV,
            accuracy, and sample size, extracted exactly as reported.
          </li>
          <li>
            <strong>Additional fields</strong> -- autonomous vs. assistive designation,
            target condition, ground truth method, number of sites, and stated limitations.
          </li>
        </ul>

        <h4 style={{fontSize: "14px", marginTop: "16px", marginBottom: "8px"}}>Important distinction:</h4>
        <p>
          "Bench testing" means the algorithm was tested on a dataset of images or cases
          offline, even if sourced from multiple institutions. This is different from a
          clinical study where the device was tested in an actual clinical workflow.
          Many 510(k) submissions describe bench testing but do not include clinical
          validation studies.
        </p>
      </section>

      <section className="methodology-section">
        <h3>Proportionality Analysis</h3>
        <p>
          The core analysis maps each device's claim tier against its evidence tier to
          identify proportionality gaps. Devices in the <strong>"concern zone"</strong> are
          those making high-impact clinical claims (detection, triage, diagnosis, or
          treatment) while reporting only bench testing or no validation data in their
          510(k) submission.
        </p>
        <p>
          This framework responds to the April 2026 Nature Medicine editorial calling for
          evidence standards that "systematically and consistently link claims of impact
          to appropriate, proportional evidence."
        </p>
      </section>

      <section className="methodology-section">
        <h3>Validation</h3>
        <p>
          LLM extraction accuracy was validated against a stratified random sample of
          150 devices reviewed by a human annotator who read the original 510(k) PDFs.
          Inter-rater agreement (Cohen's kappa) is reported for claim category and
          validation design classifications separately.
        </p>
        <p>
          A regex-based backstop independently extracts performance metrics (sensitivity,
          specificity, AUC, sample size) to catch data the LLM misses, particularly in
          longer documents where relevant metrics appear beyond the LLM's focus window.
        </p>
      </section>

      <section className="methodology-section">
        <h3>Known Limitations</h3>
        <ul className="methodology-list">
          <li>
            <strong>510(k) summaries vary in detail.</strong> Some contain comprehensive
            clinical data; others are brief descriptions with minimal performance information.
            The absence of data in the summary does not necessarily mean no evidence exists
            in the full submission.
          </li>
          <li>
            <strong>LLM extraction is not perfect.</strong> Automated extraction may
            misclassify claims or validation designs. All classifications should be verified
            against the original 510(k) summary, which is linked for each device.
          </li>
          <li>
            <strong>510(k) clearance does not require published evidence.</strong> The
            510(k) pathway requires demonstration of substantial equivalence to a predicate
            device, not peer-reviewed clinical studies. A device with no published evidence
            may still be legally marketed.
          </li>
          <li>
            <strong>Safety data depends on voluntary reporting.</strong> MAUDE adverse event
            reports are known to undercount actual events. The absence of reports does not
            guarantee safety.
          </li>
          <li>
            <strong>No independent literature matching.</strong> ValidMed currently analyzes
            what manufacturers report in their FDA submissions. It does not systematically
            link devices to independently published peer-reviewed validation studies, as
            automated literature-device matching remains an open methodological challenge.
          </li>
          <li>
            <strong>Data freshness.</strong> The analysis reflects FDA data as of December
            2025 and 510(k) summaries available at the time of download. Newly cleared
            devices or updated submissions may not be reflected.
          </li>
        </ul>
      </section>

      <section className="methodology-section">
        <h3>Open Source</h3>
        <p>
          The complete extraction pipeline, data processing code, and dashboard source
          are available on{" "}
          <a href="https://github.com/dcxht/ValidMed" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
          . Code generation was assisted by{" "}
          <a href="https://claude.ai/code" target="_blank" rel="noopener noreferrer">
            Claude Code
          </a>
          .
        </p>
      </section>

      <section className="methodology-section">
        <h3>Citation</h3>
        <p>If referencing ValidMed in academic work, please cite:</p>
        <div className="citation-block">
          ValidMed: Verified AI Literature & Intelligence Database for Medical Devices.
          Available at: https://validmed.org. Accessed: [date].
        </div>
      </section>

      <section className="methodology-section">
        <h3>Contact</h3>
        <p>
          For questions, corrections, or collaboration inquiries, please use the
          GitHub repository or email chet@validmed.org. If you believe a device's
          claims or evidence are miscategorized, we welcome corrections.
        </p>
      </section>
    </div>
  );
}
