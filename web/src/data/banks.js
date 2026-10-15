import psychiatry from "./step2/psychiatry";
import familyMedicine from "./step2/familyMedicine";
// Step 1 static banks archived in tag step1-archive-2026-10-14.
export const BANKS = {
  s2fm: { label: "Family Medicine", questions: familyMedicine.filter((q) => !q.duplicateOf), allQuestions: familyMedicine, coverage: "Source conversion and acceptance complete for clinical pages 4-317. Source claims and current notes are distinct; documented verification limits remain." },
  s2psy: { label: "Psychiatry", questions: psychiatry.filter((q) => !q.duplicateOf), allQuestions: psychiatry, coverage: "Partial: source pages 3-11 converted; remaining clinical pages 12-53 and final QA still in progress." },
};
