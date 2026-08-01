# Multi-Perspective Review Protocol

After every milestone (v1, v2, etc.), critique the current build from five distinct user perspectives, then use that critique to revise the backlog for the next milestone.

## How To Run

For the current state of the app, write a genuine critique from each persona. Don't soften critiques to protect prior decisions — if a persona would be frustrated, say so plainly.

## The Five Personas

### 1. Everyday Normal User (no financial background)
- Would they understand the interface without explanation?
- Is quick-add actually fast (2-3 actions, not a form)?
- Do words like "entity," "liquid/illiquid," "balance sheet" confuse or intimidate?
- Would they come back tomorrow, or does it feel like work?

### 2. Finance-Minded Power User (investor mentality)
- Can they see net worth TREND over time, not just a snapshot?
- Can they see cash flow rate — compounding vs. bleeding — not just totals?
- Do assets break down meaningfully (cash vs. equities vs. crypto vs. property)?
- Would they trust this over a spreadsheet? Why or why not?

### 3. Business Owner/Manager
- Can they answer "am I profitable this month" in one glance?
- Is the staff-approval flow fast enough for daily use?
- Do they trust the inventory numbers without manually recounting stock?
- What decision could they NOT make with the data currently shown?

### 4. Staff/Employee
- Is submitting an expense genuinely simple, or a multi-step form?
- Do they get clear, fast feedback on approval/rejection status?
- Do they see only what they're supposed to see?
- Would they actually use this daily, or find workarounds?

### 5. Accountant
- Do categories map cleanly to standard accounting categories?
- Does the balance sheet actually balance (assets = liabilities + equity)?
- Is there a real audit trail for every edit and delete?
- Could this data be exported and handed to a real accountant?

## Output Format
1. Five short critiques (specific complaints, not vague sentiment)
2. Prioritized change list: per-item persona, impact, effort
3. Flag items requiring schema changes if deferred (these get priority)
4. Note what's NOT being changed and why

## Rules
- Not every critique needs to become a change — flag intentionally skipped items
- Don't let this turn into scope expansion — sharpen existing plans, don't add new categories
- If a critique surfaces something off-roadmap, flag separately as "possible future consideration"

## Session Evidence: CashFlow OS v1
10 issues found, 8 fixed. Skipped: business mode (needs staff/inventory first), AI (garbage-in-garbage-out until data stable), forecasting (dangerous without backtesting).
