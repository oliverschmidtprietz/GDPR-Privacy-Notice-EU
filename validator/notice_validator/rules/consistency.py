"""CONSIST-1 and AGE-1 : consequential-invalid-input rules for the delivery
summary's own Settled/Assumed/Contested and children's-age content
(SKILL.md 'Confidence and what gets handed back', EU_COMMON.md 'Children's
Data'). Findings-based; every rule here is defensive against malformed input
(SCHEMA-1 already reports the shape violation — these rules simply decline
to double-report it) rather than raising.
"""
from ..findings import Finding
from ..registry import rule

_CONSIST_SPEC = "SKILL.md#confidence-and-what-gets-handed-back"
_AGE_SPEC = "references/EU_COMMON.md#multi-jurisdiction-rule"

# Art. 8 GDPR age thresholds for the jurisdictions this skill's reference
# files cover (references/EU_COMMON.md 'Age Thresholds by Member State').
# UK is not an EU Member State but is carried in references/OTHER_EU.md
# alongside the others; its DPA 2018 s.9 threshold (13) is included here on
# the same footing.
_AGE_THRESHOLDS = {
    "AT": 14, "BE": 13, "DE": 16, "ES": 14, "FR": 15,
    "IE": 16, "IT": 14, "NL": 16, "UK": 13,
}


@rule(id="CONSIST-1", severity="rejection", category="consistency",
      description="A contested item must carry its [TO CONFIRM WITH COUNSEL] flag "
                  "before delivery. This fires regardless of notice.art13_14_compliant "
                  "— omitting that claim is not a way to bypass the check (break-it "
                  "test 2026-10-02, probe05: the claim was absent, not false, and the "
                  "unflagged item still shipped).",
      spec_anchor=_CONSIST_SPEC)
def compliant_claim_with_unflagged_contested_item(sidecar, ctx):
    out = []
    notice = sidecar.get("notice") if isinstance(sidecar, dict) else None
    confidence = sidecar.get("confidence") if isinstance(sidecar, dict) else None
    if not isinstance(confidence, dict):
        return out
    contested = confidence.get("contested")
    if not isinstance(contested, list):
        return out
    claims_compliant = isinstance(notice, dict) and notice.get("art13_14_compliant") is True
    for item in contested:
        if not isinstance(item, dict):
            continue  # SCHEMA-1 already reports the type violation
        if item.get("confirm_with_counsel_flag_emitted") is False:
            claim_note = (
                " notice.art13_14_compliant is true, which makes shipping it unflagged "
                "worse"
                if claims_compliant else
                " notice.art13_14_compliant is not claimed true here, but leaving that "
                "field unset is not a way to bypass this check"
            )
            out.append(Finding(
                rule_id="CONSIST-1", category="consistency", severity="rejection",
                entry_type="contested_item", entry_id=item.get("id"),
                message=(f"Contested item {item.get('id')!r} has no [TO CONFIRM WITH "
                          f"COUNSEL] flag emitted.{claim_note} — SKILL.md requires a "
                          "contested position never be smoothed over silently."),
                spec_anchor=_CONSIST_SPEC,
                fix_hint="Render the [TO CONFIRM WITH COUNSEL: ...] flag for this item "
                         "(confirm_with_counsel_flag_emitted=true) before delivering "
                         "the notice as compliant.",
            ))
    return out


@rule(id="AGE-1", severity="rejection", category="consistency",
      description="Every covered jurisdiction (single or multi) must apply its own Art. 8 "
                  "threshold, or the highest applicable threshold when the service cannot "
                  "reliably localise users — never the lowest. A notice that never sets "
                  "localizes_users is treated the same as one that cannot localise "
                  "(conservative default), and a jurisdiction outside this skill's "
                  "age-threshold table is reported, not silently passed.",
      spec_anchor=_AGE_SPEC)
