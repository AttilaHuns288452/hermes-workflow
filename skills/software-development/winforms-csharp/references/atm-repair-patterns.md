# ATM Crypto Bank Repair Notes

## Locked EXE during rebuild
Symptom: `MSB3021` / `MSB3027` copy failures with `The process cannot access the file ... because it is being used by another process`.
Fix: kill the running `AtmCryptoBank.exe`, then `dotnet clean`, remove `bin/obj`, and rebuild.

## Namespace mismatch
Symptom: `CS0234` `The type or namespace name 'UI' does not exist in the namespace 'AtmCryptoBank'`.
Cause: `Program.cs` had `using AtmCryptoBank.UI;` but the form was later moved to `AtmCryptoBank`.
Fix: remove stale `using` and align namespaces.

## Storage method rename
Old expectation in UI: `CreateAccountAsync(...)` returning `Task<string>` with account number.
Actual interface shape: `Task<string> CreateAccountAsync(...)`.
UI fix: call `.GetAwaiter().GetResult()` from WinForms event handlers to avoid async lambda issues, and use the returned account number for status text.

## Black screen on launch
Cause: form BackColor was dark but controls were not explicitly colored.
Fix: apply full dark premium palette to every control: form, card panels, labels, textboxes, buttons, and prompts.
