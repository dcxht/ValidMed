import pediatrics from "./step2/pediatrics";
import neurology from "./step2/neurology";
import psychiatry from "./step2/psychiatry";
import familyMedicine from "./step2/familyMedicine";
// Step 1 static banks archived in tag step1-archive-2026-10-14.
export const BANKS = {
  s2fm: { label: "Family Medicine", questions: familyMedicine.filter((q) => !q.duplicateOf), allQuestions: familyMedicine, coverage: "Source conversion and acceptance complete for clinical pages 4-317. Source claims and current notes are distinct; documented verification limits remain." },
  s2psy: { label: "Psychiatry", questions: psychiatry.filter((q) => !q.duplicateOf), allQuestions: psychiatry, coverage: "Source conversion and acceptance complete for clinical pages 3-53. Source claims and current notes are distinct; documented verification limits remain." },
  s2neuro: { label: "Neurology", questions: neurology.filter((q) => !q.duplicateOf), allQuestions: neurology, coverage: "Source conversion and acceptance complete for clinical pages 4-71. Source claims and current notes are distinct; documented verification limits remain." },
  s2peds: { label: "Pediatrics", questions: pediatrics.filter((q) => !q.duplicateOf), allQuestions: pediatrics, coverage: "Partial: first source conversion pp4-74; pp75-203 and full second source-detail, clinical and product acceptance remain." },
};
