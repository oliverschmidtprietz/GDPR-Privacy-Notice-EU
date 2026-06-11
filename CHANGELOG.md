# Changelog — privacy-notice-eu

All notable changes to this skill are documented here.

Format: `## [vX.Y] — YYYY-MM-DD`

---

## [v1.2] — 2026-06-11

Output-discipline + audience-clarity guidance from the LegalQuants QA review (PR #7), which flagged this skill's finished, formatted .docx as the output a lawyer is most tempted to ratify rather than review. No change to the notice templates, intake flow, or jurisdiction references.

- **Confidence model that travels with the document (pre-merge fix).** Legal positions are tagged Settled / Assumed / Contested; contested points are NOT smoothed into authoritative prose — they render as highlighted **[TO CONFIRM WITH COUNSEL]** flags in the .docx and as explicit Assumptions / Open-items lists in the delivery summary.
- **Out-of-playbook STOP + stale-data caveat (pre-merge fix).** Jurisdictions beyond the nine loaded reference files now trigger a clean STOP + route to local counsel instead of silently defaulting to "GDPR defaults"; bundled article / adequacy-DPF / age-threshold data is flagged as point-in-time and to be re-verified against the live source.
- **"Who this is for" + work shape.** Names the operator (privacy practitioner / DPO / supporting lawyer; a non-lawyer must route output to counsel before publication) and the bounded, document-centric work shape.
- **Privilege note.** The gap findings surfaced alongside the notice are candid drafting observations, not legal advice and not in themselves a privileged work product.

**Status:** reviewed (carried from v1.1) — additive guidance and output discipline, no change to drafting logic.

---

## [v1.1] — 2026-05-31

Regulatory-horizon additions to `references/EU_COMMON.md` (no change to notice-drafting logic).

- **EDPB 2026 transparency enforcement (LIVE).** Flags the EDPB Coordinated Enforcement Framework action on transparency and the right to information (Arts. 12–14), launched 19 March 2026 — an active EU-wide enforcement priority. Reinforces full Art. 13/14 checklist completeness as elevated-risk in 2026.
- **Digital Omnibus reduced-transparency proposal (PROPOSED).** Flags the Commission's Digital Omnibus (COM(2025) 833 final, 19 Nov 2025) proposal to reduce Art. 13/14 transparency in limited cases — not in force; full obligations still apply.

**Status:** reviewed (carried from v1.0).

---

## [v1.0] — 2026-05-14

First **reviewed** release. Eval pass via `/skill-creator` confirmed skill value against no-skill baseline.

- 4 realistic test cases run with-skill vs no-skill baseline (40 assertions total)
- Result: 40/40 (100%) with skill vs 34/40 (85%) without — **+15 pp differential**
- Diagnostic finding: skill wins on structural discipline rather than raw doctrinal substance — notice-type-driven section-map articulation, precise statutory retention citations (TCA 1997 s. 886; § 15 AGG + Puffer), concrete docx delivery spec, CNIL doctrine specifics (Délibérations 2020-091/092), Art. 21 rendered as a dedicated blockquote on every output, correct BlnBDI address (Alt-Moabit 59-61 vs baseline's outdated Friedrichstr.), explicit governing-language clause
- Narrower differential reflects strong baseline knowledge of § 26 BDSG, AGG, L.34-5 CPCE; skill earns its keep on consistency and citation depth
- See `../../privacy-notice-eu-workspace/iteration-1/` for full eval artifacts

## [v0.9] — 2026-05-13

Version format normalised to SemVer per repo convention (`vX.Y`). Status: **pre-review** pending eval.

- Prior internal version string: `2026.02.09`
- No functional changes to skill content
