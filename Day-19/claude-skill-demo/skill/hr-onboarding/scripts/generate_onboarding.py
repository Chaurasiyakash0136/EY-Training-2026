#!/usr/bin/env python3
"""
HR Onboarding Document Generator
Bundled script for the hr-onboarding Claude skill.

Usage:
    python generate_onboarding.py --name "Jane Doe" --role "Engineer" \
        --department "Engineering" --manager "John Smith" \
        --start-date "July 1, 2026" --salary "18,00,000" \
        --location "Bengaluru (Hybrid)" --company "Acme Technologies"
"""

import argparse
import os
from datetime import datetime, timedelta


def parse_args():
    parser = argparse.ArgumentParser(description="Generate HR onboarding documents")
    parser.add_argument("--name", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--department", default="[FILL IN]")
    parser.add_argument("--manager", default="[FILL IN]")
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--salary", required=True)
    parser.add_argument("--location", default="Office")
    parser.add_argument("--company", default="[FILL IN]")
    parser.add_argument("--output", default="/tmp/onboarding_output/")
    return parser.parse_args()


def get_role_plan(role: str) -> dict:
    role_lower = role.lower()
    if any(k in role_lower for k in ["engineer", "developer", "sde", "software"]):
        return {
            "day30": [
                "Set up local dev environment and toolchain",
                "Complete codebase onboarding walkthrough with buddy",
                "Attend 3 team standups and understand sprint cadence",
                "Ship first small PR (bug fix or documentation update)",
                "Complete all mandatory compliance trainings",
            ],
            "day60": [
                "Own a feature task end-to-end from design to deployment",
                "Participate actively in sprint planning and retrospectives",
                "Conduct 1:1 introductions with all direct teammates",
                "Review and understand CI/CD and release processes",
            ],
            "day90": [
                "Lead at least one sprint task independently",
                "Propose one code quality or process improvement",
                "Present a technical topic in a team knowledge-share",
                "Complete performance baseline check-in with manager",
            ],
        }
    elif any(k in role_lower for k in ["design", "ux", "ui", "product designer"]):
        return {
            "day30": [
                "Access and explore Figma workspace, design system, and component library",
                "Review 3 past shipped product designs for context",
                "Shadow 2 user research sessions or review recordings",
                "Complete first design critique participation",
            ],
            "day60": [
                "Own design for one small feature end-to-end",
                "Present design work in a team review",
                "Contribute one reusable component to the design system",
            ],
            "day90": [
                "Lead design discovery for a medium-complexity feature",
                "Run or co-facilitate one usability test",
                "Present portfolio of first 90-day contributions to team",
            ],
        }
    else:
        return {
            "day30": [
                "Complete all onboarding modules and compliance training",
                "Meet with key stakeholders across departments",
                "Understand team OKRs and how your role contributes",
                "Shadow a colleague for a full working day",
            ],
            "day60": [
                "Take ownership of one ongoing project or workstream",
                "Set up regular 1:1s with direct reports or peers",
                "Contribute meaningfully to one team decision",
            ],
            "day90": [
                "Independently drive one project from start to milestone",
                "Identify and propose one improvement in your area",
                "Complete your first formal performance check-in",
            ],
        }


def get_tools_by_department(department: str) -> list:
    dept_lower = department.lower()
    base_tools = [
        "Google Workspace (Gmail, Calendar, Drive, Docs)",
        "Slack — join #general, #your-team, and #announcements",
        "Zoom — test audio/video before Day 1",
        "Notion / Confluence — company wiki access",
        "HR Portal (BambooHR / Darwinbox) — leave, payroll, documents",
    ]
    if any(k in dept_lower for k in ["engineer", "tech", "product", "devops"]):
        base_tools += [
            "GitHub / GitLab — request repo access from your manager",
            "Jira / Linear — sprint board and ticket tracker",
            "VS Code / JetBrains IDE — license provided via IT",
            "AWS / GCP console — request IAM role from DevOps",
            "Datadog / Sentry — observability dashboards",
        ]
    elif "design" in dept_lower:
        base_tools += [
            "Figma — request team access from Design Lead",
            "Maze / Lyssna — user testing platform",
            "Zeplin — design handoff tool",
        ]
    elif any(k in dept_lower for k in ["sales", "marketing", "growth"]):
        base_tools += [
            "Salesforce / HubSpot CRM",
            "LinkedIn Sales Navigator",
            "Google Analytics 4",
            "Canva Pro — marketing assets",
        ]
    return base_tools


def generate_bundle(args) -> str:
    today = datetime.today().strftime("%B %d, %Y")
    offer_expiry = (datetime.today() + timedelta(days=5)).strftime("%B %d, %Y")
    first_name = args.name.split()[0]
    role_plan = get_role_plan(args.role)
    tools = get_tools_by_department(args.department)

    sections = []

    # ── OFFER LETTER ──────────────────────────────────────────────────────────
    sections.append(f"""## DOCUMENT: Offer Letter
<!-- employee: {args.name} | generated: {today} -->

{args.company}
Date: {today}

Dear {args.name},

We are delighted to extend an offer of employment for the role of **{args.role}**
within our **{args.department}** team at **{args.company}**.

### Terms of Employment

| Detail | Information |
|---|---|
| **Position** | {args.role} |
| **Department** | {args.department} |
| **Reporting To** | {args.manager} |
| **Start Date** | {args.start_date} |
| **Annual CTC** | ₹{args.salary} per annum |
| **Work Location** | {args.location} |
| **Employment Type** | Full-time, Permanent |

### Conditions of Offer

This offer is contingent upon:
- Successful completion of background and reference verification
- Submission of all required documentation before your start date
- Execution of the Employee Confidentiality and IP Agreement

Please sign and return this letter by **{offer_expiry}** to confirm your acceptance.
A copy of this signed offer should be sent to hr@{args.company.lower().replace(' ', '').replace('.', '')[:15]}.com

We are excited about the value you will bring to the team and look forward to
welcoming you aboard.

Warm regards,

{args.manager}
{args.department} Lead, {args.company}
""")

    # ── WELCOME LETTER ────────────────────────────────────────────────────────
    sections.append(f"""## DOCUMENT: Welcome Letter
<!-- employee: {args.name} | generated: {today} -->

Hi {first_name},

Welcome to the team! We're genuinely thrilled to have you joining us as our new
**{args.role}**.

I want you to know that we didn't choose you lightly — you stood out not just for
your skills but for how you think and communicate. I'm excited to see what we'll
build together.

Your first few weeks are all about getting comfortable. Don't worry about knowing
everything immediately — ask questions freely, explore the codebase/tools/processes
at your own pace, and lean on your buddy (who will be introduced on Day 1).

A few things to look forward to:
- A welcome lunch with the team on your first day
- A 1:1 with me at the end of your first week
- Full access to our learning budget from Day 30

We're rooting for you. See you on **{args.start_date}**!

{args.manager}
{args.department}, {args.company}
""")

    # ── DAY 1 CHECKLIST ───────────────────────────────────────────────────────
    sections.append(f"""## DOCUMENT: Day 1 Checklist
<!-- employee: {args.name} | generated: {today} -->

# Your Day 1 at {args.company} — {first_name}'s Checklist

## Before You Arrive
- [ ] Sign and return your offer letter
- [ ] Submit all required documents (see list below)
- [ ] Download Slack on your phone
- [ ] Check your email for IT setup instructions (sent 2 days before start)

## Documents to Bring / Submit
- [ ] Aadhaar Card (original + 2 copies)
- [ ] PAN Card
- [ ] Last 3 months payslips (if applicable)
- [ ] Educational certificates (highest degree)
- [ ] Bank account details (for payroll setup)
- [ ] Passport-size photograph (2 copies)
- [ ] Relieving/experience letter from previous employer

## Morning (10:00 AM)
- [ ] Receive your laptop and access card from IT
- [ ] Complete IT security orientation (30 min)
- [ ] Set up email, Slack, and core tools
- [ ] Get your ID card photo taken at reception

## Afternoon
- [ ] Team introductions lunch with {args.manager} and colleagues
- [ ] Walk-through of office / virtual tour of key Slack channels
- [ ] Access HR portal and complete personal details
- [ ] Review company handbook (link in your email)

## End of Day
- [ ] Confirm your buddy's contact for the first 2 weeks
- [ ] Check your onboarding schedule for the rest of Week 1
- [ ] Message your team on Slack saying hello! 👋

**Your reporting manager**: {args.manager} — reach out anytime on Slack.
""")

    # ── 30-60-90 DAY PLAN ─────────────────────────────────────────────────────
    day30_items = "\n".join(f"- [ ] {item}" for item in role_plan["day30"])
    day60_items = "\n".join(f"- [ ] {item}" for item in role_plan["day60"])
    day90_items = "\n".join(f"- [ ] {item}" for item in role_plan["day90"])

    sections.append(f"""## DOCUMENT: 30-60-90 Day Plan
<!-- employee: {args.name} | generated: {today} -->

# {first_name}'s Ramp-Up Plan — {args.role}

This plan is a guide, not a rigid contract. The goal is to help you find your footing
confidently. Review this with {args.manager} at the end of each phase.

## Days 1–30: Learn & Orient

**Theme**: Understanding before building. Ask all the questions.

{day30_items}

**Success looks like**: You can describe what the team is building, why it matters,
and where you fit in.

---

## Days 31–60: Contribute & Connect

**Theme**: Start shipping and forming relationships.

{day60_items}

**Success looks like**: You've made a visible contribution and feel comfortable
in day-to-day team rhythms.

---

## Days 61–90: Own & Improve

**Theme**: Take initiative. You belong here now.

{day90_items}

**Success looks like**: Your manager trusts you to run with tasks independently,
and the team feels the impact of you being here.
""")

    # ── IT & TOOLS SETUP ──────────────────────────────────────────────────────
    tools_list = "\n".join(f"- [ ] {tool}" for tool in tools)

    sections.append(f"""## DOCUMENT: IT & Tools Setup Guide
<!-- employee: {args.name} | generated: {today} -->

# IT & Tools Setup — {first_name}

Your IT onboarding checklist. Complete as many as possible on Day 1; IT support
will help with the rest.

## Accounts to Set Up

{tools_list}

## Security Essentials (mandatory Day 1)
- [ ] Enable 2FA on your company Google account
- [ ] Install company-approved password manager (1Password/Bitwarden)
- [ ] Complete mandatory security awareness training (30 min, link in email)
- [ ] Do NOT install unapproved software — raise a ticket via IT portal if needed

## Getting Help
- **Slack**: #it-support for general issues
- **Email**: it-helpdesk@{args.company.lower().replace(' ', '')[:10]}.com
- **Response time**: Critical issues — 2 hours; General — next business day
""")

    # ── COMPANY POLICY SUMMARY ────────────────────────────────────────────────
    sections.append(f"""## DOCUMENT: Company Policy Summary
<!-- employee: {args.name} | generated: {today} -->

# Company Policy Highlights — {args.company}

*This is a summary. Full policy document is in the HR portal.*

## Leave Policy
| Leave Type | Days/Year | Notes |
|---|---|---|
| Earned Leave | 15 days | Accrues monthly; carry-forward up to 15 days |
| Sick Leave | 12 days | No carry-forward; doctor's note needed for 3+ days |
| Casual Leave | 6 days | Max 3 consecutive days |
| Public Holidays | ~12 days | As per Karnataka state calendar |
| Maternity / Paternity | 26 weeks / 5 days | As per statutory guidelines |

## Work Hours & Hybrid Policy
- Core hours: **10 AM – 4 PM IST** (all meetings scheduled within this window)
- Work-from-home: **2 days/week** standard; team-specific variations apply
- Overtime is not expected; if project demands it, comp-off is provided

## Code of Conduct (Key Points)
- Treat all colleagues, vendors, and customers with respect
- Raise concerns via your manager or anonymously via the Ethics Hotline
- Zero tolerance for discrimination, harassment, or data misuse
- All company data is confidential — do not share externally without approval

## Learning & Development
- Annual L&D budget: ₹25,000 (books, courses, conferences)
- Available from Day 30 — request via HR portal
- Internal monthly knowledge-share: join #learning on Slack

## Probation & Performance
- Probation period: 6 months
- Mid-probation check-in at 3 months with {args.manager}
- Performance reviews: Bi-annual (April & October)

---
*For full policy details, visit the HR Portal. Questions? hr@{args.company.lower().replace(' ', '')[:10]}.com*
""")

    # Assemble full bundle
    bundle = f"""# Onboarding Bundle — {args.name}
**Role**: {args.role} | **Department**: {args.department}
**Company**: {args.company} | **Start Date**: {args.start_date}
**Generated**: {today}

> This bundle contains {len(sections)} documents. Each section is separated by `---`.
> Ask Claude to export any section as a Word document or PDF.

---

"""
    bundle += "\n\n---\n\n".join(sections)
    return bundle


def main():
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)

    print(f"Generating onboarding bundle for {args.name}...")
    bundle = generate_bundle(args)

    filename = f"onboarding_{args.name.replace(' ', '_').lower()}.md"
    output_path = os.path.join(args.output, filename)

    with open(output_path, "w") as f:
        f.write(bundle)

    print(f"✅ Onboarding bundle saved to: {output_path}")
    print(f"   Documents included: Offer Letter, Welcome Letter, Day 1 Checklist,")
    print(f"   30-60-90 Day Plan, IT & Tools Guide, Company Policy Summary")
    return output_path


if __name__ == "__main__":
    main()
