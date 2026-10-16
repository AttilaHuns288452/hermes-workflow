# Hermes team audit and implementation record

Date: 2026-10-11

## Architecture implemented

- **default**: Chief of Staff/orchestrator. Handles simple work directly and routes qualifying work to Kanban.
- **codingprofile**: software engineering owner.
- **learning**: research, source verification, documentation, scripts, and storyboards.
- **finance**: quantitative finance and data.
- **channel**: independent QA, review, and fact-checking.
- **local**: offline-safe execution and media/motion support.

The image/graphic role is intentionally merged into learning for briefs and local for execution. Project-management/knowledge coordination is intentionally merged into default plus the native Kanban board. No extra profile was created because Bot Mode supports a maximum of six members and the existing six are already the smallest useful team.

## Verified configuration

- Hermes version: `v0.21.6+131.g38880bd.dirty`.
- Cloud profiles: `default, channel, codingprofile, finance, learning` use xKiro and `xiaomi/mimo-v2.6-pro`.
- Local profile: `local` uses Ollama `phi4-mini` intentionally for offline work.
- Root Kanban: `orchestrator_profile=default`, `auto_decompose=true`, `review_dispatch=true`; gateway dispatcher is active. Root and all four cloud profiles now route vision, compression, triage specification, Kanban decomposition, and profile-description auxiliaries through xKiro MiMo. Their provider-level fallback defaults are also aligned to MiMo, so implicit provider resolution cannot silently switch to GLM. The local profile intentionally remains Ollama-only.
- Existing Bot Mode group preserved: **Codingprofile, Learning, Hermes, Finance, Local, Channel**. Members: `default, codingprofile, learning, finance, local, channel`.
- Collaboration protocol: `/home/attila/.hermes/TEAM_PROTOCOL.md`. Reusable workflows: `/home/attila/.hermes/TEAM_WORKFLOWS.md`.

## Real validation

- Existing smoke handoff: `t_a9f85f14` codingprofile → `t_6edfc70a` learning, both done.
- New coding dispatch: `t_ce3339b3`, codingprofile wrote and attached `team-smoke.txt`, exact content verified.
- New dependent QA dispatch: `t_7378e5b8`, channel independently verified the parent artifact and returned `PASS`; artifact unchanged.
- Full review lifecycle test: `t_7848fb1c` created a deliberate defect; dependent `t_92619744` independently returned `FAIL` with an exact correction; dependent `t_b7b4ca0a` applied the correction, requested review, and channel then independently approved it. The board recorded the `review_requested` transition and the second reviewer run.
- Final board after validation: 37 done, 0 ready, 0 running, 0 blocked, 0 review.
- Fresh direct profile probes after prompt changes: default, channel, codingprofile, finance, learning, and local returned exact responses. After routing all cloud auxiliaries through xKiro MiMo and disabling the stale Honcho selection in codingprofile and finance, fresh probes returned `MIMO_TEAM_OK` and then `MEMORY_FIXED_OK` with no Honcho warning.
- Gateway: active after restart.

## Actual media capability

- Verified available: `ffmpeg`, `ffprobe`, `blender`, Node/npm/npx, HyperFrames CLI, Pagecast and DemoSmith MCP processes, Blender MCP process, and relevant media skills.
- Chosen pipeline: brief → script/storyboard → local assets → HyperFrames or FFmpeg/Blender render → technical checks → extracted-frame review → corrections → final export. A disposable FFmpeg smoke artifact was actually produced at `/home/attila/.hermes/cache/scratch/team-media-smoke.mp4` (1.0s, 2,271 bytes, ffprobe-readable). The first SVG-input attempt correctly failed because this FFmpeg build has no SVG decoder; the fallback used a stdlib-generated PPM frame.
- Not claimed as fully available: some cloud image/video/TTS providers still report missing configuration/dependencies in logs. Vercel and Twelve Data OAuth remain intentionally parked.

## Backups and recovery

- Initial configuration backup: `/home/attila/.hermes/backups/team-architecture-20261010-2335/`.
- Prompt/metadata backup before team-contract changes: `/home/attila/.hermes/backups/team-prompts-20261010-2350/`.
- Media-prompt backup: `/home/attila/.hermes/backups/team-prompts-20261011-0030/`.
- Auxiliary-routing backup: `/home/attila/.hermes/backups/aux-routing-20261011-0115/`.
- Provider-default alignment backup: `/home/attila/.hermes/backups/xkiro-default-model-20261011-0135/`.
- Inactive-MoA model-routing cleanup backup: `/home/attila/.hermes/backups/model-routing-cleanup-20261011-0200/`.
- Honcho plugin cleanup backup: `/home/attila/.hermes/backups/honcho-cleanup-20261011-0225/`.
- Memory-routing backup: `/home/attila/.hermes/backups/memory-routing-20261011-0125b/`.
- Each backup has `MANIFEST.sha256`; hashes were verified. Restore only the named files after stopping the gateway, then restart and re-run the profile probes.

## Remaining gaps

- The primary Bot Mode group is local profile metadata, not a hosted multi-user room. Vercel and Twelve Data are now consistently parked in MCP config (`enabled: false`); backup: `/home/attila/.hermes/backups/vercel-park-20261011-0230/`.
- A targeted group-chat discussion was not completed: desktop computer-use input required foreground approval, and the visible session showed an approval-timeout notice. The group exists and its membership is independently verified from `profile.yaml`; the source confirms `GROUP_CHAT_MAX_MEMBERS = 6`.
- HyperFrames media smoke: `/home/attila/Downloads/hermes-team-hyperframes-smoke.mp4`, 2.0s, 1920×1080, 24fps, ffprobe-readable. `hyperframes check` passed with 0 errors and 2 non-blocking warnings. The artifact was rendered with the local HyperFrames pipeline and an extracted frame was verified at 1920×1080. This is a pipeline smoke artifact, not a claim of polished production video.
- Remaining gaps are bounded: Vercel/Twelve Data OAuth are intentionally parked; optional local media fallbacks for Whisper/Kokoro/MusicGen are not installed; Hermes doctor still reports the vendor-slug advisory and package-vulnerability advisories even though live xKiro calls work. The stale Honcho profile selection is now fully removed from codingprofile and finance, including their plugin lists; fresh probes returned `HONCHO_CLEAN_OK` without warnings. These do not block the verified MiMo profile probes, Kanban dispatch, or HyperFrames render.
- Backup durability was re-verified after the independent audit flagged the prior timeout: the 2026-10-11 run completed at 02:03:27, uploaded `Hermes_Backup_2026-10-11.zip.enc`, reset the job failure streak to 0, and remote retention now contains the 2026-10-10 and 2026-10-11 encrypted artifacts. The prior 2026-10-10 timeout was a transient upload stall, not the current state.
