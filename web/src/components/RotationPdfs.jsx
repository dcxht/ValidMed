import { BANKS } from "../data/banks";
const ROTATIONS = [
  { name: "Family Medicine", bank: "s2fm", pdf: "hy-family-medicine", title: "HY Family Medicine" },
  { name: "Psychiatry", bank: "s2psy", pdf: "hy-psych", title: "HY Psych" },
  { name: "Neurology", bank: "s2neuro", pdf: "hy-neuro", title: "HY Neuro" },
  { name: "Pediatrics", bank: "s2peds", pdf: "hy-pediatrics", title: "HY Pediatrics" },
  { name: "Medicine", pdf: "hy-internal-medicine", title: "HY Internal Medicine" },
  { name: "Surgery", pdf: "hy-surgery", title: "HY Surgery" },
  { name: "OB/GYN", pdf: "hy-obgyn-repro", title: "HY Obgyn/Repro" },
];

export default function RotationPdfs() {
  return (
    <section className="rotation-library" aria-labelledby="rotation-title">
      <div className="rotation-intro"><h2 id="rotation-title">Rotations</h2></div>
      <div className="rotation-list">
        {ROTATIONS.map((rotation, index) => (
          <article className="rotation-resource" key={rotation.pdf}>
            <span className="rotation-number" aria-hidden="true">{index + 1}</span>
            <div className="rotation-detail">
              <h3>{rotation.name}</h3>
              
              {rotation.bank && BANKS[rotation.bank] ? <a className="rotation-practice" href={`?bank=${rotation.bank}#practice`}>Review questions · {BANKS[rotation.bank].questions.length} →</a> : <p className="rotation-pending">Coming next</p>}
              <div className="rotation-links">
                <a className="rotation-pdf" href={`/mehlman/${rotation.pdf}.pdf`} target="_blank" rel="noreferrer">PDF ↗</a>
              </div>
              {rotation.extra && <a className="rotation-extra" href={`/mehlman/${rotation.extra.pdf}.pdf`} target="_blank" rel="noreferrer">Also: {rotation.extra.title} ↗</a>}
            </div>
          </article>
        ))}
      </div>
      <footer className="rotation-footer">
        <p>PDFs by Mehlman Medical.</p>
      </footer>
    </section>
  );
}
