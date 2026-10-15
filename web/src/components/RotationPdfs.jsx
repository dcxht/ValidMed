const SOURCE = "https://freestuff.mehlmanmedical.com";
const ROTATIONS = [
  { name: "Family Medicine", pdf: "hy-family-medicine", title: "HY Family Medicine" },
  { name: "Psychiatry", pdf: "hy-psych", title: "HY Psych" },
  { name: "Neurology", pdf: "hy-neuro", title: "HY Neuro" },
  { name: "Pediatrics", pdf: "hy-pediatrics", title: "HY Pediatrics" },
  { name: "Medicine", pdf: "hy-internal-medicine", title: "HY Internal Medicine" },
  { name: "Surgery", pdf: "hy-surgery", title: "HY Surgery" },
  { name: "OB/GYN", pdf: "hy-obgyn-repro", title: "HY Obgyn/Repro" },
];

export default function RotationPdfs({ view }) {
  return (
    <section className="rotation-library" aria-labelledby="rotation-title">
      <div className="rotation-intro">
        <h2 id="rotation-title">{view === "step2" ? "Step 2 CK review" : "Rotation shelves"}</h2>
        <p>{view === "step2" ? "Review the clinical subjects across your rotations." : "Mehlman PDFs, in rotation order."}</p>
        <p className="rotation-status">Question banks are being rebuilt from these PDFs. No Step 1 cards are included.</p>
        <p className="rotation-note">Full PDFs may include both Step 1 and Step 2 material. This view groups them for shelf prep; it does not filter their contents.</p>
      </div>
      <div className="rotation-list">
        {ROTATIONS.map((rotation, index) => (
          <article className="rotation-resource" key={rotation.pdf}>
            <span className="rotation-number" aria-hidden="true">{index + 1}</span>
            <div className="rotation-detail">
              <h3>{rotation.name}</h3>
              <p>{rotation.title} <span className="rotation-author">by Mehlman Medical</span></p>
              <div className="rotation-links">
                <a className="rotation-open" href={`/mehlman/${rotation.pdf}.pdf`} target="_blank" rel="noreferrer">Open PDF <span aria-hidden="true">↗</span></a>
                <a className="rotation-source" href={`${SOURCE}/documents/${rotation.pdf}`} target="_blank" rel="noreferrer">Official source</a>
              </div>
              {rotation.extra && <a className="rotation-extra" href={`/mehlman/${rotation.extra.pdf}.pdf`} target="_blank" rel="noreferrer">Also: {rotation.extra.title} ↗</a>}
            </div>
          </article>
        ))}
      </div>
      <footer className="rotation-footer">
        <p>PDFs by Mehlman Medical. <a href={SOURCE} target="_blank" rel="noreferrer">Official free library ↗</a></p>
        <p>No dedicated PDF for the wellness block. Electives depend on the subject.</p>
      </footer>
    </section>
  );
}
