# Changelog — privacy-notice-eu

All notable changes to this skill are documented here.

Format: `## [vX.Y] — YYYY-MM-DD`

---

## [v1.6] — 2026-09-15

Adversarial-review correction pass (source: `docs/projects/gdpr-skills-marathon/ADVERSARIAL-REVIEW-2026-09-08.md`, findings 7 and 14). Legal-accuracy fixes only; no change to notice structure, templates or jurisdiction overlays.

- **Finding 7 — `references/EU_COMMON.md` multi-jurisdiction children's-age rule was wrong.** The rule instructed applying the **lowest** applicable Art. 8 age threshold across all target markets. This is incorrect: a German 14-year-old remains protected by Germany's 16-year threshold even if the service also operates in a 13-country — a Member State's threshold protects the children that Member State's law protects, determined by where the child is / which market the service is directed at, not by the controller's establishment. Replaced with the correct rule: apply each Member State's own threshold to its own market; where the service cannot reliably localise its users, apply the **highest** applicable threshold (16) as the fallback, since it is the only choice that cannot be wrong in any target market. Also corrected the same error where it recurred in the Art. 8 age-threshold table's Germany source citation.
- **Finding 14a — `references/DE.md` cited a nonexistent provision for Germany's consent age.** "§ 2 Nr. 17 TDDDG" was cited as a national implementation lowering the age to 16; § 2 TDDDG contains only definitions (Nr. 1–6) and no such provision exists. Germany has enacted no national derogation from the Art. 8(1) default — corrected to state 16 years applies as the GDPR default, with no lowering provision in BDSG or TDDDG. Audited the remaining TDDDG pinpoints in the skill (§ 25 cookie/tracking consent, § 176 TKG telecom traffic-data retention) — both check out against the statute and were left unchanged.
- **Finding 14b — `references/OTHER_EU.md` Spain citations were swapped/wrong.** "Art. 12 LOPDGDD: right to digital disconnection" and "Art. 89: right of rectification on the internet" were incorrect — Art. 12 is general provisions on exercising rights, Art. 89 is workplace video/audio surveillance. Corrected to Art. 88 LOPDGDD (derecho a la desconexión digital) and Art. 85 LOPDGDD (derecho de rectificación en internet), and clarified Arts. 79–97 LOPDGDD as the "derechos digitales" title. Audited the other Spanish pinpoints in the section (Art. 7 = age 14 for minors' consent) — correct, left unchanged.

## [v1.5] — 2026-08-21

Portfolio-audit correction pass (source: portfolio audit AUDIT-2026-08-19). Legal-accuracy and cross-skill consistency fixes; no change to notice structure, templates or jurisdiction overlays.

- **CF-03 — `references/DE.md` Art. 37(1) DPO-trigger citations were swapped.** The mandatory-DPO section tagged "systematic monitoring" as Art. 37(1)(c) and left the special-categories line uncited. Corrected: special-category/criminal-data processing is Art. 37(1)(c); systematic monitoring is Art. 37(1)(b).
- **CF-04 — `references/FR.md` cited the same provision for two different retention periods.** The retention table cited Art. 2224 Code civil for both a 5-year period (commercial contracts) and a 6-year period (cookie consent proof), four rows apart. Art. 2224 sets France's general limitation period at 5 years; there is no reading of it that yields 6. Corrected the cookie-consent-proof row to 5 years.
- **CF-16 — `references/EU_COMMON.md` conflated the two EU AI Act application dates.** Art. 50 transparency obligations were framed as applicable "from August 2025 onwards"; that date covers GPAI/governance obligations only (Art. 113(a)). Art. 50 itself applies from 2 August 2026 (Art. 113(b)) — matching `ai-act-transparency/SKILL.md`. The applicability statement is now split: GPAI/governance from 2 Aug 2025, Art. 50 transparency from 2 Aug 2026 (now in force).

---

## [v1.4] — 2026-07-21

Digital Omnibus instrument-citation correction. Legal-accuracy patch; no change to notice structure, templates or jurisdiction overlays.

- **`references/EU_COMMON.md` — wrong instrument corrected.** The Digital Omnibus proposal was cited as *COM(2025) 833 final*. The Digital Omnibus package of 19 November 2025 is **COM(2025) 836** (Digital Omnibus on AI, 2025/0359(COD)), **COM(2025) 837** (Digital Omnibus Regulation — data, privacy and cybersecurity, 2025/0360(COD), carrying the GDPR amendments in **Article 3**) and **COM(2025) 838** (European Business Wallets). **No Commission proposal bears the number COM(2025) 833** — EUR-Lex has no `52025PC0833`. The transparency regulatory-horizon note now cites COM(2025) 837 final, procedure 2025/0360(COD), GDPR amendments at Article 3, with an instrument note and primary-source URL.
- **Substance unaffected.** The proposed narrowing of the Art. 13/14 transparency burden was described correctly; only the document identifier was wrong.
- Verified 2026-07-21 against EUR-Lex (CELEX 52025PC0837) and the European Parliament Legislative Train entry for the digital package; corroborated by `data-subject-rights/sources/verification-log.md` §4.1.

**Status:** reviewed (carried from v1.3).

---

## [v1.3] — 2026-07-07

Group G DPIA-indicator correction (legal accuracy) + sibling wiring.

- Added the missing 9th WP248 rev.01 criterion ("processing that prevents data subjects from exercising a right or using a service or contract") — Group G previously listed only 8 of 9.
- "Appears to be required" reframed as a **rebuttable presumption** at 2+ criteria, matching dpia-sentinel's (correct) framing — the two skills previously diverged on the legal test.
- Group G now explicitly defers threshold ownership to the `dpia-sentinel` skill and routes users there for the full assessment and jurisdiction overlays (previously described a DPIA "as a separate exercise" without naming the sibling skill).

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
