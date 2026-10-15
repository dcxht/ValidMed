import familyMedicine from "./step2/familyMedicine";
// Step 1 static banks archived in tag step1-archive-2026-10-14.
export const BANKS = {
  s2fm: { label: "Family Medicine", questions: familyMedicine.filter((q) => !q.duplicateOf), allQuestions: familyMedicine, coverage: "Clinical pages 4-317 reviewed. Final source mapping and clinical QA still in progress." },
};
