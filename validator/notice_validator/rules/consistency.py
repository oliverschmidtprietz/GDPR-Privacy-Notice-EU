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
      description="A notice claiming art13_14_compliant=true must not carry a contested "
                  "item with no [TO CONFIRM WITH COUNSEL] flag emitted.",
      spec_anchor=_CONSIST_SPEC)
def compliant_claim_with_unflagged_contested_item(sidecar, ctx):
    out = []
    notice = sidecar.get("notice") if isinstance(sidecar, dict) else None
    confidence = sidecar.get("confidence") if isinstance(sidecar, dict) else None
    if not isinstance(notice, dict) or not isinstance(confidence, dict):
        return out
    if notice.get("art13_14_compliant") is not True:
        return out
    contested = confidence.get("contested")
    if not isinstance(contested, list):
        return out
    for item in contested:
        if not isinstance(item, dict):
            continue  # SCHEMA-1 already reports the type violation
        if item.get("confirm_with_counsel_flag_emitted") is False:
            out.append(Finding(
                rule_id="CONSIST-1", category="consistency", severity="rejection",
                entry_type="contested_item", entry_id=item.get("id"),
                message=(f"notice.art13_14_compliant is true but contested item "
                          f"{item.get('id')!r} has no [TO CONFIRM WITH COUNSEL] flag "
                          "emitted — SKILL.md requires a contested position never be "
                          "smoothed over silently."),
                spec_anchor=_CONSIST_SPEC,
                fix_hint="Either render the [TO CONFIRM WITH COUNSEL: ...] flag for this "
                         "item (confirm_with_counsel_flag_emitted=true), or drop the "
                         "art13_14_compliant claim.",
            ))
    return out


@rule(id="AGE-1", severity="rejection", category="consistency",
      description="Multi-jurisdiction notices must apply each Member State's own Art. 8 "
                  "threshold, or the highest applicable threshold when the service cannot "
                  "reliably localise users — never the lowest.",
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
    if not known:
        return out

    localizes = notice.get("localizes_users")
    if localizes is False and len(jurisdictions) >= 2:
        expected = max(known.values())
        applied = children.get("effective_age_applied")
        if isinstance(applied, int) and applied < expected:
            out.append(Finding(
                rule_id="AGE-1", category="consistency", severity="rejection",
                field="children_data.effective_age_applied",
                message=(f"children_data.effective_age_applied={applied} but this service "
                          f"cannot localise users across {jurisdictions} — the correct "
                          f"fallback is the HIGHEST applicable Art. 8 threshold "
                          f"({expected}), never the lowest. This is the v1.6 Finding 7 "
                          "regression this rule guards against."),
                spec_anchor=_AGE_SPEC,
                fix_hint=f"Set children_data.effective_age_applied to {expected} (or set "
                         "notice.localizes_users=true and supply per-market thresholds).",
            ))
    elif localizes is True:
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
