# Roblox UI styling: native depth + idempotent modifiers

How to give a plain-Frame UI the surface treatment modern Roblox games have, without the
recursion and idempotency traps that come with creating modifiers at runtime.

## The stack (native, no image assets)

| Modifier | Job | Sensible values |
|---|---|---|
| `UICorner` | rounded card | `CornerRadius = UDim.new(0, 14)` |
| `UIStroke` | hairline edge that separates the card from the scene | `Thickness = 1`, `Transparency ≈ 0.86`, `ApplyStrokeMode = Border` |
| `UIShadow` | soft lift off the world | `BlurRadius = UDim.new(0, 14)`, `Transparency ≈ 0.55`, `Offset = UDim.new(0, 4)`, `Spread = UDim.new(0, 1)` |
| `UIGradient` | subtle top-to-bottom tint on the fill | `Rotation = 90`, `Transparency` 0.92 → 1 |

All four are `Instance.new`-able on current clients. Confirm before relying on one:
`pcall(Instance.new, "UIShadow")` returning `true` is the check, and it is cheap enough to
leave in as a guard.

## The guard pattern

An attribute, set before any work, not a class lookup:

```lua
local function style(panel: GuiObject)
    if panel:GetAttribute("TgStyled") then return end
    panel:SetAttribute("TgStyled", true)

    if panel:FindFirstChildOfClass("UICorner") == nil then
        local corner = Instance.new("UICorner")
        corner.CornerRadius = UDim.new(0, 14)
        pcall(function() corner.Parent = panel end)
    end

    local ok, shadow = pcall(Instance.new, "UIShadow")
    if ok and shadow then
        pcall(function()
            shadow.Name = "PanelShadow"      -- name BEFORE parenting
            shadow.BlurRadius = UDim.new(0, 14)
            shadow.Transparency = 0.55
            shadow.Parent = panel
        end)
    end
end
```

Why attribute and not `FindFirstChild("PanelShadow")`: if the class or name is not
registered the way you expect (engine version skew, or the headless mock), the lookup
returns nil every time and the modifier is created again on every pass — an unbounded
churn that manifests as a hang or a silent process abort, never as a clear error.

## Where to call it: registration, not the click path

Style the panel once, where the panel is registered with its manager:

```lua
function PanelManager.register(panel: GuiObject)
    table.insert(entries, { panel = panel })
    style(panel)
end
```

Doing it from a `DescendantAdded`-driven ordering pass means the modifier you just
parented fires the same hook that is currently running. The observed failure mode is
the Luau process dying with no assertion message.

If an ordering pass must exist, it needs both:

```lua
local ordering = false
local function order(gui)
    if ordering then return end
    ordering = true
    local ok, err = pcall(orderInner, gui)   -- never leave the flag stuck true
    ordering = false
    if not ok then print("[UiScaler] order failed:", err) end
end
```

## Modal scrim + pop

A dim layer is what makes a panel read as a modal:

```lua
local scrim = Instance.new("Frame")
scrim.Name = "Scrim"
scrim.Size = UDim2.new(1, 0, 1, 0)
scrim.Position = UDim2.new(0, 0, 0, 0)   -- MUST be set; an unset Position is a number
scrim.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
scrim.BackgroundTransparency = 0.55
scrim.BorderSizePixel = 0
scrim.ZIndex = 9                            -- just under the panels (10)
scrim.Visible = false
```

Create it at startup (in `register`), and only toggle `.Visible` in the click path.
Creation inside a click handler is what re-enters the UI pass.

Pop-on-open, 140ms, scale only:

```lua
local scale = frame:FindFirstChild("PanelPop") or Instance.new("UIScale")
scale.Name = "PanelPop"
scale.Parent = frame
scale.Scale = 0.94
TweenService:Create(scale, TweenInfo.new(0.14, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Scale = 1 }):Play()
```

**Verify the scrim visibly, never from a green suite.** A scrim can be created, wired and
covered by passing tests while no dimming appears on screen at all — the tests assert your
PanelManager logic, not that the frame draws above the 3D world. Take a capture with a panel
open and confirm the scene behind it is actually darker before calling it done.

## Judging the result

- Capture the panel in the LIVE client (Studio play mode or the browser client), not the
  offline renderer. The renderer cannot draw list-layout rows, so every panel looks empty
  and you will restyle a working UI.
- Compare old vs new frame side by side and ask an independent reviewer for a score plus
  the named element behind each complaint. Then verify every claim against the source
  before acting: a reviewer that says "this NPC has no eyes" is describing a
  parts-only art ceiling (not a bug you can fix with another frame), while "the rail is
  sorted alphabetically" is a real regression worth fixing immediately.
- Score out of 10 per iteration and keep the number. 4 → 7 across one styling pass is
  useful signal; "looks better now" is not.
