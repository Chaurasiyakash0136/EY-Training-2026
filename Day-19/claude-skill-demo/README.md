# Claude Skill Demo — HR Onboarding

A working demo of a Claude `SKILL.md` file applied to the **HR Tech** industry.

## What's in this repo

```
skill/hr-onboarding/
├── SKILL.md                      ← The skill Claude reads
├── scripts/
│   └── generate_onboarding.py   ← Bundled document generator
└── references/
    └── role-plans.md             ← 30-60-90 day plans by role type

demo/
└── onboarding_arjun_verma.md    ← Live generated output example
```

## What is a SKILL.md?

A `SKILL.md` is an instruction file that teaches Claude how to do a specific repeatable task. Claude automatically detects and uses it when your request matches the skill's description.

```
Your request → Claude scans available skills → Finds matching SKILL.md → Follows instructions → Consistent output
```

## Industry: HR Tech

Every company that hires needs onboarding documents. HR teams spend **2–4 hours per new hire** drafting offer letters, welcome kits, checklists, and plans manually. This skill automates all of it.

**This skill generates 6 documents per hire:**
- Offer Letter
- Welcome Letter
- Day 1 Checklist
- 30-60-90 Day Plan (role-specific)
- IT & Tools Setup Guide
- Company Policy Summary

## Run the demo

```bash
python skill/hr-onboarding/scripts/generate_onboarding.py \
  --name "Your Employee" \
  --role "Software Engineer" \
  --department "Engineering" \
  --manager "Their Manager" \
  --start-date "August 1, 2026" \
  --salary "18,00,000" \
  --location "Bengaluru (Hybrid)" \
  --company "Your Company Pvt. Ltd." \
  --output ./output/
```

See `demo/onboarding_arjun_verma.md` for a real generated example.

## How to install in Claude

Copy the skill folder into your Claude skills directory:

```bash
cp -r skill/hr-onboarding/ ~/.claude/skills/hr-onboarding/
```

Then just describe your need naturally in Claude:
> *"Generate onboarding documents for Priya joining as Data Engineer on July 15"*
