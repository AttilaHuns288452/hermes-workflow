# Tenor GIF Integration for Quiz Stickers

## Extracting Direct GIF URLs

Given a Tenor embed code:
```html
<div class="tenor-gif-embed" data-postid="10797314150976249328" ...></div>
```

1. Note the `data-postid` value
2. Visit the GIF's view page URL (can extract from the `<a>` href in the embed)
3. Use curl to extract the direct CDN URL:

```bash
curl -sL "https://tenor.com/view/<slug>-gif-<postid>" | grep -oP 'https://media[^\"]*\.gif' | head -1
```

Example output: `https://media.tenor.com/ldfEA4E83fAAAAAC/yao-yi-yao-yao-guang.gif`

## Common Cute Anime GIFs for Quizzes

| GIF ID | URL | Description |
|--------|-----|-------------|
| `10797314150976249328` | `https://media.tenor.com/ldfEA4E83fAAAAAC/yao-yi-yao-yao-guang.gif` | Yao Yi Yao — dancing/shaking anime girl |
| `3689940142159005851` | `https://media.tenor.com/MzVNAlfXiJsAAAAC/1.gif` | Cat dance — cute chibi cat |
| `13611084194942855813` | `https://media.tenor.com/vORI9e-AqoUAAAAC/menhera-chan-chibi.gif` | Menhera Chan — chibi angry anime girl |
| `12448557298959934938` | `https://media.tenor.com/rMIo6HqaZdoAAAAC/honkai-star-rail-anime.gif` | Honkai Star Rail — game sticker |
| `15879740996011221209` | `https://media.tenor.com/3GAsTSh04NkAAAAC/chibi-anime-boy.gif` | Chibi anime boy — cute boy dancing |
| `361787905988688182` | `https://media.tenor.com/BQVULwR8-TYAAAAC/dance-chibi.gif` | Kaoruko — chibi dance character |

## Auto-Cycling Timer Pattern

```tsx
// ⚠️ DO NOT use Math.random() in useState initializer (causes React Error #310)
// Use a fixed initial value; randomize after client mount
const stickerGifs = [ /* 6-10 URLs */ ];
const [currentSticker, setCurrentSticker] = useState(stickerGifs[0]);

// Effect: randomize on mount, then auto-cycle
useEffect(() => {
  const switchSticker = () => {
    const next = Math.floor(Math.random() * stickerGifs.length);
    setCurrentSticker(stickerGifs[next]);
  };
  switchSticker();  // immediate randomize (client-side only, matches server render)
  const interval = setInterval(switchSticker, 4000 + Math.random() * 5000);
  return () => clearInterval(interval);
}, []);
```

## Sticker Display Pattern

Place on both landing page and each question card. Circular container with glow + floating hearts + sparkles:

```tsx
{/* Decorative sparkles around the card */}
<div className="sticker-sparkle text-lg" style={{top: '5%', left: '10%', animationDelay: '0s'}}>✨</div>
<div className="sticker-sparkle text-sm" style={{top: '15%', right: '15%', animationDelay: '0.5s'}}>⭐</div>
<div className="sticker-sparkle text-base" style={{bottom: '20%', left: '8%', animationDelay: '1s'}}>💫</div>
<div className="sticker-sparkle text-lg" style={{bottom: '10%', right: '10%', animationDelay: '1.5s'}}>🌟</div>

{/* Glowing sticker circle */}
<div className="sticker-glow w-40 h-40 rounded-full bg-gradient-to-br from-pink-200 via-purple-200 to-blue-200 flex items-center justify-center relative overflow-hidden">
  <div className="sticker-float text-2xl absolute -top-2 right-1 z-10">💕</div>
  <div className="sticker-float text-xl absolute -top-1 left-2 z-10" style={{ animationDelay: '0.3s' }}>💖</div>
  <img src={currentSticker} alt="Anime sticker" className="w-36 h-36 object-cover rounded-full" style={{ transform: 'scale(1.15)' }} />
</div>
<p className="text-xs text-purple-400 mt-3 sticker-float font-medium">✨ Let's find your perfect match! ✨</p>
```
