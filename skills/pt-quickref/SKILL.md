---
name: pt-quickref
description: Packet Tracer quick reference + debug guide for local model sessions. Use when doing or troubleshooting anything in Cisco Packet Tracer via the packet-tracer MCP.
---

# Packet Tracer quickref (condensed from verified lab + benchmark)

## SSH recipe (PT 9.0 — the one that works)
```
R1(config)# crypto key generate rsa        <- config mode, NO modulus on this line
How many bits in the modulus [512]: 1024   <- answer as a SEPARATE line
% Generating 1024 bit RSA keys...[OK]
%SSH-5-ENABLED: SSH 1.99 has been enabled
```
☠️ TRAP: `crypto key generate rsa modulus 1024` is SILENTLY REJECTED ("Invalid input") even though valid on real IOS. Without keys SSH greets then dies: "Connection closed by foreign host". This includes pt_apply_hardening's own generated config — after hardening, always re-do keygen manually and verify `%SSH-5-ENABLED`.

## Full SSH enable on PT router
```
conf t
 hostname R1
 username admin privilege 15 secret <pass>
 username lab privilege 1 secret <pass>
 enable secret <enable-pass>
 ip domain-name lab.local
 crypto key generate rsa            <- then answer 1024 at the prompt
 ip ssh version 2
 line vty 0 4
  transport input ssh
  login local
 banner motd #Authorized access only#
```
L2 switch (2960) additionally needs an IP:
```
 conf t
  interface vlan 1
   ip address 192.168.0.10 255.255.255.0
   no shutdown
  ip default-gateway 192.168.0.1
```

## Debug playbook (symptom → cause → fix)
| Symptom | Cause | Fix |
|---|---|---|
| "Connection closed by foreign host" | no RSA keys | keygen recipe above |
| "% Connection refused" | target has no IP | interface IP / SVI + `no shut` |
| banner shows but login closes | VTY not `login local` / wrong `transport input` | `line vty 0 4` → `login local`, `transport input ssh` |
| "Translating..." hang ~70s | stray input triggers DNS lookup | Ctrl+Shift+6, then `no ip domain-lookup` |
| commands turn into junk (line 3, login prompt) | console context reset / initial-config dialog | answer `no` to dialog; re-`enable`; send one command at a time |
| DHCP client gets 169.254.x | pool wrong / server not in LAN | `ip dhcp pool LAN1`, `network`, `default-router` |
| SW1 SSH from PC fails after router works | L2 switch has no routable IP | SVI + `ip default-gateway` |

## Console discipline (mandatory for pt_send_raw)
1. ONE command per call. 2. Settle ~300ms. 3. Read prompt/echo in a SEPARATE call. 4. Never rely on `setTimeout` batching. 5. Read the echo/output and adapt — never resend an identical call in a loop.
States: `R1>` needs `enable` → `R1#` needs `configure terminal` → `R1(config)#`. Dialog prompt = answer `no`. `Username:` = console bounced, log in again.

## Verification bar (never claim without these)
- topology: `pt_query_topology` shows devices+links
- users: console `show users` after a real SSH login (`* <n> vty 0 admin`)
- `pt_health_check` green + `write memory` on each device

## Bridge handshake (startup lag)
If `pt_bridge_status` reports "no está conectado": PT's extension retries the bridge every ~30-60 s. Just wait and call `pt_bridge_status` again — do NOT rebuild/restart anything. "CONNECTED por HTTP" = linked. First tool call in a fresh session may fail for this reason only.
