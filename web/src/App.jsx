import { Analytics } from "@vercel/analytics/react";
import "./App.css";

const sections = [
  {
    id: "definition",
    title: "What is Cirrhosis?",
    content: (
      <div className="def-section">
        <div className="callout callout-teal">
          <p className="callout-text">
            End-stage hepatic fibrosis with architectural distortion and
            regenerative nodules — the final common pathway of chronic liver
            injury.
          </p>
        </div>
        <div className="two-col">
          <div className="card">
            <div className="card-accent purple" />
            <h3>Etiologies</h3>
            <ul>
              <li><strong>Alcohol</strong> <span className="dim">— 60-70% of cases</span></li>
              <li><strong>NAFLD / MASH</strong> <span className="dim">— rising globally</span></li>
              <li><strong>Hepatitis B & C</strong> <span className="dim">— chronic viral</span></li>
              <li><strong>Autoimmune Hepatitis</strong> <span className="dim">— immune-mediated</span></li>
              <li><strong>Wilson Disease</strong> <span className="dim">— copper accumulation</span></li>
              <li><strong>Hemochromatosis</strong> <span className="dim">— iron overload</span></li>
              <li><strong>a1-Antitrypsin Deficiency</strong> <span className="dim">— genetic</span></li>
            </ul>
          </div>
          <div className="card">
            <div className="card-accent coral" />
            <h3>Compensated vs. Decompensated</h3>
            <div className="mini-card green-bg">
              <strong className="teal">Compensated</strong>
              <p>Often asymptomatic — liver function maintained</p>
            </div>
            <div className="mini-card red-bg">
              <strong className="coral">Decompensated</strong>
              <p>Clinical complications emerge:</p>
              <ul className="bullet-coral">
                <li>Ascites</li>
                <li>Variceal hemorrhage</li>
                <li>Hepatic encephalopathy</li>
                <li>Jaundice</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    ),
  },
  {
    id: "history",
    title: "Key History to Elicit",
    subtitle: "What to ask every patient with suspected liver disease",
    content: (
      <div className="history-list">
        {[
          { num: "01", title: "Alcohol Use", detail: "Quantity, duration, pattern — screen with CAGE / AUDIT", color: "teal" },
          { num: "02", title: "Viral Hepatitis Risk", detail: "IVDU, transfusions (pre-1992), tattoos, sexual history, travel", color: "coral" },
          { num: "03", title: "Medications", detail: "Acetaminophen, herbal/OTC supplements, methotrexate, amiodarone", color: "purple" },
          { num: "04", title: "Family History", detail: "Liver disease, Wilson's, hemochromatosis, a1-AT deficiency", color: "amber" },
          { num: "05", title: "Metabolic Syndrome", detail: "Obesity, T2DM, dyslipidemia — screen for MASH", color: "teal" },
          { num: "06", title: "Symptom Timeline", detail: "Fatigue, weight changes, abdominal swelling, GI bleed, confusion", color: "coral" },
        ].map((item) => (
          <div className="history-row" key={item.num}>
            <div className={`history-badge ${item.color}`}>{item.num}</div>
            <div>
              <strong>{item.title}</strong>
              <p className="dim">{item.detail}</p>
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: "symptoms",
    title: "Symptoms by System",
    content: (
      <div className="symptom-grid">
        {[
          { system: "Constitutional", items: ["Fatigue, anorexia", "Weight loss, muscle wasting"], color: "teal" },
          { system: "Gastrointestinal", items: ["Nausea, early satiety", "RUQ pain, abdominal distension"], color: "coral" },
          { system: "Hematologic", items: ["Easy bruising / bleeding", "Hematemesis, melena"], color: "purple" },
          { system: "Neurologic", items: ["Sleep-wake reversal, confusion", "Asterixis (encephalopathy)"], color: "blue" },
          { system: "Dermatologic", items: ["Pruritus (cholestatic)", "Dark urine, jaundice"], color: "amber" },
          { system: "Reproductive", items: ["Gynecomastia, decreased libido", "Amenorrhea, erectile dysfunction"], color: "coral" },
        ].map((s) => (
          <div className="symptom-card" key={s.system}>
            <div className={`card-accent ${s.color}`} />
            <span className={`system-label ${s.color}`}>{s.system.toUpperCase()}</span>
            <ul>
              {s.items.map((item, i) => (
                <li key={i}><span className={`bullet ${s.color}`}>&#9656;</span> {item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: "exam",
    title: "Physical Exam Findings",
    content: (
      <div className="exam-layout">
        <div className="exam-grid">
          {[
            { region: "Hands & Arms", items: ["Palmar erythema", "Dupuytren contracture", "Terry nails (white proximal, pink distal)", "Asterixis (liver flap)", "Clubbing"], color: "teal" },
            { region: "Head & Chest", items: ["Scleral icterus / jaundice", "Fetor hepaticus (musty breath)", "Spider angiomata (SVC distribution)", "Gynecomastia", "Parotid enlargement (alcoholic)"], color: "coral" },
            { region: "Abdomen", items: ["Hepatomegaly (early) then shrunken (late)", "Splenomegaly (portal HTN)", "Ascites — shifting dullness, fluid wave", "Caput medusae"], color: "purple" },
            { region: "Lower Ext & Other", items: ["Bilateral pitting edema", "Muscle wasting / sarcopenia", "Testicular atrophy", "Decreased body hair", "Petechiae / ecchymoses"], color: "amber" },
          ].map((r) => (
            <div className="exam-card" key={r.region}>
              <div className={`card-left-accent ${r.color}`} />
              <span className={`system-label ${r.color}`}>{r.region.toUpperCase()}</span>
              <ul>
                {r.items.map((item, i) => (
                  <li key={i}><span className={`bullet ${r.color}`}>&#9657;</span> {item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="high-yield">
          <div className="hy-header">HIGH YIELD</div>
          {[
            { t: "Spider Angiomata", d: "SVC distribution — face, chest, upper arms. Arterial, blanch from center." },
            { t: "Caput Medusae", d: "Periumbilical venous distension from portal hypertension." },
            { t: "Asterixis", d: '"Liver flap" — negative myoclonus in hepatic encephalopathy.' },
            { t: "Palmar Erythema", d: "Hyperdynamic circulation + elevated estrogen." },
          ].map((h) => (
            <div className="hy-item" key={h.t}>
              <strong>{h.t}</strong>
              <p>{h.d}</p>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  {
    id: "complications",
    title: "Complications, Labs & Prognosis",
    content: (
      <div className="comp-section">
        <div className="two-col">
          <div className="card">
            <div className="card-accent coral" />
            <h3 className="coral">Decompensation — "HAVE"</h3>
            <div className="have-list">
              {[
                { letter: "H", rest: "epatic Encephalopathy", note: "Confusion, asterixis, sleep-wake reversal" },
                { letter: "A", rest: "scites (+ SBP)", note: "Most common decompensation event" },
                { letter: "V", rest: "ariceal Hemorrhage", note: "Life-threatening" },
                { letter: "E", rest: "levated Bilirubin / Jaundice", note: "Conjugation failure" },
              ].map((h) => (
                <div className="have-item" key={h.letter}>
                  <span className="have-letter">{h.letter}</span>
                  <div>
                    <span className="have-rest">{h.rest}</span>
                    <p className="dim small">{h.note}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="card">
            <div className="card-accent teal" />
            <h3 className="teal">Key Laboratory Findings</h3>
            <ul className="lab-list">
              {[
                { lab: "Decreased Albumin", reason: "synthetic dysfunction" },
                { lab: "Elevated INR / PT", reason: "coagulopathy" },
                { lab: "Elevated Bilirubin", reason: "conjugation failure" },
                { lab: "Thrombocytopenia", reason: "splenic sequestration" },
                { lab: "AST:ALT > 2:1", reason: "alcoholic etiology" },
                { lab: "Elevated Ammonia", reason: "encephalopathy" },
              ].map((l) => (
                <li key={l.lab}><strong>{l.lab}</strong> <span className="dim">— {l.reason}</span></li>
              ))}
            </ul>
          </div>
        </div>
        <div className="scoring-row">
          <div className="score-card purple-bg">
            <strong className="purple">CHILD-PUGH SCORE</strong>
            <p>A/B/C classification using albumin, bilirubin, INR, ascites, encephalopathy</p>
          </div>
          <div className="score-card amber-bg">
            <strong className="amber">MELD SCORE</strong>
            <p>Bilirubin + INR + creatinine — determines transplant listing priority</p>
          </div>
        </div>
      </div>
    ),
  },
  {
    id: "takeaway",
    title: "Take-Home Points",
    content: (
      <div className="takeaway-grid">
        {[
          { num: "1", title: "Silent Until It's Not", desc: "Cirrhosis is often asymptomatic until decompensation — high index of suspicion is key.", color: "teal" },
          { num: "2", title: "History is Everything", desc: "Alcohol, viral risk factors, and metabolic syndrome cover the vast majority of cases.", color: "coral" },
          { num: "3", title: "Exam Tells the Story", desc: "Spider angiomata, ascites, asterixis, and palmar erythema are classic findings.", color: "purple" },
        ].map((t) => (
          <div className="takeaway-card" key={t.num}>
            <div className={`card-accent ${t.color}`} />
            <div className={`takeaway-num ${t.color}`}>{t.num}</div>
            <strong>{t.title}</strong>
            <p>{t.desc}</p>
          </div>
        ))}
      </div>
    ),
  },
];

export default function App() {
  return (
    <div className="app">
      <header className="hero">
        <div className="hero-deco-1" />
        <div className="hero-deco-2" />
        <div className="hero-bars">
          <div className="bar bar-teal" />
          <div className="bar bar-purple" />
        </div>
        <h1>CIRRHOSIS</h1>
        <p className="hero-sub">
          Patient Presentation &middot; Key History &middot; Symptoms &middot;
          Exam Findings
        </p>
        <div className="hero-pill">5-MINUTE CLINICAL REVIEW</div>
      </header>

      <main>
        {sections.map((section) => (
          <section key={section.id} id={section.id}>
            <div className="section-header">
              <h2>{section.title}</h2>
              {section.subtitle && <p className="subtitle">{section.subtitle}</p>}
            </div>
            {section.content}
          </section>
        ))}
      </main>

      <footer>
        <p>Clinical Review &middot; For educational purposes</p>
      </footer>
      <Analytics />
    </div>
  );
}
