# OSF Submission Packet — Will Breaker (prepared 2026-10-26)

Owner action required: OSF account login + final submit clicks. This
packet makes that a copy-paste job. Two components:

- **Part A — Exp 1 pre-registration** (future human study; register
  BEFORE any recruitment). Source draft: `OSF_PRE_REGISTRATION.md`.
- **Part B — Completed-study components** (register as project
  components with data/code; these are done science, NOT
  pre-registrations — label them as such).

## Part A: Exp 1 field mapping (OSF "OSF Preregistration" template)

| OSF field | Paste this |
|---|---|
| Title | Binaural Entrainment + Target Identification: A Randomized Controlled Trial |
| Authors | OWNER DECISION: real name or `comandante`. OSF permits either; pick before submitting, it is frozen. |
| Description | Randomized, within-subjects crossover test of whether theta (7 Hz) binaural-beat induction improves blind target identification vs monaural-beat control, judged blind against a 20-target pool (sum-of-ranks, chance mean rank 10.5). Negative results will be published. |
| Hypotheses | H1 (primary): within-subjects mean target rank is lower (better) in binaural than monaural condition. H2 (secondary): condition effect ≥ d=0.3. Exploratory: delta-detection flag correlation, shift-intensity correlates (no confirmatory claims — see gaps). |
| Study type | Experiment |
| Blinding | Participants blind to hypothesis (audio condition may be perceptible — add exit guess-check); target selection and judging blind. Do NOT claim double-blind for participants. |
| Design | Within-subjects crossover, counterbalanced order, 48h washout, 25-min induction + 10-min target description per session. |
| Existing data | Registration prior to creation of data |
| Sample size | SEE GAP 1 — recommend N=70 (power .81 at d=0.3, one-tailed paired α=.05). Draft's N=40 gives power .60. |
| Stopping rule | Fixed N; interim look at N=20 is safety/logistics ONLY (no efficacy test, no alpha spent). Draft must say this or drop the interim look. |
| Manipulated variables | Audio condition (binaural 7 Hz vs monaural control), within-subjects. |
| Measured variables | Blind-judge rank (1–20) of true target per trial (2 judges, mean); confidence; experience ratings; sleep/caffeine/mood covariates. |
| Indices | Primary: per-participant mean rank difference (monaural − binaural). |
| Statistical model | One-tailed paired t-test on per-participant mean-rank difference (Wilcoxon signed-rank as robustness check); Cohen's dz. SEE GAP 2. |
| Inference criteria | α=.05 one-tailed on the single primary contrast. All other analyses exploratory. |
| Data exclusion | Pre-declare: incomplete session, audio non-compliance (<20 of 25 min), judge disagreement rule (mean of 2 judges; no post-hoc judge dropping). |
| Missing data | Complete-cases for primary; report attrition per condition order. |

### Gaps the owner must close before clicking submit

1. **Power/N.** Draft N=40: paired power .60 at d=0.3 (.81 at d=0.4);
   the "20 vs 20" framing in the draft implies between-groups power
   .24 — unwinnable. Decide: N=70 for 80% power at d=0.3, or keep
   N=40 and pre-declare d≥0.4 as the smallest effect of interest.
   Budget effect: $50/participant → $2,000 (N=40) or $3,500 (N=70).
2. **Primary test inconsistency.** Draft mixes "sum of ranks" with
   "one-tailed binomial" (binomial needs a hit definition it never
   gives). Packet resolves to: paired test on mean ranks (primary).
   Delete the binomial or define a hit (e.g., rank ≤5) as a named
   secondary. Do not submit with both undefined.
3. **H4/H5 not operationalized.** "Delta-detection flags correlate
   ≥30%" and "Phi proxy" have no defined human-subjects instrument
   or unit of analysis in the procedure. Move to exploratory (done
   in mapping above) or define instruments before submitting.
4. **IRB/ethics.** Human audio experiment; draft says "IRB pending
   (if university-affiliated)". No affiliation is known — owner
   decides: independent ethics review, or register on OSF without
   recruitment until review exists. Do not recruit on the draft.
5. **Blinding language.** Replace "double-blind" with the mapping
   above + an exit guess-check item.
6. **PI identity** (see Authors row).

## Part B: completed-study components (add under the same OSF project)

Register as components, each with its repo path; describe as
completed with pre-commitment artifacts where true:

1. **Paper 010** — low-entropy attractor basins in LLM
   self-observation; cross-architecture replication
   (35B MoE + Llama-3.1-8B). `research/010-mechanistic-attractor-paper.md`
2. **Campbell AI-RV DB-FTCD battery** — N=30, NULL_RESULT (20% vs
   25% chance), pre-committed `commit_0bd66be14374` /
   `commit_22f3f2c9aa06`. `results/campbell_rv/`, `research/campbell/`
3. **Sealed prediction registry** — SHA-256 pre-commitments, 44
   sealed / 17+ resolved incl. Session 041 sports correction
   (13/22, Brier 0.2330). `notes/crypto_predictions_registry.jsonl`

## Submit checklist (owner, ~15 min)

1. osf.io → New Project "Will Breaker" → add Part B components.
2. Registrations → OSF Preregistration → paste Part A fields.
3. Close gaps 1–6 inline while pasting (decisions, not edits).
4. Submit; paste the OSF DOI back into `OSF_PRE_REGISTRATION.md`
   (replacing "TBD") and `will_breaker/PLAYBOOK.md` Exp 1 row.
