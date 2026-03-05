[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Agent Skill](https://img.shields.io/badge/Agent_Skill-Open_Standard-orange)](https://agentskills.io)

# Privacy Notice EU v1.0

**Pan-EU GDPR Privacy Notice Generator** — an [Agent Skill](https://agentskills.io) that produces jurisdiction-aware, GDPR-compliant privacy notices as professional .docx documents.

> **Note:** This is an [Agent Skill](https://agentskills.io) — not a standalone application. It runs inside any compatible AI agent, including Claude Code, Claude.ai, Cursor, VS Code, GitHub Copilot, Gemini CLI, OpenAI Codex, JetBrains Junie, and [many more](https://agentskills.io). The skill extends your agent's capabilities with specialized GDPR privacy notice drafting knowledge, multi-jurisdiction requirements, and document generation.

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

This is an [Agent Skill](https://agentskills.io) compatible with any tool that supports the open Agent Skills standard.

### Claude Code

```bash
git clone https://github.com/oliverschmidtprietz/GDPR-Privacy-Notice-EU.git
cp -r GDPR-Privacy-Notice-EU/ ~/.claude/skills/user/gdpr-privacy-notice-eu-oliver-schmidt-prietz/
```

The skill will auto-activate when you mention privacy notices, Datenschutzerklaerung, politique de confidentialite, Art. 13/14, or related topics.

### Other Compatible Agents

For Cursor, VS Code, Gemini CLI, OpenAI Codex, JetBrains Junie, and other tools supporting the Agent Skills standard, follow the skill installation instructions for your specific tool. The skill folder structure is portable — just point your agent to the cloned directory.

See [agentskills.io](https://agentskills.io) for a full list of compatible tools and integration guides.

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
