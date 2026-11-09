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
| DHCP client gets 169.254.x (APIPA = nobody answered) | DHCP service off, server has no IP, no pool matches the client's LAN, or `ip helper-address` targets an IP no device owns | server gets a static IP in its LAN + service ON + one pool per client LAN (`network` + `default-router`); helper-address on the client-side router interface must equal the server's IP |
| client leases the router's own `.1` and fights it | pool start address includes `.1`, or Default-Gateway / Start-IP fields swapped when filling the GUI form | start the pool at `.10`; `default-router` = the router interface, never a host |
| PC stuck on 169.254 after the fix | PT caches APIPA and never retries | toggle the PC: IP Configuration → Static, then DHCP again |
| relayed PCs get the wrong LAN's addresses | PT served the default pool instead of the giaddr's | select the right pool → Set As Default, renew the clients |
| SW1 SSH from PC fails after router works | L2 switch has no routable IP | SVI + `ip default-gateway` |

Server-PT DHCP config (service on/off, pools) has no `pt_*` tool: dump it with `d.serializeToXml()` and read the `DHCP_SERVERS` block (full recipe in the `packet-tracer` skill).

## Console discipline (mandatory for pt_send_raw)
1. ONE command per call. 2. Settle ~300ms. 3. Read prompt/echo in a SEPARATE call. 4. Never rely on `setTimeout` batching. 5. Read the echo/output and adapt — never resend an identical call in a loop.
States: `R1>` needs `enable` → `R1#` needs `configure terminal` → `R1(config)#`. Dialog prompt = answer `no`. `Username:` = console bounced, log in again.

## Verification bar (never claim without these)
- topology: `pt_query_topology` shows devices+links
- users: console `show users` after a real SSH login (`* <n> vty 0 admin`)
- `pt_health_check` green + `write memory` on each device

## Bridge handshake (startup lag vs. mailbox mismatch)
If `pt_bridge_status` reports "no está conectado": call it again first — the HTTP bridge starts lazily on the first tool call of a session and the extension retries every ~30-60 s. Do NOT rebuild/restart anything. "CONNECTED por HTTP" = linked.
If PT is open and waiting does not clear it, the two ends are on different file mailboxes: the extension heartbeats `alive.txt` under `~/AppData/Local/packet-tracer-mcp/bridge` while the Python MCP reads `~/.local/state/packet-tracer-mcp/bridge`. Fresh heartbeat in one dir, nothing in the other = link them once: `ln -s ~/AppData/Local/packet-tracer-mcp/bridge ~/.local/state/packet-tracer-mcp/bridge`, then `pt_bridge_status` → "CONNECTED por file-bridge".
