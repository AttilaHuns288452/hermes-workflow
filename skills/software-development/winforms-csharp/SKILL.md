---
name: winforms-csharp
description: "Scaffold, build, and run a WinForms C# application using .NET SDK."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
---

# WinForms C# Application Skill

## Trigger Conditions
- User asks to create, build, or run a Windows Forms (WinForms) application in C#.
- User wants a simple GUI calculator, data entry form, or any desktop app using System.Windows.Forms.

## Overview
This skill provides a reusable workflow to scaffold, build, and run a basic WinForms C# project using the .NET SDK. It includes project structure, minimal boilerplate, and steps to compile and execute the application.

## References
- `references/winforms-overview.md` – brief overview of WinForms and .NET Windows Desktop SDK.
- `templates/WinForms.csproj` – minimal project file template.
- `templates/Program.cs` – minimal WinForms entry point with a simple form.
- `scripts/build-and-run.bat` – Windows batch script to restore, build, and run the project.
- `references/premium-calculator.md` – verified premium calculator palette, layout, and failure modes.
- `references/calculator-pattern.md` – concrete calculator implementation notes, verified call shapes, and default UI values.
- `references/atm-repair-patterns.md` – repair recipes for common WinForms ATM rebuild issues: locked EXE, namespace mismatches, storage method rename, and black-screen fixes.

## Steps

1. **Create project directory**
   ```bash
   mkdir -p <project-name>
   cd <project-name>
   ```

2. **Add project file** (copy from template or write directly)
   ```xml
   <Project Sdk="Microsoft.NET.Sdk.WindowsDesktop">
     <PropertyGroup>
       <OutputType>WinExe</OutputType>
       <TargetFramework>net8.0-windows</TargetFramework>
       <UseWindowsForms>true</UseWindowsForms>
       <Nullable>enable</Nullable>
       <ImplicitUsings>enable</ImplicitUsings>
     </PropertyGroup>
   </Project>
   ```

3. **Add Program.cs** (copy from template)
   ```csharp
   using System;
   using System.Drawing;
   using System.Windows.Forms;

   namespace <project-name>
   {
       public class MainForm : Form
       {
           private TextBox txtInput;
           private Button btnShow;
           private Label lblOutput;

           public MainForm()
           {
               Text = "WinForms App";
               Size = new Size(300, 200);
               StartPosition = FormStartPosition.CenterScreen;

               txtInput = new TextBox { Left = 10, Top = 20, Width = 260 };
               btnShow = new Button { Text = "Show", Left = 10, Top = 50, Width = 75 };
               lblOutput = new Label { Left = 10, Top = 80, AutoSize = true };

               btnShow.Click += (s, e) =>
               {
                   lblOutput.Text = $"You entered: {txtInput.Text}";
               };

               Controls.AddRange(new Control[] { txtInput, btnShow, lblOutput });
           }

           [STAThread]
           public static void Main()
           {
               Application.SetHighDpiMode(HighDpiMode.SystemAware);
               Application.EnableVisualStyles();
               Application.SetCompatibleTextRenderingDefault(false);
               Application.Run(new MainForm());
           }
       }
   }
   ```

4. **Restore dependencies**
   ```bash
   dotnet restore
   ```

5. **Build the project**
   ```bash
   dotnet build
   ```

6. **Run the application**
   ```bash
   dotnet run
   ```
   *or* run the generated executable directly:
   ```bash
   .\\bin\\Debug\\net8.0-windows\\<project-name>.exe
   ```

## Design Guidance — Modern & Premium Look

### Color Contrast Rules (MANDATORY)
- **Dark theme**: Use `#1E1E1E` or `#2D2D30` for the form background.
- **Display area**: `#2D2D30` or darker (`#121212`), white text — high contrast is non-negotiable.
- **Number buttons**: `#505050` minimum fill, white bold text. Do NOT use near-black fills (`#202020`) — they blend into the form background.
- **Operator buttons**: A vivid orange `#FF9F1C` or `#FF9500` with **white** text — must visibly contrast against the dark background.
- **Equals button**: A bright blue `#0078D4` with **white** text.
- **Function buttons** (C, ±, %): `#A0A0A0` fill with **black** text for contrast.
- **Hover state**: Lighten each button's base color by 15-20% on mouseover.
- **Verification**: Each button text must be readable from 2 feet away on a 1080p display.

