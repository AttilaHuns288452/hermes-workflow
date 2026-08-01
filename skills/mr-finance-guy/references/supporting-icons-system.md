# Supporting Icons System for Mr. Finance Guy Videos

This reference documents the PIL-based icon drawing system used in v9+ videos.
Every scene MUST have supporting icons under each card and a concept box.

## Icon Types & Usage

| Icon Type | Shape | Color | Used For |
|-----------|-------|-------|----------|
| `bank` | Building with pillars | Black outline | Saving, bank accounts, deposits |
| `chart_up` | Bar chart with up arrow | Black | Growth, investments, stocks up |
| `coin` | Stack of 3 coins (gold center) | Gold #D4AF37 | Money, cash, savings |
| `piggy` | Circle + snout + ear | Black outline | Saving, emergency fund (metaphor) |
| `star` | 5-pointed star | Gold filled | Success, goals, good outcomes |
| `growth` | Arrow up + dollar sign | Green #33BB77 | Investing growth, returns |
| `shield` | Shield shape | Blue #007BFF border | Protection, security, safety net |
| `calendar` | Calendar with date number | Black outline | Time, years, months, duration |
| `clock` | Round clock with hands | Black outline | Time, speed, hours |
| `question` | Question mark text | Blue #007BFF | Hook scene, unknown, curiosity |

## How to Use

Import and call `draw_icon(draw, cx, cy, icon_type, size=55)` where:
- `draw` = PIL ImageDraw.Draw object
- `cx, cy` = center coordinates for the icon
- `icon_type` = string from the table above
- `size` = diameter in pixels (default 55 for under-card, 50 for concept box)

## Complete draw_icon() Function

Copy this verbatim into your render script:

```python
def draw_icon(draw, cx, cy, icon_type, size=60):
    """Draw a simple icon/symbol at (cx, cy) center."""
    s = size // 2
    
    if icon_type == "bank":
        # Building shape
        draw.rectangle([cx-s, cy-s+10, cx+s, cy+s], outline=BLACK, width=4)
        draw.rectangle([cx-s+5, cy-s+10, cx+s-5, cy-10], fill=BLACK)
        draw.rectangle([cx-8, cy-8, cx+8, cy+10], fill=BLACK)
        draw.rectangle([cx-6, cy-4, cx+6, cy+s], fill=BG, outline=BLACK, width=2)
        draw.rectangle([cx-s+2, cy-s+10, cx-s+8, cy+s], fill=BG, outline=BLACK, width=2)
        draw.rectangle([cx+s-8, cy-s+10, cx+s-2, cy+s], fill=BG, outline=BLACK, width=2)
        
    elif icon_type == "chart_up":
        draw.line([cx-s, cy+s, cx-s, cy+s-5, cx-s+20, cy+s-25, cx-s+10, cy+s-35, cx, cy+s-50, cx+s-10, cy+s-30, cx+s, cy+s-45, cx+s, cy+s], fill=BLACK, width=5)
        draw.line([cx-s, cy+s, cx+s, cy+s], fill=BLACK, width=3)
        
    elif icon_type == "coin":
        for i in range(3):
            y_offset = cy - s + i * 15
            draw.ellipse([cx-12, y_offset-8, cx+12, y_offset+8], outline=BLACK, width=3, fill=GOLD if i == 1 else BG)
        bbox = draw.textbbox((0, 0), "$", font=ImageFont.truetype(FONT_BOLD, 18))
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((cx - tw//2, cy - s + 15 - th//2), "$", fill=BLACK, font=ImageFont.truetype(FONT_BOLD, 18))
        
    elif icon_type == "piggy":
        draw.ellipse([cx-20, cy-15, cx+20, cy+15], outline=BLACK, width=3, fill=BG)
        draw.ellipse([cx+18, cy-5, cx+28, cy+6], outline=BLACK, width=2, fill=BG)
        draw.ellipse([cx-8, cy-20, cx+8, cy-12], outline=BLACK, width=2, fill=BG)
        draw.rectangle([cx-5, cy-12, cx+5, cy-8], fill=BLACK)
        draw.point([cx+6, cy-5], fill=BLACK)
        
    elif icon_type == "star":
        pts = []
        for i in range(10):
            angle = math.pi/2 + i * math.pi/5
            r = s if i % 2 == 0 else s//2
            pts.append((cx + r * math.cos(angle), cy -15 + r * math.sin(angle)))
        draw.polygon(pts, outline=GOLD, width=3, fill=(255, 240, 200))
        
    elif icon_type == "growth":
        draw.line([cx-s, cy+10, cx-10, cy+10, cx+10, cy-30, cx+s-20, cy-30, cx+s-20, cy-45], fill=GREEN, width=5)
        draw.line([cx+s-30, cy-45, cx+s-20, cy-45, cx+s-20, cy-35], fill=GREEN, width=5)
        bbox = draw.textbbox((0, 0), "$", font=ImageFont.truetype(FONT_BOLD, 24))
        draw.text((cx + 10 - (bbox[2]-bbox[0])//2, cy - 15), "$", fill=GREEN, font=ImageFont.truetype(FONT_BOLD, 24))
        
    elif icon_type == "shield":
        pts = [(cx-20, cy-15), (cx+20, cy-15), (cx+22, cy+5), (cx, cy+20), (cx-22, cy+5)]
        draw.polygon(pts, outline=BLUE, width=3, fill=LIGHT_BLUE)
        
    elif icon_type == "calendar":
        draw.rectangle([cx-20, cy-18, cx+20, cy+18], outline=BLACK, width=3, fill=BG)
        draw.line([cx-20, cy-5, cx+20, cy-5], fill=BLACK, width=2)
        draw.rectangle([cx-12, cy-12, cx-5, cy-8], fill=BLACK)
        draw.rectangle([cx+5, cy-12, cx+12, cy-8], fill=BLACK)
        
    elif icon_type == "clock":
        draw.ellipse([cx-18, cy-18, cx+18, cy+18], outline=BLACK, width=3, fill=BG)
        draw.line([cx, cy, cx, cy-10], fill=BLACK, width=3)
        draw.line([cx, cy, cx+8, cy-3], fill=BLACK, width=3)
        
    elif icon_type == "question":
        bbox = draw.textbbox((0, 0), "?", font=ImageFont.truetype(FONT_BOLD, 50))
        draw.text((cx - (bbox[2]-bbox[0])//2, cy - 20), "?", fill=BLUE, font=ImageFont.truetype(FONT_BOLD, 50))
```

## Helper for Placing Icons Under Cards

```python
def place_icon_under_card(draw, card_x, icon_type):
    """Place an icon centered under a card."""
    card_w = CARD_W  # 42% of frame width
    card_h = CARD_H  # 14% of frame height
    card_y = CARD_Y  # 6% from top
    icon_cx = card_x + card_w // 2
    icon_cy = card_y + card_h + 40
    draw_icon(draw, icon_cx, icon_cy, icon_type, size=55)
```
