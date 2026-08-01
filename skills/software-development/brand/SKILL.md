---
name: brand
description: "Brand voice, visual identity, messaging frameworks, asset management, brand consistency. Use for brand voice, tone of voice, marketing assets, brand compliance, style guides."
---

# Brand

Brand identity, voice, messaging, asset management, and consistency frameworks.

## When to Use

- Brand voice definition and content tone guidance
- Visual identity standards and style guide development
- Messaging framework creation
- Brand consistency review and audit
- Asset organization, naming, and approval
- Color palette management and typography specs

## Quick Start

```bash
# Inject brand context
node scripts/inject-brand-context.cjs
node scripts/inject-brand-context.cjs --json

# Validate an asset
node scripts/validate-asset.cjs <asset-path>

# Extract/compare colors
node scripts/extract-colors.cjs --palette
node scripts/extract-colors.cjs <image-path>
```

## Brand Sync Workflow

```bash
# 1. Edit brand guidelines
# 2. Sync to design tokens
node scripts/sync-brand-to-tokens.cjs
# 3. Verify
node scripts/inject-brand-context.cjs --json | head -20
```

## References

| Topic | File |
|-------|------|
| Voice Framework | `references/voice-framework.md` |
| Visual Identity | `references/visual-identity.md` |
| Messaging | `references/messaging-framework.md` |
| Consistency | `references/consistency-checklist.md` |
| Guidelines Template | `references/brand-guideline-template.md` |
| Asset Organization | `references/asset-organization.md` |
| Color Management | `references/color-palette-management.md` |
| Typography | `references/typography-specifications.md` |
| Logo Usage | `references/logo-usage-rules.md` |
| Approval Checklist | `references/approval-checklist.md` |
