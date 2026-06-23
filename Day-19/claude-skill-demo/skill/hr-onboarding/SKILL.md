---
name: hr-onboarding
description: >
  Use this skill whenever someone needs to generate HR onboarding documents,
  employee welcome kits, offer letters, onboarding checklists, orientation
  schedules, or any new-hire paperwork. Trigger when the user mentions
  "onboarding", "new hire", "offer letter", "welcome kit", "joining formalities",
  "employee induction", "first day documents", or wants to automate HR document
  generation for a new employee. Also trigger when someone says things like
  "set up documents for our new developer" or "prepare joining pack for candidate".
  Works for startups, enterprises, IT companies, and any business hiring staff.
---

# HR Onboarding Document Generator

This skill automates the generation of a complete, professional new-hire onboarding
package. It produces consistent, branded documents that HR teams can hand off directly
to new employees — saving hours of manual drafting per hire.

## What This Skill Produces

For each new hire, generate a **complete onboarding bundle** containing:

1. **Offer Letter** — formal employment offer with compensation, role, and start date
2. **Welcome Letter** — warm personal letter from the manager/CEO
3. **Day 1 Checklist** — what to bring, who to meet, what to set up
4. **30-60-90 Day Plan** — structured ramp-up goals by role type
5. **IT & Tools Setup Guide** — accounts, access, software to install
6. **Company Policy Summary** — leave, WFH, code of conduct highlights

## Required Inputs

Ask the user for these before generating (or infer from context):

| Field | Example |
|---|---|
| Employee Name | Priya Sharma |
| Role / Job Title | Senior Software Engineer |
| Department | Engineering |
| Manager Name | Rahul Mehta |
| Start Date | July 1, 2026 |
| Salary / CTC | ₹18,00,000 per annum |
| Location | Bengaluru (Hybrid) |
| Company Name | Acme Technologies Pvt. Ltd. |

If any field is missing, make reasonable placeholders and note them with `[FILL IN]`.

## Generation Workflow

### Step 1 — Gather inputs
Extract employee details from the conversation or uploaded file. If key fields
are missing, ask for them in a single grouped question (not one at a time).

### Step 2 — Generate documents
Use `scripts/generate_onboarding.py` to produce a structured Markdown bundle.
Each document section is clearly delimited so it can be split into individual files.

```bash
python scripts/generate_onboarding.py \
  --name "Priya Sharma" \
  --role "Senior Software Engineer" \
  --department "Engineering" \
  --manager "Rahul Mehta" \
  --start-date "July 1, 2026" \
  --salary "18,00,000" \
  --location "Bengaluru (Hybrid)" \
  --company "Acme Technologies Pvt. Ltd." \
  --output /tmp/onboarding_priya_sharma/
```

### Step 3 — Review and present
- Show the user a summary of what was generated
- Offer to tweak tone (formal/warm), add company-specific policies, or export to DOCX/PDF
- If the user wants Word format, refer to the `docx` skill

### Step 4 — Offer follow-ups
After generation, suggest:
- "Want me to email this to the employee directly?"
- "Should I add a custom 30-60-90 day plan for this specific role?"
- "Want me to generate for multiple hires from a CSV?"

## Document Templates

### Offer Letter Template
```
[COMPANY LETTERHEAD]
Date: {date}

Dear {name},

We are delighted to offer you the position of {role} at {company}.

COMPENSATION & BENEFITS
- Annual CTC: {salary}
- Work Location: {location}
- Start Date: {start_date}

This offer is contingent upon successful completion of background verification.
Please sign and return by {offer_expiry}.

Warm regards,
{manager}
{company}
```

### 30-60-90 Day Plan (Engineering Roles)
- **Days 1–30**: Environment setup, codebase walkthrough, shadow team standup, ship first small PR
- **Days 31–60**: Own a feature end-to-end, participate in sprint planning, 1:1 with all team members
- **Days 61–90**: Lead a sprint task independently, propose one process/code improvement

For non-engineering roles, load the appropriate template from `references/role-plans.md`.

## Tone Guidelines

- Offer letters: **formal and precise** — use full legal name, exact figures
- Welcome letters: **warm and human** — use first name, express genuine excitement
- Checklists: **clear and scannable** — bullet points, no jargon
- Policy summaries: **plain English** — avoid HR legalese where possible

## Output Format

Always produce output as a **single Markdown file** with clear `---` section dividers,
so it can be previewed in chat AND easily split into individual documents later.

Each section starts with:
```
## DOCUMENT: [Document Name]
<!-- employee: {name} | generated: {date} -->
```

## Industry Context

This skill is designed for the **HR Tech / People Ops** industry. Companies using this skill:
- Startups scaling from 10 → 100 employees where HR bandwidth is limited
- Mid-size IT companies (common in Bengaluru, Hyderabad, Pune) with high hiring velocity
- HR SaaS platforms building automated onboarding flows for their customers

Typical time saved: **2–4 hours per hire** in document drafting and formatting.

## Error Handling

If the script fails, fall back to generating the bundle directly in Markdown in the
conversation. The templates in this SKILL.md are sufficient to produce a complete
output without the script.