### Typography
- Display: **Segoe UI 28pt Bold**, right-aligned, white on dark.
- Buttons: **Segoe UI 14pt Bold**, matching the style.
- Labels: **Segoe UI 9-10pt**.

### Spacing & Layout
- Button padding: **4px** minimum between buttons.
- Form size: allow enough room — 320×480px minimum for a standard calculator.
- Zero button spans two columns (classic feel).
- Use `TableLayoutPanel` with `SizeType.Percent` for equal sizing.

### Common Failures
- Same dark fill on the form AND the buttons → buttons invisible against background.
- Using `#202020` or `#1A1A1A` button fills on a `#1E1E1E` form.
- No hover feedback → feels dead and unresponsive.
- Flat style with `BorderSize = 0` is fine IF the background color makes the button obvious.
- `TableLayoutPanel.SetColumnSpan` expects a `bool`, not a column count. If a helper method such as `AddButton(..., bool spanColumns = false)` wraps span logic, pass `true`/`false` rather than `2`.

## Workflow Policy
- Build first, then run. Do not hand-wave past a failing build.
- When a prior partial scaffold exists, prefer a clean new project in a fresh subdir or a verified empty project state before adding files.
- Do not keep orphaned partial files live in the project tree. If a partial split changes, remove the leftover file.
- Keep the design and docs aligned with the user’s tooling: document the design model and update Obsidian notes for the project in the same pass.
- **Namespace matching rule:** A folder layout alone does not guarantee a matching namespace. After creating `Models/`, `Services/`, or `Forms/`, confirm the actual `namespace ...` declaration in each file before referencing that namespace elsewhere. The most common mismatch is root-namespace files left in `AtmCryptoBank;` while consumers add `using AtmCryptoBank.Models;`.
- **Startup form rule:** When resuming an existing scaffold, verify the form type referenced from `Program.cs` actually exists in the current file tree. Mismatches between legacy form names and current file names are a frequent cause of `CS0246` at the entry point.
- **Resume repair sequence:** For a stalled WinForms build, run: 1) `dotnet clean`, 2) remove `bin/obj`, 3) inspect `*.csproj`, 4) list project files, 5) inspect namespace declarations and `Program.cs` startup type, 6) rebuild before adding new code.
- **Locked EXE guard:** Before rebuilding, check if the running EXE is locked. If `dotnet build` fails with `MSB3021`/`MSB3027` copy errors, kill the running process or clean `bin/obj` before retrying.
- **Design enforcement:** Always apply a verified dark premium palette. Never ship a form with only a BackColor set and no explicit control colors — that produces a black screen with invisible controls. Verify every button and field has a distinct fill from the form background.

## User Preferences
- Polished, high-fidelity UI: use the premium dark palette from `references/premium-calculator.md` as the baseline for all WinForms apps.
- End-to-end completion: prefer finishing the task cleanly in one pass over incremental troubleshooting.
- Obsidian notes: update project notes in the same pass as code changes; keep them aligned with the actual project state.

## Verification
- After `dotnet run`, a window should appear with the controls defined in `Program.cs`.
- The executable should exist at `bin/Debug/<tfm>/<project-name>.exe`.
- No build errors (warnings are acceptable).

## Optional Enhancements
- Add more controls (menus, dialogs) by dragging in Designer or coding manually.
- Use MVVM or data binding for more complex apps.
- Publish as a self-contained executable: `dotnet publish -r win-x64 --self-contained true`.

## Notes
- This skill targets .NET 6+; adjust `<TargetFramework>` as needed.
- The templates use placeholders `<project-name>`; replace with actual folder name or use script to substitute.