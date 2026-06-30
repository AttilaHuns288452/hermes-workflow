# Content Visibility UX — Diagnosing & Fixing Buried Content on Tool Sites

## Problem

Tool/calculator sites routinely bury blog posts, guides, and CTAs below the fold — behind collapsed `<details>` elements, feedback forms, or affiliate link sections. The user complained: *"why are the tools below they would barely see that"* — meaning visitors never scroll far enough to see the resource library.

## Diagnosis via Browser Snapshot

Use `browser_navigate` to the live site, then inspect the snapshot for **DOM order**. Key indicators of buried content:

| Snapshot Signal | What It Means | Severity |
|----------------|--------------|----------|
| Blog cards listed after `DisclosureTriangle` keywords | Users never see guides | 🔴 Critical |
| Affiliate link elements inside a results section | Distraction from core value | 🔴 Critical |
| Feedback form before blog section | Survey fatigue before content delivery | 🟠 High |
| Blog section after multiple `details` or `group` nodes | Content was an afterthought | 🟠 High |
| Only one "Sponsored" divider between tool and blog | Better but still buried | 🟡 Medium |

## The Fix: Section Priority Reordering

### Goal Layout (good visibility)

```
Hero → Calculator → Blog cards → Methodology (visible) → Value-add section → FAQ → CTA
```

### Avoid Layout (buried)

```
Hero → Calculator → [collapsed <details>] → [collapsed FAQ] → Feedback form → Affiliate links → Blog cards
```

## Code Patterns

### 1. Visible Sections Instead of `<details>`

```tsx
// ❌ Bad — content hidden
<details className="bg-white rounded-xl ...">
  <summary className="cursor-pointer font-medium">How this calculation works</summary>
  <div className="mt-4 space-y-3 text-sm text-gray-600">
    <p><strong>Formula:</strong> ...</p>
  </div>
</details>

// ✅ Good — permanently visible card grid
<section className="bg-gradient-to-b from-gray-50 to-white py-12 border-t border-gray-100">
  <div className="max-w-4xl mx-auto px-4">
    <h2 className="text-2xl md:text-3xl font-bold text-gray-900">How This Calculation Works</h2>
    <div className="grid gap-4 md:grid-cols-2">
      {steps.map(step => (
        <div key={step.num} className="flex gap-4 p-4 bg-white rounded-xl border hover:shadow-md transition-shadow">
          <div className={`w-10 h-10 ${step.color} text-white rounded-lg flex items-center justify-center font-bold text-sm`}>
            {step.num}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">{step.title}</h3>
            <p className="text-xs text-gray-500 mt-1">{step.description}</p>
          </div>
        </div>
      ))}
    </div>
  </div>
</section>
```

### 2. Remove Affiliate Links and Feedback from Calculator Output

```tsx
// ❌ Bad — inside calculator results
{results && (
  <>
    <ResultCard />
    <AffiliateLinks />        {/* REMOVE — sponsored links in results section */}
    <FeedbackForm />           {/* REMOVE — survey before content */}
    <AdSense />                {/* OK — non-interactive ad only */}
  </>
)}

// ✅ Good — clean calculator
{results && (
  <>
    <ResultCard />
    <AdSense />
  </>
)}
```

Move affiliate links to a dedicated `/resources` page with proper above-the-fold affiliate disclosure. Move feedback to `/contact` page as an email contact.

### 3. Section IDs for Scroll Navigation

```tsx
<section id="calculator">
  <RateCalculator />
</section>
<section id="guides">
  <BlogCards posts={BLOG_POSTS} />
</section>
<section id="how-it-works">
  <Methodology steps={METHODOLOGY_STEPS} />
</section>
<section id="faq">
  <FAQs items={FAQS} />
</section>

<!-- In CTA section at bottom of page -->
<a href="#calculator" className="...">↑ Back to Calculator</a>
```

### 4. Sticky Header

```tsx
<header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
  <nav className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
    <a href="/" className="flex items-center gap-2 text-gray-900 font-semibold text-sm">
      <span className="flex items-center justify-center w-7 h-7 bg-blue-600 text-white rounded-lg text-xs font-bold">FC</span>
      <span className="hidden sm:inline">Freelance Calculator</span>
    </a>
    <div className="flex items-center gap-1 text-sm">
      <a href="/" className="px-3 py-1.5 text-gray-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg">Calculator</a>
      <a href="/blog" className="px-3 py-1.5 text-gray-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg">Blog</a>
      <a href="/resources" className="px-3 py-1.5 text-gray-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg">Resources</a>
      <a href="/about" className="px-3 py-1.5 text-gray-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg">About</a>
    </div>
  </nav>
</header>
```

### 5. Hero with Trust Badges

```tsx
<header className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-900 text-white relative overflow-hidden">
  <div className="max-w-4xl mx-auto px-4 py-10 md:py-14">
    <h1 className="text-3xl md:text-5xl font-bold">
      Design Your Ideal<br />
      <span className="text-blue-200">Freelance Life</span>
    </h1>
    <p className="mt-3 text-white/80 max-w-2xl">
      Tell us the life you want — and we'll tell you <strong className="text-white">exactly what to charge</strong>.
    </p>
    <div className="mt-5 flex flex-wrap gap-3 text-xs text-white/60">
      <span>✅ 100% free</span>
      <span>🔒 No signup needed</span>
      <span>📊 Updated for 2026</span>
    </div>
  </div>
</header>
```

## Verification Checklist

- [ ] Browser snapshot: blog section appears BEFORE `details`, `DisclosureTriangle`, or feedback form elements
- [ ] No affiliate/Sponsored links inside calculator or form output area
- [ ] No feedback form between tool results and content section
- [ ] Every major section has an `id` attribute
- [ ] Bottom-of-page CTAs use `href="#section-id"` (not `#top`)
- [ ] Sticky nav header present on pages longer than 1 viewport
- [ ] Build passes with no `<script>`-in-JSX errors
- [ ] Scroll-to-section links work from bottom CTA

## Real-World Example: freelancecalculator.xyz

The original layout was:
```
Hero → Calculator → [affiliate links] → [feedback form] → [collapsed methodology] → [collapsed FAQ] → Blog cards
```

Fixed to:
```
Hero → Calculator (clean, no affiliates/feedback) → Blog cards (visible!) → Methodology (visible 8-step grid) → Undercharge explainer (dark card) → FAQ (accordion) → CTA (#calculator scroll)
```

Result: blog cards went from last to second position in the DOM, sticky nav added, all sections got IDs, hero got trust badges.
