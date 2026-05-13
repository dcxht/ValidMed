const neuroQuestions = [
  // BRAINSTEM LESIONS
  { id: 1, category: "Brainstem", q: "65-year-old woman presents with apathy, disinhibition, and personality changes. Where is the lesion?", a: "Frontal lobe. Diagnosis is frontotemporal dementia." },
  { id: 2, category: "Brainstem", q: "69F with Hx of HTN presents after a stroke with tongue deviated to the left side. Where is the stroke lesion on a medulla cross-section?", a: "Medial medulla on the left side (medial medullary syndrome). Ipsilateral tongue deviation = medial medullary syndrome. Supplied by the paramedian branch of the anterior spinal artery (ASA)." },
  { id: 3, category: "Brainstem", q: "70M with Hx of HTN presents with left-sided Bell's palsy, left-sided hearing loss, and loss of temperature/pain to the left side of face and right side of body. Where is the stroke lesion?", a: "Lateral pons on the left side (lateral pontine syndrome). Bell's palsy is the key detail. Caused by lesion of anterior inferior cerebellar artery (AICA). Mnemonic: FACIAL contains AICA backwards." },
  { id: 4, category: "Brainstem", q: "CT of the pons shows a central lesion — what is the diagnosis and most likely cause?", a: "Central pontine myelinolysis secondary to correction of hyponatremia too rapidly with hypertonic saline. Patient presents with locked-in syndrome (quadriplegia + aphonia + impaired horizontal eye movements)." },
  { id: 5, category: "Brainstem", q: "78M with Hx of HTN; left eye is directed laterally and inferiorly + weakness of right side of body. Dx?", a: "Weber syndrome — midbrain lesion resulting in ipsilateral CN III palsy + contralateral hemiparesis (loss of crus cerebri). Lesion in paramedian branch of posterior cerebral artery (PCA)." },
  { id: 6, category: "Brainstem", q: "75F had a cerebral infarction many years ago. Brain on autopsy shows infarction of right crus cerebri. What would her main deficit have been?", a: "Spastic paralysis on the left side of the body (contralateral to the lesion)." },

  // MLF / INO
  { id: 7, category: "Multiple Sclerosis", q: "32F with one-week Hx of urge to run to the bathroom at inopportune moments + inability to adduct left eye when gazing to the right + convergence not affected. Where is the lesion?", a: "Left medial longitudinal fasciculus (MLF). Dx is MLF syndrome (internuclear ophthalmoplegia/INO) in a patient with multiple sclerosis. The side that cannot adduct is the side of the pathology. MLF syndrome is pathognomonic for MS." },
  { id: 8, category: "Multiple Sclerosis", q: "42F + diplopia + can read books normally + decreased adduction in left eye when gazing to the right. Location of demyelinating plaque?", a: "Left MLF (internuclear ophthalmoplegia). Can converge normally, which distinguishes from CN III lesion." },
  { id: 9, category: "Multiple Sclerosis", q: "27F + intermittent headaches + blurry vision. Dx?", a: "Optic neuritis (multiple sclerosis). Presents as blurry vision, change in color vision, or Marcus Gunn pupil (relative afferent pupillary defect)." },
  { id: 10, category: "Multiple Sclerosis", q: "34F + left eye pain + blurry vision + progressive weakness of right arm and both legs + fundoscopy shows optic disc swelling + MRI shows multiple T2-weighted bright signal abnormalities in white matter. What cell is attacked?", a: "Oligodendrocytes. Dx is multiple sclerosis — T cell-mediated destruction of oligodendrocytes in CNS." },
  { id: 11, category: "Multiple Sclerosis", q: "28F + urinary incontinence + blurry vision + diminished vibration in toes + unable to maintain balance with eyes closed. Damage to which spinal tract?", a: "Fasciculus gracilis of the dorsal columns. Dx is MS presenting with classic urge incontinence, optic neuritis, and (+) Romberg sign." },
  { id: 12, category: "Multiple Sclerosis", q: "34F + Hx of MS + two-week Hx of severe shooting pain in left cheek brought on by brushing teeth. Most likely location of demyelination?", a: "Pons (giving rise to trigeminal nerve; MS patient with trigeminal neuralgia-like presentation from central lesion)." },

  // PARKINSON / BASAL GANGLIA
  { id: 13, category: "Basal Ganglia", q: "74M with unilateral resting tremor + shuffling gait. Where on MRI is the location of his pathology?", a: "Midbrain (substantia nigra pars compacta). Diagnosis is Parkinson disease." },
  { id: 14, category: "Basal Ganglia", q: "23F + unilateral resting tremor + increased hepatic ALT and AST + low hematocrit. Which letter correctly labels the putamen on MRI?", a: "B = putamen. Parkinsonism in a young patient is Wilson disease until proven otherwise; copper deposition occurs in basal ganglia, classically the putamen." },
  { id: 15, category: "Basal Ganglia", q: "41M + one-year Hx of jerking movements of extremities + 6-month Hx of worsening dementia + father had similar presentation and died at age 56. Where on MRI is the pathology?", a: "Caudate nucleus. Dx is Huntington disease (autosomal dominant CAG trinucleotide repeat on chromosome 4)." },
  { id: 16, category: "Basal Ganglia", q: "63M + longstanding Hx of HTN + acute-onset flailing movements of left arm. Where is the pathology?", a: "Right subthalamic nucleus. Dx is hemiballismus — lesion of contralateral subthalamic nucleus." },
  { id: 17, category: "Basal Ganglia", q: "51F + irregular flailing movements of right side of body. Dx and site of lesion?", a: "Hemiballismus; lesion of contralateral (left) subthalamic nucleus." },
  { id: 18, category: "Basal Ganglia", q: "18M + used 'synthetic heroine' at party + tight muscles + shuffling gait + bradykinesia + afebrile and pupils normal. Location of brain affected?", a: "Substantia nigra. MPTP-induced Parkinsonism. MPTP is sold as 'synthetic heroine' and can cause Parkinsonism." },
  { id: 19, category: "Basal Ganglia", q: "59M + Parkinson disease. Loss of patient's substantia nigra is most likely to result in disinhibition in which brain area?", a: "Striatum." },

  // INTERNAL CAPSULE
  { id: 20, category: "Strokes", q: "78M + long Hx of HTN + sudden paresis of left side of body. Where is the most likely location of his stroke?", a: "Posterior limb of internal capsule. Lenticulostriate vessels supply the internal capsule. Posterior limb infarcts cause 'pure motor' dysfunction." },

  // CRANIAL NERVES
  { id: 21, category: "Cranial Nerves", q: "32F hiking in Connecticut + circular rash on forearm + Bell's palsy. Which nerve explains her findings?", a: "Facial nerve (CN VII). Bell's palsy secondary to Lyme disease." },
  { id: 22, category: "Cranial Nerves", q: "76M + stroke + uvula deviates to the left when he says 'Ahh.' Which nerve is affected?", a: "Right vagus nerve (CN X). Vagus nerve lesion causes contralateral uvula deviation." },
  { id: 23, category: "Cranial Nerves", q: "35F + complete loss of hearing in left ear. Which CN is damaged?", a: "Left vestibulocochlear nerve (CN VIII)." },
  { id: 24, category: "Cranial Nerves", q: "47M + touching the face just lateral to the nose produces pain. The nerve supplying this area exits the skull through where?", a: "Foramen rotundum (maxillary branch/V2 of trigeminal nerve)." },
  { id: 25, category: "Cranial Nerves", q: "19M + viral infection + Bell palsy. What other finding might be seen as a result of the nerve lesion?", a: "Ipsilateral hyperacusis (loud sounds). CN VII (facial) innervates the stapedius muscle, which dampens sounds." },
  { id: 26, category: "Cranial Nerves", q: "54F + 4-day Hx of hoarseness and difficulty swallowing + unable to elevate left side of palate. Which CN is damaged?", a: "Left vagus nerve. Failure of elevation of ipsilateral palate causes contralateral uvula deviation." },
  { id: 27, category: "Cranial Nerves", q: "24M + decreased taste to anterior 2/3 of left side of tongue. Which nerve is likely damaged?", a: "Left facial nerve (CN VII)." },
  { id: 28, category: "Cranial Nerves", q: "45M + uvula deviation to the right + dysphagia. Which tongue muscle might be affected?", a: "Palatoglossus (innervated by CN X). Other tongue muscles innervated by CN XII." },
  { id: 29, category: "Cranial Nerves", q: "The thalamus notably does not receive sensory input from which nerve?", a: "Olfactory nerve (CN I) — the only CN that doesn't relay through thalamus." },
  { id: 30, category: "Cranial Nerves", q: "59F + metastatic breast cancer + absent corneal reflex on right. Metastases to which cranial nerve exit point?", a: "Superior orbital fissure — exit point for ophthalmic branch of trigeminal nerve (V1). Mnemonic: Standing Room Only = Superior orbital fissure, foramen Rotundum, foramen Ovale for V1, V2, V3." },

  // VASCULATURE
  { id: 31, category: "Vasculature", q: "48F with Hx of cystic kidneys + right pupil enlarged. An aneurysm of which vessel explains this?", a: "Posterior communicating artery (PCoM). PCoM aneurysms cause ipsilateral mydriasis (blown pupil). Increased risk of ACoM and PCoM aneurysms in ADPKD." },
  { id: 32, category: "Vasculature", q: "82F with Hx of atrial fibrillation + inability to move all muscles of body except for eyes. Where is the stroke?", a: "Basilar artery — resulting in locked-in syndrome." },
  { id: 33, category: "Vasculature", q: "68M with Hx of HTN + acute-onset painless loss of vision in the right eye. Which vessel on the circle of Willis reflects the path of the embolus?", a: "Ophthalmic artery (branch of internal carotid). Dx is central retinal artery occlusion from carotid plaque." },
  { id: 34, category: "Vasculature", q: "32M with Hx of fainting episodes + blood pressure lower in right arm than left arm; retrograde flow through which vessel?", a: "Right vertebral artery. Dx is subclavian steal syndrome." },

  // CEREBELLUM
  { id: 35, category: "Cerebellum", q: "34F + boating accident + dysmetria of right side of body + normal strength. Where is the injury?", a: "Right cerebellar hemisphere. Cerebellar injuries cause ipsilateral dysmetria. Vermis lesion would cause truncal ataxia instead." },
  { id: 36, category: "Cerebellum", q: "44M + long Hx of alcoholism + stumbles to the right when ambulating + Romberg sign intact. Where is the pathology?", a: "Right side of cerebellum. Cerebellar lesions are always ipsilateral. Romberg (-) = cerebellar etiology on USMLE." },
  { id: 37, category: "Cerebellum", q: "44M + progressive ataxia with unsteady gait + left-sided intention tremors. Cause is damage to which brain area?", a: "Left cerebellar hemisphere (cerebellar lesions lead to ipsilateral neurologic signs)." },

  // BRACHIAL PLEXUS / PERIPHERAL NERVES
  { id: 38, category: "Peripheral Nerves", q: "26M + arm slashed in bar fight + arm pronated and unable to extend wrist. Which nerve is affected?", a: "Radial nerve (posterior cord of brachial plexus)." },
  { id: 39, category: "Peripheral Nerves", q: "Midshaft fracture of humerus — which nerve is injured?", a: "Radial nerve — wrist-drop + pronated forearm." },
  { id: 40, category: "Peripheral Nerves", q: "Supracondylar fracture of humerus — which nerve is injured?", a: "Median nerve." },
  { id: 41, category: "Peripheral Nerves", q: "Medial epicondylar fracture — nerve injury?", a: "Ulnar nerve." },
  { id: 42, category: "Peripheral Nerves", q: "Surgical neck of humerus fracture — nerve injury?", a: "Axillary nerve." },
  { id: 43, category: "Peripheral Nerves", q: "Mastectomy + post-operative winged scapula — nerve injury?", a: "Long thoracic nerve (innervates serratus anterior)." },
  { id: 44, category: "Peripheral Nerves", q: "25M + impaired plantar flexion + inversion. Dx?", a: "Tibial nerve injury." },
  { id: 45, category: "Peripheral Nerves", q: "25M + impaired dorsiflexion + eversion. Dx?", a: "Common peroneal nerve injury." },
  { id: 46, category: "Peripheral Nerves", q: "15M + pain and tingling in right hand when backpacking + symptoms resolve five minutes after removing backpack. Dx?", a: "Thoracic outlet syndrome due to first cervical rib." },
  { id: 47, category: "Peripheral Nerves", q: "32F + paresthesias in thenar region of hand +/- hand weakness + sensation intact over dorsum of hand. Next best step in Dx?", a: "Electrophysiological testing (for carpal tunnel syndrome). Tinel sign and Phalen maneuver alone are insufficient." },

  // SPINAL CORD
  { id: 48, category: "Spinal Cord", q: "45M + boating accident years prior to death + autopsy with myelin stain shows bilateral lesions of the fasciculus gracilis. What was his most likely deficit?", a: "Loss of vibration/proprioception of the lower limbs." },
  { id: 49, category: "Spinal Cord", q: "43F + inability to sense pain/temperature over right lower extremity. Where on a spinal cord cross-section is the lesion?", a: "Left spinothalamic tract (spinothalamic tract lesions are contralateral)." },
  { id: 50, category: "Spinal Cord", q: "24M + viral infection + loss of left leg motor function + loss of left leg vibration/proprioception + loss of right leg pain/temperature sensation. Dx?", a: "Brown-Sequard syndrome — hemisection of the spinal cord." },
  { id: 51, category: "Spinal Cord", q: "33F + 1-wk Hx of R-sided weakness + L-sided inability to feel temperature/pain + diminished vibratory sensation over R foot + brisk R-sided reflexes + R-sided Babinski sign. Dx?", a: "Brown-Sequard syndrome secondary to viral infection." },
  { id: 52, category: "Spinal Cord", q: "67M + long history of cervical spondylosis + whiplash injury after rear-end MVA + weakness in upper limbs > weakness in lower limbs. Dx?", a: "Central cord syndrome. Typically follows hyperextension injury of the neck." },
  { id: 53, category: "Spinal Cord", q: "69M + long Hx of T2DM + bilateral loss of motor function and pain/temperature below level of nipples + intact vibration/proprioception. Dx?", a: "Anterior cord syndrome (dorsal columns spared). Often due to atherosclerosis + infarction of anterior spinal artery." },
  { id: 54, category: "Spinal Cord", q: "23M + neurologic dysfunction + spinal cord cross-section with myelin stain shows only dorsal columns demyelinated. Most likely diagnosis?", a: "Tabes dorsalis (neurosyphilis) — isolated loss of vibration/proprioception." },
  { id: 55, category: "Spinal Cord", q: "31M + motorcycle accident + spinal lesion affecting the anterior white commissure. What type of neurologic dysfunction?", a: "Bilateral loss of pain and temperature. Dx is syringomyelia. Can be due to trauma, infections, and classically Chiari I." },
  { id: 56, category: "Spinal Cord", q: "54M + clonus and Babinski reflex in left foot + fasciculations in right hand + brisk reflexes + elevated serum CK. Dx?", a: "Amyotrophic lateral sclerosis (ALS). Combination of UMN and LMN findings with NO sensory abnormalities." },
  { id: 57, category: "Spinal Cord", q: "55M + immigrant from Albania + left leg with remarkably decreased muscle bulk and diminished motor function. Dx?", a: "Polio — loss of anterior horns of spinal cord." },
  { id: 58, category: "Spinal Cord", q: "40M + combination of LMN and UMN findings + no sensory abnormalities. Dx?", a: "Amyotrophic lateral sclerosis (ALS). No sensory findings is the key detail." },

  // SPINE & VERTEBRAE
  { id: 59, category: "Spine", q: "22M + needs laminectomy. Where on a vertebra is the most appropriate location for surgical entrance to the neural canal?", a: "Lamina." },
  { id: 60, category: "Spine", q: "17M + undergoing spinal surgery + needle inserted posteriorly between L3 and L4. What ligament must be traversed?", a: "Ligamentum flavum." },
  { id: 61, category: "Spine", q: "24M + lumbar disc herniation. Which spinal ligament is pushed into the spinal root nerves?", a: "Posterior longitudinal ligament." },
  { id: 62, category: "Spine", q: "63M + pain radiating down distal anterior thigh, knee, medial leg, and medial foot. Compression of nerve root in which intervertebral foramina?", a: "L3-L4." },
  { id: 63, category: "Spine", q: "32F + gestational pemphigoid with itchy vesicles around the umbilicus. Dermatome?", a: "T10." },
  { id: 64, category: "Spine", q: "48M + burns his thumb. Pain sensed via which dermatome?", a: "C6. Lateral digits = C6; middle finger = C7; medial digits = C8." },
  { id: 65, category: "Spine", q: "81F + difficulty fastening buttons + weakness of intrinsic muscles of hands + loss of sensation in 5th fingers. Dx at level of spine?", a: "C7-T1 foraminal stenosis." },
  { id: 66, category: "Spine", q: "44M + saddle anesthesia + late urinary incontinence. Dx?", a: "Cauda equina syndrome — bundle of spinal nerves and rootlets arising from the conus medullaris." },
  { id: 67, category: "Spine", q: "44M + perianal anesthesia + early urinary + fecal incontinence. Dx?", a: "Conus medullaris syndrome — bulbous end of the spinal cord." },

  // STROKES
  { id: 68, category: "Strokes", q: "77M + sudden-onset miosis of left eye + ptosis of left eyelid + dysphagia + difficulty speaking + pain and temperature decreased on left side of face and right side of body. Which artery occluded?", a: "Left posterior inferior cerebellar artery (PICA). Horner syndrome + PICA infarct = lateral medullary syndrome (Wallenberg)." },
  { id: 69, category: "Strokes", q: "69M + stroke + hoarse voice + can't detect pinprick or cold on right side of face or left side of body. Location?", a: "Lateral medulla (right PICA). Lateral medullary syndrome = PICAchew (Pikachu) = dysphagia/hoarseness +/- Horner syndrome." },
  { id: 70, category: "Strokes", q: "54F + decreased fluency of spontaneous speech after cerebral infarction + comprehension is normal + weakness of lower 2/3 of right side of face. Dx and which vessel?", a: "Broca aphasia; left middle cerebral artery." },
  { id: 71, category: "Strokes", q: "65M + BP 140/100 + 2/5 muscle strength in left leg + brisk reflexes in left leg. Which vessel?", a: "Right anterior cerebral artery." },
  { id: 72, category: "Strokes", q: "65M + Hx of T2DM, HTN, and hyperlipidemia + new-onset quadriplegia + impaired horizontal eye movements but vertical intact + speech is dysarthric. Part of brain affected?", a: "Pons. Locked-in syndrome caused by basilar artery stroke." },
  { id: 73, category: "Strokes", q: "55M + two-week Hx of constant and intense pain of left arm + Hx of stroke 5 months ago + loss of sensation to left side of body. Cause of pain?", a: "Right thalamus. Thalamic pain syndrome is a HY post-stroke cause of pain." },
  { id: 74, category: "Strokes", q: "54M + Hx of HTN + unable to recognize people's face + unable to recognize objects unless he touches them. Damaged area supplied by what artery?", a: "Posterior cerebral artery. Prosopagnosia and visual agnosia = occipital lobe lesions (PCA infarct)." },
  { id: 75, category: "Strokes", q: "71F + stroke + agraphia, acalculia, finger agnosia, and left-right agnosia. What part of the brain?", a: "Angular gyrus (parietal lobe). Dx = Gerstmann syndrome." },
  { id: 76, category: "Strokes", q: "81M + stroke + which type of cell of CNS is likely to clear necrotic tissue?", a: "Microglial cells (macrophages of the CNS)." },
  { id: 77, category: "Strokes", q: "Stroke causing Horner syndrome + dysphagia + loss of pain/temp from contralateral body and ipsilateral face. Dx?", a: "Lateral medullary syndrome (PICA infarct). 'Pikachu' = PICA-chew = dysphagia." },
  { id: 78, category: "Strokes", q: "Stroke causing ipsilateral Bell palsy. Dx?", a: "Lateral pontine syndrome (AICA infarct). FACIAL spelled backwards has AICA in it." },
  { id: 79, category: "Strokes", q: "Stroke causing ipsilateral tongue deviation + contralateral paralysis and loss of proprioception. Dx?", a: "Medial medullary syndrome (paramedian branch of anterior spinal artery)." },
  { id: 80, category: "Strokes", q: "Stroke causing locked-in syndrome. Dx?", a: "Basilar artery stroke." },
  { id: 81, category: "Strokes", q: "Lacunar infarct affecting posterior limb of internal capsule — what deficits?", a: "Pure motor (contralateral). Caused by HTN leading to lipohyalinosis of lenticulostriate vessels." },
  { id: 82, category: "Strokes", q: "Lacunar infarct affecting thalamus — what deficits?", a: "Pure sensory (contralateral). VPL senses from body; VPM from face." },
  { id: 83, category: "Strokes", q: "Pain in contralateral limb months after stroke resolves. Dx?", a: "Thalamic pain syndrome." },
  { id: 84, category: "Strokes", q: "Coma or persistent vegetative state following deceleration injury (MVA or fall). Dx?", a: "Diffuse axonal injury." },
  { id: 85, category: "Strokes", q: "MCA stroke on dominant hemisphere; HY findings?", a: "Contralateral limb + face sensory and/or motor deficits; also Broca and Wernicke aphasias." },
  { id: 86, category: "Strokes", q: "ACA stroke; HY findings?", a: "Contralateral lower leg sensory and/or motor dysfunction." },
  { id: 87, category: "Strokes", q: "PCA stroke; HY findings?", a: "Contralateral hemianopsia with macular sparing." },

  // APHASIA
  { id: 88, category: "Strokes", q: "Broca aphasia; HY findings and location?", a: "Non-fluent aphasia; telegraphic speech; comprehends normally but can't communicate; repetition impaired. Location: posterior, lateral, inferior frontal lobe." },
  { id: 89, category: "Strokes", q: "Wernicke aphasia; HY findings and location?", a: "Fluent aphasia; word salad; non-sensical speech; does not comprehend; repetition impaired. Location: superior temporal gyrus." },
  { id: 90, category: "Strokes", q: "What is conduction aphasia?", a: "Patient has only impaired repetition (arcuate fasciculus connecting Broca and Wernicke areas)." },
  { id: 91, category: "Strokes", q: "What is transcortical motor aphasia?", a: "Sounds like Broca aphasia but repetition is intact." },
  { id: 92, category: "Strokes", q: "What is transcortical sensory aphasia?", a: "Sounds like Wernicke aphasia but repetition is intact." },

  // BRAIN BLEEDS
  { id: 93, category: "Brain Bleeds", q: "84M + one-year Hx of progressive cognitive decline + no Hx of HTN/CVD/AF + experiences a stroke and dies. CT finding?", a: "Intracerebral (intraparenchymal) hemorrhage. Dx is amyloid angiopathy in Alzheimer disease." },
  { id: 94, category: "Brain Bleeds", q: "17M + motorcycle accident + severe cognitive impairment two years later. Based on MRI, diagnosis?", a: "Diffuse axonal injury — caused by shearing forces from rapid-deceleration injury." },
  { id: 95, category: "Brain Bleeds", q: "Epidural hematoma; next best step after CT confirms?", a: "Intubation and hyperventilation on Neuro NBME. After this, craniotomy." },
  { id: 96, category: "Brain Bleeds", q: "Subdural hematoma; next best step after CT?", a: "Craniotomy on NBME (not observation)." },
  { id: 97, category: "Brain Bleeds", q: "What do you see on non-contrast CT with epidural vs subdural?", a: "Epidural = lens (biconvex) shape; subdural = crescent-shaped." },
  { id: 98, category: "Brain Bleeds", q: "Blood pressure of 220/120 + confusion. Dx + Tx?", a: "Hypertensive encephalopathy. Give IV sodium nitroprusside." },
  { id: 99, category: "Brain Bleeds", q: "BP of 220/120 + sodium nitroprusside administered + now patient has confusion. Dx?", a: "Cyanide toxicity caused by nitroprusside." },
  { id: 100, category: "Brain Bleeds", q: "Severe headache + stiff neck. Dx?", a: "Subarachnoid hemorrhage (can cause meningism similar to meningitis)." },
  { id: 101, category: "Brain Bleeds", q: "Brain bleed in patient with Alzheimer. Dx?", a: "Amyloid angiopathy (intracerebral hemorrhage)." },
  { id: 102, category: "Brain Bleeds", q: "31F + MVA + GCS of 6 + BP 165/90 + RR 10 + HR 55. Mechanism for hypertension?", a: "Increased intracranial pressure (Cushing triad: HTN, bradycardia, bradypnea)." },
  { id: 103, category: "Brain Bleeds", q: "29M + MVA + hematoma over mastoid processes bilaterally + rhinorrhea + otorrhea + raccoon eyes. Dx?", a: "Base of skull fracture (classic tetrad)." },
  { id: 104, category: "Brain Bleeds", q: "Drug that can be given to prevent vasospasm after SAH?", a: "Nimodipine (dihydropyridine CCB)." },
  { id: 105, category: "Brain Bleeds", q: "Correct hyponatremia too quickly?", a: "Locked-in syndrome due to central pontine myelinolysis (osmotic demyelination)." },
  { id: 106, category: "Brain Bleeds", q: "Correct hypernatremia too quickly?", a: "Cerebral edema." },
  { id: 107, category: "Brain Bleeds", q: "How to Dx brain cancer?", a: "Contrast head CT." },
  { id: 108, category: "Brain Bleeds", q: "How to Dx brain bleed?", a: "Non-contrast CT." },

  // CNS TUMORS
  { id: 109, category: "CNS Tumors", q: "44F + SLE + ring-enhancing lesion on head CT. Diagnosis?", a: "Primary CNS lymphoma (NOT Toxoplasmosis). Autoimmune diseases carry increased risk of primary CNS lymphoma." },
  { id: 110, category: "CNS Tumors", q: "3M + failure to thrive + seizure + large solid and cystic lesion on MRI. Diagnosis?", a: "Pilocytic astrocytoma. Most common brain tumor in kids. Has solid (white) and cystic (black) components." },
  { id: 111, category: "CNS Tumors", q: "54M + 3-month Hx of cognitive disturbance + seizure + heterogeneous mass on CT crossing midline. Diagnosis?", a: "Glioblastoma multiforme (butterfly glioma). Most common primary brain cancer in adults." },
  { id: 112, category: "CNS Tumors", q: "16M + developed cataracts at young age + six-month history of left-sided tinnitus and hearing loss. Most likely underlying genetic condition?", a: "Neurofibromatosis type II (NF2). Dx is acoustic schwannoma at cerebellopontine junction." },
  { id: 113, category: "CNS Tumors", q: "56M + nine-year Hx of progressive right-sided hearing loss; MRI shows large mass at cerebellopontine junction. Arises from which nerve and cell type?", a: "Vestibulocochlear nerve and neural crest cells (Schwann cells)." },
  { id: 114, category: "CNS Tumors", q: "47M + bitemporal hemianopsia. Most likely tumor?", a: "Prolactinoma (most common pituitary tumor in adults)." },
  { id: 115, category: "CNS Tumors", q: "8M + bitemporal hemianopsia. Most likely tumor?", a: "Craniopharyngioma (most common pituitary tumor in children; derived from Rathke pouch)." },
  { id: 116, category: "CNS Tumors", q: "3F + morning vomiting + truncal ataxia. Dx?", a: "Medulloblastoma of cerebellar vermis." },
  { id: 117, category: "CNS Tumors", q: "Most common primary brain cancer in children?", a: "Pilocytic astrocytoma — solid + cystic on MRI; has Rosenthal fibers; not aggressive." },
  { id: 118, category: "CNS Tumors", q: "Most common primary brain cancer in adults?", a: "Glioblastoma multiforme (butterfly glioma) — areas of necrosis + hemorrhage; grade IV fibrillary astrocytoma." },
  { id: 119, category: "CNS Tumors", q: "5F + vomiting recently + bilateral papilledema + impaired upward gaze + shuffling gait + CT shows enlarged ventricles with 2 cm mass. Most likely location?", a: "Pineal gland. Dx = Parinaud syndrome (upward gaze palsy secondary to pinealoma)." },
  { id: 120, category: "CNS Tumors", q: "6M + dancing eyes + HTN + lesion in posterior mediastinum on CXR. Dx?", a: "Neuroblastoma. Dancing eyes = opsoclonus-myoclonus syndrome. Dx on NBME = urinary HVA and VMA." },
  { id: 121, category: "CNS Tumors", q: "Patient has brain cancer; next best step?", a: "Steroids." },

  // VISUAL PATHWAY
  { id: 122, category: "Visual Pathway", q: "31F with Hx of MS + contralateral inferior quadrantanopsia. Where is the pathology?", a: "Right parietal lobe (parietal lobe lesions cause contralateral inferior quadrantanopsia)." },
  { id: 123, category: "Visual Pathway", q: "45F + lung cancer + 2-week Hx of progressive loss of vision of the left visual field of both eyes. Metastases might be seen where?", a: "Right occipital lobe. Dx is homonymous hemianopsia." },
  { id: 124, category: "Visual Pathway", q: "52M + sudden loss of vision in right eye + central scotoma + fundoscopy shows pale opaque fundus and bright red fovea. 8 months later, if right eye is illuminated, what reaction in left pupil?", a: "No constriction — retinal ganglion cells in right eye have been destroyed. Dx is central retinal artery occlusion." },
  { id: 125, category: "Visual Pathway", q: "45M + left pupil larger than right pupil after cranial surgery. Where is the pathology?", a: "CN III (oculomotor nerve) in the cavernous sinus. Can cause down-and-out pupil and/or mydriasis." },
  { id: 126, category: "Visual Pathway", q: "24M + left eye fails to constrict when light is shone in both eyes. Where is the lesion?", a: "Oculomotor nerve (CN III)." },
  { id: 127, category: "Visual Pathway", q: "69M + smoker for 50 years + constricted left pupil + left eyelid droopy + skin dry on left side of face. Where is the lesion?", a: "Pancoast tumor of lung resulting in impingement on superior cervical ganglia (Horner syndrome)." },
  { id: 128, category: "Visual Pathway", q: "Shining light in either eye causes direct and consensual pupillary constriction. Test of functional integrity of what?", a: "Midbrain (Edinger-Westphal nucleus)." },
  { id: 129, category: "Visual Pathway", q: "45F + fundoscopy shows hard exudates + cotton wool spots + scattered hemorrhages. Dx?", a: "Diabetic retinopathy." },

  // CAVERNOUS SINUS
  { id: 130, category: "Cranial Nerves", q: "34M + sinus infection one week ago + now presents with diplopia, ophthalmoplegia, headache + fever of 103F. Dx?", a: "Cavernous sinus thrombosis. Sinus infections can ascend to cavernous sinus via valveless facial veins." },
  { id: 131, category: "Cranial Nerves", q: "41F + new-onset neurologic dysfunction following surgery of her sphenoid sinus. What additional finding is likely present?", a: "Inability to abduct eye (CN VI injury). CN VI is most medial/closest to sphenoid sinus." },
  { id: 132, category: "Cranial Nerves", q: "49M + prolactinoma + bitemporal hemianopsia. What other eye finding might be present?", a: "Inability to abduct eye (CN VI injury). Pituitary tumor expanding laterally can cause CN VI dysfunction." },

  // SEIZURES
  { id: 133, category: "Seizures", q: "6M + ECG shows miscellaneous arrhythmia + seizure-like episode. Dx?", a: "Adams-Stokes attack. Not a true seizure — arrhythmia leads to hypoxia of brainstem causing seizure-like fits." },
  { id: 134, category: "Seizures", q: "75M + episodes of loss of consciousness for 2 years + tonic-clonic-like episodes + becomes pale and sweaty + Hx of MI. Dx?", a: "Syncope (convulsive syncope) on NBME." },
  { id: 135, category: "Seizures", q: "26F + tonic-clonic seizure + immediately prior smelled foul odor. Where did the seizure originate?", a: "Temporal lobe (olfactory aura)." },
  { id: 136, category: "Seizures", q: "10-month old boy + jerking movements of limbs + EEG shows chaotic high-amplitude spikes with no recognizable pattern. Dx?", a: "West syndrome (infantile spasms). Triad: spasms + hypsarrhythmia on EEG + developmental regression. Tx = ACTH." },
  { id: 137, category: "Seizures", q: "13M + tonic-clonic seizure + 4-month Hx of hypnagogic/hypnopompic jerking of left arm + uncle has epilepsy. Dx?", a: "Juvenile myoclonic epilepsy. Tx is valproic acid." },
  { id: 138, category: "Seizures", q: "4F + few-month Hx of near-daily seizures + seizures while sleeping + started putting objects in mouth + making less eye contact + not responding to meds. Dx?", a: "Lennox-Gastaut syndrome. Severe childhood-onset epilepsy with cognitive decline. Hyperoralism = sign of cognitive regression." },

  // INFECTIONS
  { id: 139, category: "Infections", q: "24M + herpes encephalitis + treated with IV acyclovir + months later has hyperphagia, hypersexuality, hyperorality. Dx?", a: "Kluver-Bucy syndrome (bilateral amygdala lesions). Rare complication of HSV encephalitis." },
  { id: 140, category: "Infections", q: "22F returns from Central America + tonic-clonic seizure + CT of head shows 'swiss cheese' appearance. Dx?", a: "Neurocysticercosis (Taenia solium). Tx = albendazole or praziquantel." },
  { id: 141, category: "Infections", q: "AIDS patient with CD4 count of 47/uL + cognitive degeneration + miscellaneous peripheral neurologic findings. Dx?", a: "Progressive multifocal leukoencephalopathy (PML) caused by JC polyoma virus. USMLE wants 'reactivation of latent infection.'" },
  { id: 142, category: "Infections", q: "1-year-old boy + hypotonia + honey consumption. Dx?", a: "Botulism — ingestion of spores from honey (Clostridium botulinum)." },
  { id: 143, category: "Infections", q: "13M + camping trip + Bell palsy + constipation + hypotonia. Dx?", a: "Botulism — ingestion of preformed toxin from compromised canned goods. Tx = anti-toxin." },
  { id: 144, category: "Infections", q: "3-day-old male + born at home + umbilical cord tied with twine + arching of back. Mechanism?", a: "Tetanus — blockade of inhibitory neurotransmitter release (GABA and glycine) by inhibiting SNARE protein." },
  { id: 145, category: "Infections", q: "Neonate + intracranial calcifications + chorioretinitis + hydrocephalus. Dx?", a: "Congenital toxoplasmosis." },
  { id: 146, category: "Infections", q: "Neonate + intracranial calcifications + deafness + hepatomegaly + rash. Dx?", a: "Congenital CMV." },
  { id: 147, category: "Infections", q: "Neonate with bilateral deafness due to maternal infection + no other info given. Dx?", a: "Congenital CMV." },
  { id: 148, category: "Infections", q: "24M + burning vesicular lesions around the lips. Mechanism of this pathogen's presentation?", a: "Reactivation in sensory neurons. Herpes labialis (HSV1/2) — virus lies dormant in trigeminal nerve." },

  // NMJ
  { id: 149, category: "Neuromuscular", q: "44F + diplopia + dysphagia + eyelid ptosis; all worsen throughout the day. Dx?", a: "Myasthenia gravis. Antibodies against postsynaptic nicotinic acetylcholine receptors." },
  { id: 150, category: "Neuromuscular", q: "44F + proximal muscle weakness + able to perform upward gaze without a problem for 60 seconds. Dx?", a: "Lambert-Eaton syndrome. If cannot perform upward gaze for 60 sec = MG." },
  { id: 151, category: "Neuromuscular", q: "44F + difficulty getting up from chair but is able to after several attempts. Dx?", a: "Lambert-Eaton syndrome. Muscle weakness that improves with activity." },
  { id: 152, category: "Neuromuscular", q: "Vignette where Dx is either MG or LE but it's not listed; answer?", a: "'Neuromuscular junction.'" },
  { id: 153, category: "Neuromuscular", q: "Mechanism of MG vs LE?", a: "MG = antibodies against postsynaptic acetylcholine receptors; LE = antibodies against presynaptic voltage-gated calcium channels." },
  { id: 154, category: "Neuromuscular", q: "MG can sometimes be paraneoplastic syndrome of which cancer?", a: "Thymoma. Do chest imaging after Dx of MG; if thymoma present + removed, this cures the MG." },
  { id: 155, category: "Neuromuscular", q: "LE can sometimes be a paraneoplastic syndrome of which cancer?", a: "Small cell lung cancer." },
  { id: 156, category: "Neuromuscular", q: "How do MG vs LE perform with edrophonium?", a: "MG improves drastically; LE less change." },

  // GBS
  { id: 157, category: "Neuromuscular", q: "13F + 2-day Hx of lower limb paresthesias + CSF protein 95 mg/dL + CSF leukocyte count 4/uL. Dx?", a: "Guillain-Barre syndrome (GBS). CSF shows albuminocytologic dissociation (high protein, normal cells)." },
  { id: 158, category: "Neuromuscular", q: "24M + weakness proximally and distally in lower limbs + weakness distally in upper limbs. Dx?", a: "GBS — ascending paralysis has ascended in lower limbs but not yet in upper limbs." },
  { id: 159, category: "Neuromuscular", q: "Mechanism of GBS?", a: "T cell attack against Schwann cells of PNS." },
  { id: 160, category: "Neuromuscular", q: "Tx of GBS?", a: "IVIG + plasmapheresis; steroids are the wrong answer." },

  // CONGENITAL / PEDIATRIC
  { id: 161, category: "Pediatric", q: "Newborn + myelomeningocele. What is the affected developmental process?", a: "Closure of caudal neuropore." },
  { id: 162, category: "Pediatric", q: "23F at 20 weeks gestation + ultrasound shows fetus with anencephaly. Mechanism?", a: "Failure of closure of rostral neuropore." },
  { id: 163, category: "Pediatric", q: "Neonate + tuft of hair on midline in lumbar region + absence of spinous process. Mechanism?", a: "Failure of fusion of the sclerotomes (spina bifida occulta)." },
  { id: 164, category: "Pediatric", q: "MRI showing inferior herniation of cerebellar tonsils in a teenager. Diagnosis?", a: "Chiari I malformation. Can be associated with syringomyelia." },
  { id: 165, category: "Pediatric", q: "MRI showing absent cerebellar vermis + cystic dilation of fourth ventricle. Diagnosis?", a: "Dandy-Walker malformation." },
  { id: 166, category: "Pediatric", q: "Floppy baby syndrome — Dx and location of CNS/PNS affected?", a: "Werdnig-Hoffmann syndrome (spinal muscular atrophy). Anterior horns affected. Presents with profound hypotonia, absent reflexes, and tongue fasciculations." },
  { id: 167, category: "Pediatric", q: "23M + inferonasal 'bleeding' of the pupil + incomplete closure of embryonic fissure. What structure is responsible?", a: "Iris. CHARGE syndrome presents with coloboma of the eye." },
  { id: 168, category: "Pediatric", q: "Newborn + strabismus. Rationale for surgically correcting during early childhood?", a: "If not treated, normal binocular vision won't develop." },
  { id: 169, category: "Pediatric", q: "7F + facial grimaces past 5 months + no other motor findings + mental status normal. Next best step?", a: "Schedule a follow-up examination in 3 months. Dx = provisional tic disorder." },
  { id: 170, category: "Pediatric", q: "6F + rheumatic fever + Sydenham chorea. Mechanism?", a: "Autoimmune disorder to the basal ganglia." },

  // VENTRICLES
  { id: 171, category: "Ventricles", q: "32M + hydrocephalus + MRI shows colloid cyst. Most likely location?", a: "Foramen of Monro. Colloid cysts originate from the roof of the anterior third ventricle." },
  { id: 172, category: "Ventricles", q: "72M + unsteady gait + personality change + urinary incontinence + Parkinsonism. Enlarged structures on CT are derived from which component of brain development?", a: "Telencephalon of the prosencephalon — dilated lateral ventricles in normal pressure hydrocephalus (wet, wobbly, wacky)." },
  { id: 173, category: "Ventricles", q: "7M + ingested substance under the kitchen since + vomiting. What part of the brain is responsible and where is it located?", a: "Area postrema — chemotactic trigger zone for emesis, located on dorsal aspect of medulla at caudal 4th ventricle." },

  // DEMENTIA / NEURODEGENERATIVE
  { id: 174, category: "Dementia", q: "61F + brought to ER confused + disheveled + broad-based gait and nystagmus + alcohol and drug screening negative. Brain MRI will show atrophy of what?", a: "Mammillary bodies. Dx is Wernicke encephalopathy (ACOW = Ataxia, Confusion, Ophthalmoplegia, Wernicke)." },
  { id: 175, category: "Dementia", q: "56M + alcoholism + acutely intoxicated + B1 is administered; the latter decreases what most significantly?", a: "Anterograde amnesia (Wernicke encephalopathy)." },
  { id: 176, category: "Dementia", q: "68M + transient ischemic attack + new-onset anterograde amnesia. Most likely affected location?", a: "Hippocampus — very sensitive to ischemic insult." },
  { id: 177, category: "Dementia", q: "23M + near-drowning episode with hypoxia to brain. What change might be seen in the hippocampi?", a: "'Red neurons' — pathologic staining pattern during acute hypoxic injury. Hippocampi are notably susceptible to ischemia." },

  // HEADACHES
  { id: 178, category: "Headaches", q: "59F + temporal headache + muscle pain and stiffness + high ESR. Dx and next best step?", a: "Temporal arteritis + polymyalgia rheumatica. Next step = IV methylprednisolone first, then temporal artery biopsy." },
  { id: 179, category: "Headaches", q: "50F + jaw pain + headaches + normal ESR. Dx?", a: "Temporal mandibular joint syndrome. If ESR is high, answer is jaw claudication caused by temporal arteritis." },
  { id: 180, category: "Headaches", q: "32M + diffuse headache relieved by acetaminophen + sleep. Dx?", a: "Tension-type headache. Tx = rest + taper caffeine." },
  { id: 181, category: "Headaches", q: "Tx and prophylaxis for cluster headache?", a: "Tx = 100% oxygen; prophylaxis = verapamil." },
  { id: 182, category: "Headaches", q: "Tx and prophylaxis for trigeminal neuralgia?", a: "Tx = goes away on its own (lasts only seconds); prophylaxis = carbamazepine." },
  { id: 183, category: "Headaches", q: "Tx and prophylaxis for migraine?", a: "Tx = NSAID, then triptan (triptans are NOT prophylaxis); prophylaxis = propranolol." },
  { id: 184, category: "Headaches", q: "23F + Hx of migraines. Which chemical mediator may contribute to her Sx?", a: "Substance P." },

  // VERTIGO / HEARING
  { id: 185, category: "Vertigo", q: "40F + episodes of room spinning + sometimes with vomiting + physician reproduces Sx with Dix-Hallpike maneuver. Mechanism?", a: "Posterior semicircular canal otolith. Dx = BPPV. Tx with Epley maneuver." },
  { id: 186, category: "Vertigo", q: "40F + viral infection + tinnitus + hearing loss + vertigo. Dx?", a: "Labyrinthitis." },
  { id: 187, category: "Vertigo", q: "40F + viral infection + vertigo (no hearing loss). Dx?", a: "Vestibular neuritis." },
  { id: 188, category: "Vertigo", q: "32M + waxing and waning tinnitus and hearing loss + difficulty hearing conversations at dinner + family Hx. Dx?", a: "Meniere disease — low-frequency hearing loss. Mechanism = defective endolymphatic drainage." },
  { id: 189, category: "Vertigo", q: "55F + few-month Hx of spinning + when head hangs off examination table she develops coarse, rotary nystagmus. Dx?", a: "BPPV. Dx with Dix-Hallpike maneuver. Tx with Epley maneuver." },
  { id: 190, category: "Vertigo", q: "31M + warm water instilled into left ear causes nystagmus, but warm water in right ear does not. Where is the lesion?", a: "Right-sided vestibular apparatus. If nystagmus fails to occur with stimulation, there is weakness on that side." },
  { id: 191, category: "Vertigo", q: "25M IV drug user + Tx for endocarditis + now the room is spinning. Dx?", a: "CN VIII toxicity caused by aminoglycoside (gentamicin)." },
  { id: 192, category: "Vertigo", q: "3M + pinna displaced upward and outward + fever. Dx?", a: "Mastoiditis. Next best step = CT or MRI of temporal bone (x-ray is wrong)." },

  // DRUG SIDE EFFECTS
  { id: 193, category: "Pharmacology", q: "Antipsychotic medication started + muscle rigidity + no fever. Dx + Tx?", a: "Acute dystonia. Tx with benztropine (muscarinic receptor antagonist) or diphenhydramine." },
  { id: 194, category: "Pharmacology", q: "Antipsychotic + abnormal eye movements + stiff neck. Dx?", a: "Acute dystonia (oculogyric crisis + torticollis)." },
  { id: 195, category: "Pharmacology", q: "Antipsychotic + muscle rigidity + fever. Dx + Tx?", a: "Neuroleptic malignant syndrome. Tx = dantrolene (inhibits ryanodine channel)." },
  { id: 196, category: "Pharmacology", q: "Antipsychotic med + restlessness. Dx + Tx?", a: "Akathisia. Tx with propranolol." },
  { id: 197, category: "Pharmacology", q: "Antipsychotic med + bradykinesia. Dx + Tx?", a: "Drug-induced Parkinsonism. Tx with amantadine or propranolol." },
  { id: 198, category: "Pharmacology", q: "Antipsychotic med + abnormal tongue movements. Dx + Tx?", a: "Tardive dyskinesia. Stop antipsychotic + switch to atypical." },
  { id: 199, category: "Pharmacology", q: "Medication that can cause tardive dyskinesia that is not an antipsychotic?", a: "Metoclopramide (D2 antagonist). Can also prolong QT and cause hyperprolactinemia." },
  { id: 200, category: "Pharmacology", q: "Anti-depressant med causing seizures?", a: "Bupropion." },
  { id: 201, category: "Pharmacology", q: "Cancer patient on cisplatin or vincristine + develops neuropathy. Dx?", a: "Toxic neuropathy (chemotherapy-induced)." },
  { id: 202, category: "Pharmacology", q: "40F being treated for TB + neurologic findings in extremities +/- seizure. Dx?", a: "B6 (pyridoxine) deficiency caused by isoniazid." },
  { id: 203, category: "Pharmacology", q: "Tx for diabetic neuropathic pain?", a: "TCA (amitriptyline) first-line. Second-line is gabapentin." },
  { id: 204, category: "Pharmacology", q: "Tx for herpetic / post-herpetic neuralgia?", a: "Gabapentin." },
  { id: 205, category: "Pharmacology", q: "82M diabetic + neuropathic pain + already taking carbamazepine + gabapentin to no avail. Next best step?", a: "Switch to nortriptyline (TCA). Nortriptyline over amitriptyline in elderly — fewer adverse effects." },

  // MISCELLANEOUS
  { id: 206, category: "Miscellaneous", q: "59F + metastatic cancer + in pain + crying + 'wants to die.' Most likely reason?", a: "Inadequate pain control. 'Major depression' is wrong — must address pain management in cancer patients." },
  { id: 207, category: "Miscellaneous", q: "42F + 3-month Hx of insomnia + discomfort while lying in bed. Next best step?", a: "Check serum iron and ferritin levels. Restless leg syndrome most often caused by iron deficiency." },
  { id: 208, category: "Miscellaneous", q: "42F + 3-month Hx of insomnia + discomfort while lying in bed + serum iron and ferritin are normal. Next best step?", a: "D2 agonist — pramipexole or ropinirole." },
  { id: 209, category: "Miscellaneous", q: "Patient with restless leg syndrome is at increased risk for what disease later in life?", a: "Parkinson disease." },
  { id: 210, category: "Miscellaneous", q: "58M + loses consciousness while shaving + tilt-table test shows no abnormalities. Dx?", a: "Carotid sinus hypersensitivity. If tilt-table test (+), answer = vasovagal syncope." },
  { id: 211, category: "Miscellaneous", q: "Frontal lobe injury in car accident; which deficit is most likely?", a: "Conceptual planning." },
  { id: 212, category: "Miscellaneous", q: "56M + 3-day Hx of cutting from 12 beers a day down to 4; develops tremulousness. Tx?", a: "Chlordiazepoxide (for delirium tremens)." },
  { id: 213, category: "Miscellaneous", q: "87F + Alzheimer + low-grade fever + delirium. Next best step?", a: "Urinalysis to look for UTI as cause of delirium." },
  { id: 214, category: "Miscellaneous", q: "What cell does HIV infect in the CNS?", a: "Microglia — one of the major cellular reservoirs of HIV." },
  { id: 215, category: "Miscellaneous", q: "51M + hereditary hemochromatosis + isolated decrease in serum gonadotropins. Most likely location of pathology?", a: "Hypothalamus — iron deposition causing decreased GnRH." },
  { id: 216, category: "Miscellaneous", q: "16F + MVA + pituitary stalk is severed. Which hormone will increase?", a: "Prolactin. All hypothalamic hormones are stimulatory except dopamine's actions on prolactin (inhibitory)." },
  { id: 217, category: "Miscellaneous", q: "24F + complains food has lost its flavor since getting hit in the head during a softball game. Damage to which structure?", a: "Cribriform plate. Olfactory nerve lesion leads to decreased perception of taste." },
  { id: 218, category: "Miscellaneous", q: "22F + says cannot see out of left eye + examination shows no relative afferent pupillary defect. Dx?", a: "Conversion disorder. If she truly had impaired vision, Marcus-Gunn pupil would be present." },
  { id: 219, category: "Miscellaneous", q: "38F + hoarseness of voice + various stress factors. Dx?", a: "Conversion disorder." },
  { id: 220, category: "Miscellaneous", q: "20F + stiffness of hands + frontal balding + impaired relaxation of hypothenar muscles. Dx?", a: "Myotonic dystrophy (CTG TNR disorder)." },
  { id: 221, category: "Miscellaneous", q: "Mechanism of narcolepsy?", a: "Deficiency of orexin (hypocretin)." },
  { id: 222, category: "Miscellaneous", q: "Diagnosis of narcolepsy?", a: "Polysomnography (sleep study)." },
  { id: 223, category: "Miscellaneous", q: "Tx of narcolepsy?", a: "Stimulants (modafinil)." },
  { id: 224, category: "Miscellaneous", q: "22F + fluoxetine prescribed; benefit occurs due to effects on neurons located where?", a: "Raphe nuclei (serotonin-secreting neurons)." },
  { id: 225, category: "Miscellaneous", q: "57F + invasive gall bladder cancer + 3-week Hx of severe left-sided back and abdominal pain. Operation to relieve pain would target which spinal tract?", a: "Right spinothalamic tract (contralateral)." },
  { id: 226, category: "Miscellaneous", q: "42F + 4-month Hx of tingling that started in right hand and progressed to right arm and right side of face. Lesion in which cerebral cortex gyri?", a: "Left post-central (posterior to central sulcus — primary sensory cortex)." },
  { id: 227, category: "Miscellaneous", q: "72F + loss of pain and temperature on left side of face and right of body + paralysis of vocal cords on left + loss of gag reflex on left. Part of brainstem most likely affected?", a: "Left dorsolateral medulla. Lateral medullary syndrome; CN IX/V dysfunction." },
  { id: 228, category: "Miscellaneous", q: "61F + repair of leaking saccular aneurysm + postoperative CT shows widening of subarachnoid space. Cause?", a: "Decreased movement of CSF through the arachnoid villi." },
  { id: 229, category: "Miscellaneous", q: "42F + struck in left eye by golf ball + diplopia + periorbital swelling + enophthalmos + impaired upward gaze + decreased sensation over left zygoma + orbital floor fracture. Entrapment of which two muscles?", a: "Inferior rectus and inferior oblique." },
  { id: 230, category: "Miscellaneous", q: "3M + moderate strabismus. Calcium entry through which receptor mediates competitive interactions in the visual cortex?", a: "NMDA (glutamate) receptors." },

  // SPINAL CORD COMPRESSION
  { id: 231, category: "Spinal Cord", q: "68M + Hx of prostate cancer + now has neurologic findings. Next best step?", a: "MRI of spine to look for mets. However, if corticosteroids are listed, choose those before MRI." },
  { id: 232, category: "Spinal Cord", q: "65F + breast cancer + neurologic findings. Next best step?", a: "Intravenous high-dose dexamethasone." },
  { id: 233, category: "Spinal Cord", q: "65F + metastatic breast cancer + suprapubic mass + decreased sphincter tone + pain over lumbar vertebrae. Dx?", a: "Metastases to cauda equina." },

  // MENINGITIS WORKUP
  { id: 234, category: "Infections", q: "When do you do CT head before LP in suspected meningitis? (4 indications)", a: "1) Focal neurologic signs, 2) Seizure, 3) Papilledema or optic fundi cannot be visualized, 4) Confusion that interferes with neurologic exam / decreased GCS." },
  { id: 235, category: "Infections", q: "Bacterial meningitis CSF findings?", a: "Low glucose, high protein, high neutrophils (PMNs)." },
  { id: 236, category: "Infections", q: "Viral (aseptic) meningitis CSF findings?", a: "Normal glucose, normal (or slightly elevated) protein, high lymphocytes." },
  { id: 237, category: "Infections", q: "Fungal meningitis CSF findings?", a: "Low glucose, high protein, high lymphocytes (similar to bacterial but lymphocytes instead of neutrophils)." },
  { id: 238, category: "Infections", q: "Herpes encephalitis CSF findings?", a: "Lots of RBCs in CSF due to temporal lobe hemorrhage. CT is often negative. EEG shows temporal complexes. Tx = IV acyclovir." },
  { id: 239, category: "Infections", q: "Dx of Cryptococcal meningitis?", a: "Latex agglutination (if listed over India ink). Mucicarmine staining (red stain) can also be done." },

  // CAROTID WORKUP
  { id: 240, category: "Strokes", q: "55M + BP 150/90 + TIA. Next best step in Mx?", a: "Carotid duplex USS — look for carotid plaque that embolized to brain." },
  { id: 241, category: "Strokes", q: "80M + good blood pressure + stroke or TIA. Next best step?", a: "ECG — look for atrial fibrillation. If normal, do Holter monitor (AF is often paroxysmal)." },
  { id: 242, category: "Strokes", q: "55M + good BP + carotid bruit. Next best step?", a: "Carotid duplex ultrasound to look for carotid plaques." },
  { id: 243, category: "Strokes", q: "Carotid occlusion >70% if symptomatic, or >80% if asymptomatic — answer?", a: "Carotid endarterectomy. Below those thresholds = medical management (statin + clopidogrel OR dipyridamole + aspirin)." },

  // MUSCLE
  { id: 244, category: "Miscellaneous", q: "50F + high ESR and CK + proximal muscle weakness +/- muscle pain. Dx?", a: "Polymyositis." },
  { id: 245, category: "Miscellaneous", q: "50F + high ESR + no high CK or weakness + muscle pain + muscle stiffness. Dx?", a: "Polymyalgia rheumatica (PMR). No proximal muscle weakness + normal CK." },
  { id: 246, category: "Miscellaneous", q: "48F + high ESR and CK + proximal muscle weakness. Next best step in Dx?", a: "Anti-Jo1 / Mi2 antibodies or EMG and nerve conduction studies (to Dx polymyositis)." },
  { id: 247, category: "Miscellaneous", q: "38F + papilledema on fundoscopy + flushing of face / venous distension of head + neck. Dx?", a: "SVC syndrome. NBME wants 'obstruction of venous return to the heart.'" },
];

export default neuroQuestions;