def children_age_threshold_consistency(sidecar, ctx):
    out = []
    notice = sidecar.get("notice") if isinstance(sidecar, dict) else None
    children = sidecar.get("children_data") if isinstance(sidecar, dict) else None
    if not isinstance(notice, dict) or not isinstance(children, dict):
        return out
    if children.get("applicable") is not True:
        return out
    jurisdictions = notice.get("jurisdictions")
    if not isinstance(jurisdictions, list):
        return out

    known = {j: _AGE_THRESHOLDS[j] for j in jurisdictions
             if isinstance(j, str) and j in _AGE_THRESHOLDS}

    # Hole (c): a jurisdiction outside the playbook must not silently pass when
    # children's data is in play — the age threshold for it is simply unverified.
    uncovered = sorted({j for j in jurisdictions
                         if isinstance(j, str) and j not in _AGE_THRESHOLDS})
    for j in uncovered:
        out.append(Finding(
            rule_id="AGE-1", category="consistency", severity="warning",
            field="notice.jurisdictions", entry_id=j,
            message=(f"{j!r} is outside this skill's Art. 8 age-threshold playbook "
                      f"(references/EU_COMMON.md only tabulates {sorted(_AGE_THRESHOLDS)}) "
                      "and children_data.applicable is true for this notice — the age "
                      f"threshold actually applied for {j!r} is unverified against that "
                      "jurisdiction's own Art. 8 implementing law, not checked by this "
                      "rule."),
            spec_anchor=_AGE_SPEC,
            fix_hint=(f"Confirm {j!r}'s Art. 8 threshold with local counsel / the national "
                      "DPA before relying on any value applied for it, or route this "
                      "jurisdiction to counsel per the Step 1 STOP rule for jurisdictions "
                      "outside the loaded playbooks."),
        ))
    if not known:
        return out

    localizes = notice.get("localizes_users")
    # Holes (a)/(b): a single covered jurisdiction, and a notice that never sets
    # localizes_users at all, must still be checked — only an EXPLICIT True switches
    # to the per-market branch below. Treating "unset" as "cannot reliably localise"
    # is the conservative reading: it forces the HIGHEST threshold rather than letting
    # an unanswered question silently default to a lower one.
    if localizes is not True:
        expected = max(known.values())
        applied = children.get("effective_age_applied")
        if isinstance(applied, int) and applied < expected:
            out.append(Finding(
                rule_id="AGE-1", category="consistency", severity="rejection",
                field="children_data.effective_age_applied",
                message=(f"children_data.effective_age_applied={applied} but this notice "
                          f"does not reliably localise users across {jurisdictions} "
                          f"(notice.localizes_users={localizes!r}) — the correct fallback "
                          f"is the HIGHEST applicable Art. 8 threshold ({expected}), never "
                          "a lower one. This is the v1.6 Finding 7 regression this rule "
                          "guards against, and (break-it test 2026-10-02) now also applies "
                          "to a single covered jurisdiction and to an unset "
                          "localizes_users, not only to localizes_users=false with 2+ "
                          "jurisdictions."),
                spec_anchor=_AGE_SPEC,
                fix_hint=f"Set children_data.effective_age_applied to {expected} (or set "
                         "notice.localizes_users=true and supply per-market thresholds).",
            ))
    else:
        used = children.get("jurisdiction_thresholds_used")
        if isinstance(used, dict):
            for j, expected in sorted(known.items()):
                actual = used.get(j)
                if isinstance(actual, int) and actual != expected:
                    out.append(Finding(
                        rule_id="AGE-1", category="consistency", severity="rejection",
                        field=f"children_data.jurisdiction_thresholds_used.{j}",
                        message=(f"jurisdiction_thresholds_used[{j!r}]={actual} but the "
                                  f"correct Art. 8 threshold for {j} is {expected} "
                                  "(references/EU_COMMON.md age-threshold table)."),
                        spec_anchor=_AGE_SPEC,
                        fix_hint=f"Set jurisdiction_thresholds_used['{j}'] to {expected}.",
                    ))
    return out
