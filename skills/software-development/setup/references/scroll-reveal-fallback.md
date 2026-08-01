# Scroll-Reveal Fallback Pattern

Scroll-triggered reveal animations commonly break on production static sites because:

1. The IntersectionObserver callback never fires (hydration timing, CSS not loaded, or the element is considered 0-height).
2. The pre-rendered HTML contains content but the CSS starts it at `opacity: 0` and no JS adds `.visible`.
3. CDN/GitHub Pages caches an old build where the JS asset 404s, leaving the DOM but no reveal logic.

## Safe pattern

Make the content visible by default, then enhance with animation only when the observer is confirmed to run.

```css
.reveal {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: no-preference) {
  .reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity .7s, transform .7s;
  }
  .reveal.visible {
    opacity: 1;
    transform: translateY(0);
  }
}
```

```js
function useReveal() {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          obs.unobserve(entry.target);
        }
      },
      { threshold: 0.1 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);
  return ref;
}
```

With the CSS above, if the JS fails, the content is still readable. If the JS runs, the animation plays.

## Production check

Verify with a headless browser on the live URL (not just localhost):

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.goto('https://<user>.github.io/<repo>/')
    page.wait_for_timeout(3000)
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    page.wait_for_timeout(1000)
    reveals = page.query_selector_all('.reveal')
    visible = sum(1 for r in reveals if 'visible' in (r.evaluate('el => el.className') or ''))
    print(f'{visible}/{len(reveals)} .reveal elements have .visible')
    browser.close()
```

If the ratio is low, the reveal trigger is broken. Fall back to the CSS above.
