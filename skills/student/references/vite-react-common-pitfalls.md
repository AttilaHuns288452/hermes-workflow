# Common Vite + React Pitfalls (Beginner)

## Image Paths — Local Filesystem Won't Work

```jsx
<!-- ❌ BROWSER CAN'T READ THIS -->
<img src="C:\Users\YOUR_USERNAME\Downloads\photo.jpg" />

<!-- ✅ COPY TO public/ FIRST, THEN: -->
<img src="/photo.jpg" />
```

**Why:** The browser runs in a sandbox — it cannot read arbitrary paths from your hard drive. Vite serves files from `public/` at the root (`/`). Or import them:

```jsx
import profilePic from './assets/profile.jpg'
<img src={profilePic} />
```

## Components — JSX, Never Function Calls

```jsx
// ❌ NO — bypasses React's lifecycle, breaks hooks
import navbar from './navbar'
{navbar()}

// ✅ YES — proper component usage
import Navbar from './navbar'
<Navbar />
```

Components in JSX must be PascalCase and rendered as `<Element />`, not `{fn()}`.

## Layout — Navbar Spans Full Width

```jsx
// ❌ NO — navbar gets centered inside the flexbox with the card
<div className="min-h-screen flex justify-center items-center">
  <Navbar />
  <Card />
</div>

// ✅ YES — flex-col, navbar at top, card centered in remaining space
<div className="min-h-screen bg-gray-100">
  <Navbar />
  <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
    <Card />
  </div>
</div>
```

## Tailwind Gap vs justify-between

- `justify-between` pushes first item to flex-start and last to flex-end. If you have few items, they end up at opposite edges.
- `gap-{n}` spaces adjacent items evenly. Use when you don't need items at the far edges.
- `ml-auto` on the right-side group pushes only that group right, keeping the left group where it is.

## Button vs Anchor

- `<a href="...">` for **navigation** (pages, sections)
- `<button>` for **actions** (login, submit, toggle)
- Don't use `<a>` for actions just because it looks right — keyboard/screen reader behavior differs.
