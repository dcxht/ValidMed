import neuroQuestions from "./neuroQuestions";
import endoPathQuestions from "./endoPathQuestions";
import renalPulmQuestions from "./renalPulmQuestions";
import biochemQuestions from "./biochemQuestions";
import arrowsQuestions from "./arrowsQuestions";
import neuroAnatomyQuestions from "./neuroAnatomyQuestions";
import immunoQuestions from "./immunoQuestions";
import reproQuestions from "./reproQuestions";
import anatomyQuestions from "./anatomyQuestions";
import imageQuestions from "./nbmeImageQuestions";
import microQuestions from "./microQuestions";

export const BANKS = {
  neuro: { label: "Neuro", questions: neuroQuestions },
  endopath: { label: "Endo + Path", questions: endoPathQuestions },
  renalpulm: { label: "Renal + Pulm", questions: renalPulmQuestions },
  biochem: { label: "Biochem", questions: biochemQuestions },
  arrows: { label: "Arrows", questions: arrowsQuestions },
  neuroanatomy: { label: "Neuroanatomy", questions: neuroAnatomyQuestions },
  immuno: { label: "Immunology", questions: immunoQuestions },
  repro: { label: "Repro + OB", questions: reproQuestions },
  anatomy: { label: "Anatomy", questions: anatomyQuestions },
  nbmeimages: { label: "NBME Images", questions: imageQuestions },
  micro: { label: "Micro", questions: microQuestions },
};
