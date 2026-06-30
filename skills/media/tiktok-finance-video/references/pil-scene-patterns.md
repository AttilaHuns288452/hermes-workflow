# PIL Scene Patterns for Finance Videos

## Setup
```python
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1080, 1920  # TikTok vertical

def get_font(size):
    for fp in ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]:
        if os.path.exists(fp): return ImageFont.truetype(fp, size)
    return ImageFont.load_default()

def get_bold_font(size):
    for fp in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(fp): return ImageFont.truetype(fp, size)
    return ImageFont.load_default()
```

## Gradient Background
```python
def gradient_bg(ct, cb):
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        r = int(ct[0] + (cb[0]-ct[0])*y/H)
        g = int(ct[1] + (cb[1]-ct[1])*y/H)
        b = int(ct[2] + (cb[2]-ct[2])*y/H)
        d.line([(0,y),(W,y)], fill=(r,g,b))
    return img
```

## Center Text
```python
def center_text(draw, y, text, font, fill=(255,255,255)):
    bb = draw.textbbox((0,y), text, font=font)
    draw.text(((W-(bb[2]-bb[0]))//2, y), text, font=font, fill=fill)
```

## Rounded Rectangle
```python
def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0+radius, y0, x1-radius, y1], fill=fill)
    draw.rectangle([x0, y0+radius, x1, y1-radius], fill=fill)
    draw.pieslice([x0, y0, x0+2*radius, y0+2*radius], 180, 270, fill=fill)
    draw.pieslice([x1-2*radius, y0, x1, y0+2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1-2*radius, x0+2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1-2*radius, y1-2*radius, x1, y1], 0, 90, fill=fill)
```

## Line Chart
```python
def draw_chart(draw, x, y, w, h, vals, color):
    GRAY = (140,140,150)
    draw.line([(x,y),(x,y+h)],fill=GRAY,width=2)
    draw.line([(x,y+h),(x+w,y+h)],fill=GRAY,width=2)
    if len(vals)>1:
        pts=[]
        mn,mx=min(vals),max(vals)
        rng = mx-mn if mx!=mn else 1
        for i,v in enumerate(vals):
            px=x+i*w//(len(vals)-1)
            py=y+h-int((v-mn)/rng*h)
            pts.append((px,py))
        for i in range(len(pts)-1): draw.line([pts[i],pts[i+1]],fill=color,width=4)
        for p in pts: draw.ellipse([p[0]-5,p[1]-5,p[0]+5,p[1]+5],fill=color)
```

## Comparison Bars
```python
def draw_comparison_bar(draw, y, label1, val1, label2, val2, color1, color2):
    bar_h = 40
    max_val = max(val1, val2)
    bar1_w = int(val1 / max_val * 350)
    bar2_w = int(val2 / max_val * 350)
    draw.text((50, y-5), label1, font=get_font(22), fill=(255,255,255))
    draw_rounded_rect(draw, [50, y+25, 50+bar1_w, y+25+bar_h], 8, color1)
    draw.text((60+bar1_w, y+30), f"${val1}K", font=get_font(20), fill=(255,255,255))
    draw.text((50, y+85), label2, font=get_font(22), fill=(255,255,255))
    draw_rounded_rect(draw, [50, y+115, 50+bar2_w, y+115+bar_h], 8, color2)
    draw.text((60+bar2_w, y+120), f"${val2}K", font=get_font(20), fill=(255,255,255))
```

## Grid Overlay
```python
def draw_grid(draw, color=(45,45,55)):
    for x in range(0,W,60): draw.line([(x,0),(x,H)],fill=color,width=1)
    for y in range(0,H,60): draw.line([(0,y),(W,y)],fill=color,width=1)
```

## Character Silhouette
```python
def draw_character(draw, cx, cy, color, label):
    # Head
    draw.ellipse([cx-40, cy-100, cx+40, cy+20], fill=color)
    # Body
    draw.rectangle([cx-30, cy+20, cx+30, cy+120], fill=color)
    # Label below
    bb = draw.textbbox((0,0), label, font=get_font(24))
    tw = bb[2]-bb[0]
    draw.text((cx-tw//2, cy+140), label, font=get_font(24), fill=(255,255,255))
```

## KPI Dashboard Card
```python
def draw_stat_card(draw, x, y, label, value, color):
    draw.rectangle([x, y, x+940, y+100], fill=(35, 40, 55))
    draw.text((x+30, y+10), label, font=get_font(28), fill=(140,140,150))
    draw.text((x+30, y+50), value, font=get_bold_font(42), fill=color)
```

## Color Palette Reference
```python
BLUE = (122, 165, 255)    # Saver / neutral
RED = (255, 158, 158)     # Spender / warning
GREEN = (92, 202, 140)    # Growth / success
YELLOW = (255, 215, 100)  # Accent / VS divider
ORANGE = (255, 165, 100)  # Old age / conclusion
WHITE = (255, 255, 255)
GRAY = (140, 140, 150)
LIGHT_GRAY = (200, 200, 210)
DARK_BG = (26, 27, 38)
```

## Common Pitfalls
1. `draw.textbbox()` works, `image.textbbox()` does NOT
2. `d.text((x,y), "text", font=..., fill=...)` — fill is positional, not keyword after font
3. Use `font=get_font(size)` not `ImageFont.truetype()` directly in every call
4. For emoji in text, use simple text labels instead (PIL default font lacks emoji)
5. Save as PNG for quality, only convert to JPG for thumbnail
