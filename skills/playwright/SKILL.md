---
name: "playwright"
description: "Use when the task requires automating a real browser from the terminal (navigation, form filling, snapshots, screenshots, data extraction, UI-flow debugging) via `playwright-cli` or the bundled wrapper script."
---


# Playwright

Cross-browser automation and testing framework. Installed globally (v1.61.1) with Chromium. Use the standard `npx playwright` CLI, not `@playwright/cli`.

## Quick Start

```bash
npx playwright test              # run all tests
npx playwright test --ui         # interactive UI mode
npx playwright show-report       # view last report
npx playwright codegen           # record browser interactions
```

## Scripting (no test runner)

```javascript
import { chromium } from 'playwright';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto('https://example.com');
console.log(await page.title());
await browser.close();
```

## Key Locators

```javascript
page.getByRole('button', { name: 'Submit' })
page.getByText('Welcome')
page.getByPlaceholder('Email')
page.getByTestId('login-form')
page.locator('.card h2')
```

## Common Interactions

```javascript
await page.click('button');
await page.fill('input#email', 'user@example.com');
await page.selectOption('select#country', 'US');
await page.keyboard.press('Enter');
await page.screenshot({ path: 'shot.png' });
await page.pdf({ path: 'page.pdf' });
```

## Assertions

```javascript
await expect(page).toHaveURL(/checkout/);
await expect(page.getByText('Success')).toBeVisible();
await expect(page.locator('.error')).toHaveCount(0);
```

## Project Setup

```bash
npm init playwright@latest
# Creates: playwright.config.js, tests/, package.json
```

## Guardrails

- Prefer `getByRole` / `getByTestId` over CSS selectors — fewer false positives on DOM changes.
- Always `page.waitForLoadState('networkidle')` after navigation in scripts.
- Close browser or context after script runs (`await browser.close()`).
- When debugging: `npx playwright test --debug` or use `--headed` with `page.pause()`.
