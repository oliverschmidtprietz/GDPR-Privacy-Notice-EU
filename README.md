[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-orange)](https://docs.anthropic.com/en/docs/claude-code)

# Privacy Notice EU v1.0

**Pan-EU GDPR Privacy Notice Generator** — a comprehensive drafting skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that produces jurisdiction-aware, GDPR-compliant privacy notices as professional .docx documents.

> **Note:** This is a Claude Code skill, not a standalone application. It requires Claude Code (Anthropic's agentic coding tool) to run. The skill extends Claude's capabilities with specialized GDPR privacy notice drafting knowledge, multi-jurisdiction requirements, and document generation.

## Features

- **Five notice types**: Website/App, Applicant, Employee, Business Partner (B2B), B2C Customer
- **Multi-jurisdiction coverage**: DE (DSGVO+BDSG+TDDDG), FR (RGPD+LIL+LCEN), AT, IT, ES, NL, BE, IE, UK GDPR
- **Multi-language support**: German, French, English — with bilingual and pan-EU options
- **AI Act transparency integration**: Art. 50 AI Act disclosure requirements
- **Type-driven intake**: data categories, legal bases, and retention defaults tailored to each notice type
- **Art. 13/14 compliance verification**: structured checklist before delivery
- **Cookie & tracking section**: with CMP integration guidance
- **Art. 21 objection box**: visually prominent, separate presentation per GDPR requirement
- **DPIA indicator screening**: flags when Art. 35 assessment may be needed
- **Audit-ready .docx output** with professional formatting

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/oliverschmidtprietz/GDPR-Privacy-Notice-EU.git
   ```

2. Copy the skill folder into your Claude Code skills directory:
   ```bash
   cp -r GDPR-Privacy-Notice-EU/ ~/.claude/skills/user/gdpr-privacy-notice-eu-oliver-schmidt-prietz/
   ```

3. The skill will auto-activate when you mention privacy notices, Datenschutzerklaerung, politique de confidentialite, Art. 13/14, or related topics in Claude Code.

## File Structure

```
GDPR-Privacy-Notice-EU/
├── SKILL.md                              # Main skill instructions
├── LICENSE                               # AGPL-3.0
└── references/
    ├── templates.md                      # Document template: structure, formatting, translations
    ├── EU_COMMON.md                      # Pan-EU GDPR requirements (Art. 13/14 checklist, legal bases)
    ├── DE.md                             # Germany-specific requirements (BDSG, TDDDG, DSK guidance)
    ├── FR.md                             # France-specific requirements (CNIL recommendations, LIL, LCEN)
    ├── OTHER_EU.md                       # AT, IT, ES, NL, BE, IE, UK GDPR specifics
    └── NOTICE_TYPES.md                   # Type profiles: section maps, data categories, intake questions
```

## Usage

### Quick Start

Just tell Claude what you need:

> "I need a privacy notice for our SaaS platform. We're a German GmbH based in Berlin,
> targeting customers in Germany and France. We use Google Analytics, Stripe for payments,
> and OpenAI for an AI chatbot feature."

The skill will activate and walk you through the intake process.

### Trigger Phrases

- "Create a privacy notice" / "Datenschutzerklaerung erstellen" / "politique de confidentialite"
- "Privacy policy for our website" / "Art. 13 GDPR"
- "Bewerber-Datenschutz" / "applicant privacy notice"
- "Employee data protection notice" / "Beschaeftigten-Datenschutz"

### Workflow

| Step | Description |
|------|-------------|
| **1. Scope** | Notice type, jurisdiction(s), language, template choice |
| **2. Intake** | Type-driven collection: controller info, data inventory, legal bases, processors, cookies, AI |
| **3. Draft** | Generate notice from template + type profile + collected information |
| **4. Verify** | Art. 13/14 compliance check + type-specific checks + AI Act check |
| **5. Deliver** | Professional .docx output with post-generation checklist |

### Notice Types

| Type | Typical Use Case |
|------|------------------|
| **Website / App** | Visitors, users, subscribers — includes sub-types (brochure, e-commerce, SaaS, mobile, marketplace, AI platform) |
| **Applicant** | Job applicants and candidates |
| **Employee** | Employees, contractors, interns |
| **B2B Partner** | Contact persons at vendors, suppliers, clients |
| **B2C Customer** | End consumers in purchase/service relationships |
| **Combined** | Multiple audiences in one or linked notices |

## Regulatory Basis

| Document | Reference |
|----------|-----------|
| GDPR Articles 13 & 14 | Information duties to data subjects |
| GDPR Article 21(4) | Prominent presentation of right to object |
| GDPR Article 22 | Automated decision-making transparency |
| EU AI Act Article 50 | AI transparency obligations |
| BDSG (Germany) | Sec. 26 employee data, DPO thresholds |
| CNIL Recommendations (France) | 2020 privacy notice guidance |
| TDDDG (Germany) | Telemedien/cookie requirements |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-10 | Initial release: 5 notice types, DE/FR/EU jurisdiction coverage, multi-language support, AI Act integration, type-driven intake, portable docx generation via templates.md |

## License & Disclaimer

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).

This skill provides drafting guidance based on publicly available GDPR regulatory materials. It does not constitute legal advice. All privacy notices should be reviewed by qualified data protection counsel and your organization's DPO before publication.

---

*Created by Oliver Schmidt-Prietz — [OneZero Legal](https://onezerolegal.com)*
