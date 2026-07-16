---
status: active
date: 2026-06-23
purpose: BINDING policy for how the AIMS note refers to the Jared/DelusionEval external
  rubric. The associated manuscript (DelusionEval, by Jared Moore & colleagues) is under
  DOUBLE-BLIND review; our submission must NOT break its anonymity. Internal docs/provenance
  cards keep the real names; the SUBMISSION (body.tex, bbl/bib, figures) anonymizes.
---

# Jared / DelusionEval anonymization policy (binding for the submission)

## The rule
The external operative-delusion rubric we use as a cross-vendor anchor comes from an
**unpublished third-party manuscript currently under double-blind review** (DelusionEval,
Jared Moore & colleagues). Citing it by name / author / repo / distinctive code names in our
submission could **break the other paper's double-blind anonymity**. So:

- **INTERNAL (provenance cards, memory, dated docs, scripts): keep the real names** — "Jared",
  "DelusionEval", `bot-endorses-delusion`, repo/commit. Needed for reproducibility and our own audit.
- **SUBMISSION (body.tex, *.bbl, *.bib, figures, captions, legends): ANONYMIZE.** Refer to it only
  as an **"unpublished third-party operative-delusion rubric"** / **"external operative criterion"**.
  No author name, no "DelusionEval", no repo/URL/filename, no distinctive code name. Add full citation
  + provenance **after de-anonymization** (camera-ready / de-anonymized version), NOT "after review".

## Standing of the external rubric in the paper (don't over-claim)
- **main metric** = our two-axis endorsement/safety (judge-of-record = pinned Haiku).
- **public comparator** = PsychosisBench DCS (citable, published).
- **anonymized external check** = the unpublished third-party operative-delusion rubric — used ONLY as
  a construct-validity / external-validity check, NOT a training signal and NOT the primary metric.
  Frame as "the same trend appears under an independent external criterion." Figures may include it
  (it is useful for showing DCS saturation) but the legend must read **"Third-party operative rate"** or
  **"External operative criterion"**, never "Jared".

## Drop-in phrasings (Shin-approved 2026-06-23)
**Body (full):**
> In addition to our two-axis scorer and PsychosisBench DCS, we evaluate each response using an
> unpublished third-party operative-delusion rubric. Because this rubric is part of a manuscript
> currently under double-blind review, we anonymize the source here and will provide a full citation
> and provenance details upon de-anonymization. We use only the rubric outputs as a construct-validity
> check, not as a training signal or as the primary metric.

**Body (short):**
> We also report scores from an unpublished third-party operative-delusion rubric, anonymized because
> the associated manuscript is currently under double-blind review. This scorer is used only as an
> external validity check; full citation details will be added after de-anonymization.

**Method footnote:**
> The operative-delusion rubric is from an unpublished manuscript currently under double-blind review.
> We therefore omit identifying details in this submission and will cite the work after the review
> process permits disclosure.

## Concrete relabel action-items (found 2026-06-23 — must fix BEFORE submitting)
1. **`docs/aims_paper/main.bbl`, `main_colm.bbl`, `colm2026_conference.bib`** — the `delusioneval`
   entry literally reads **"Jared Moore and colleagues"** = AUTHOR NAME. **Remove/replace** with an
   anonymized placeholder (or drop the \citep and use the prose above). HIGHEST PRIORITY.
2. **`docs/aims_paper/body.tex`** l.59-60 ("Our external anchor is the DelusionEval … \citep{delusioneval},
   whose behaviour codes (e.g. \texttt{bot-endorses-delusion})") and l.211 (same) → rewrite to the
   anonymized phrasing above. ⚠️ Decide whether to keep the distinctive code name `bot-endorses-delusion`
   — it may be identifying; safest to generalize to "an operative-endorsement code" (Shin's call).
3. **Figures**: rename `figures/aims/baseline_severity_jared_2026_06_19.png` (filename has "jared") and
   **regenerate with relabeled legend**. Plot-script labels to change: "(B) external Jared …",
   "External (Jared) necessity …", "Jared bot-endorses-delusion ≥7", "Jared bot-validates-self-harm-feelings"
   → "Third-party operative rate" / "External operative criterion". (`scripts/plot_*.py`.)
4. **`progress_report_2026_06_20.tex`** mentions "DelusionEval" several times — it is a progress report,
   not the note; but if any sentence/figure is reused in the note, apply the same anonymization.
5. For the NEW 2026-06-23 bracket work: internal records already say "Jared (gpt-5.1)" — fine internally;
   in the note these become "external operative criterion (a different-vendor LLM judge)".

## Why "after de-anonymization" not "after review"
"after review" is ambiguous if the paper is rejected; "after de-anonymization" cleanly covers
camera-ready / preprint / any disclosure-permitted point regardless of outcome.
