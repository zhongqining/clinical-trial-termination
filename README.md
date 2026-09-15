30,000 trials

11% Positive Class

terminated

0    0.888817

1    0.111183


Phase Distribution		

Phase           mean	  count

EARLY_PHASE1	0.112108	223

NA	          0.073622	8272

PHASE1	      0.131214	2454

PHASE2	      0.204052	2073

PHASE3	      0.147263	1297

PHASE4	      0.127886	1126


Termination rate varies substantially by phase, from 7% for non-drug (NA) trials up to 20% for Phase 2 - the efficacy-testing stage where treatments most often fail. Phase is a meaningful predictor."


Sponsor Class Distribution

sponsor_class	mean	count

FED	0.118056	144

INDIV	0.000000	17

INDUSTRY	0.135651	4401

NETWORK	0.113924	79

NIH	0.190840	131

OTHER	0.102005	10372

OTHER_GOV	0.041009	317


"Sponsor class varies 4%–19%; INDUSTRY (13.6%) terminates MORE than academic OTHER (10.2%) — opposite of the 'industry staying power' expectation, possibly because commercial sponsors cut unpromising trials fast. OTHER_GOV lowest at 4%. Small groups (INDIV, NIH) noisy."



LEAKAGE

terminated

0    60.0

1    19.0

Name: enroll_count, dtype: float64




"Termination rate is stable over 2010–2022 (~9-13%, no strong trend), so the temporal train/test split is valid — no major drift to worry about."


1. Class balance — 11.1% terminated (imbalanced, confirmed).

2. Phase — signal, 7% (NA) to 20% (PHASE2), medically sensible.

3. Sponsor class — signal, but surprising direction (industry terminates more than academic).

4. Enrollment — the leakage discovery, with the ESTIMATED-safe/ACTUAL-leaky proof.

5. Year — stable, temporal split validated.
