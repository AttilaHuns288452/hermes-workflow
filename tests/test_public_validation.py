from pathlib import Path

import pytest

from scripts import validate_repo
from scripts.audit_skills import find_secret_hits


ROOT = Path(__file__).resolve().parents[1]


def test_config_template_is_valid_yaml():
    data = validate_repo.load_yaml(ROOT / "config.yaml.template")
    assert isinstance(data, dict)
    assert isinstance(data["mcp_servers"], dict)
    assert isinstance(data["mcp_servers"]["opendesign"]["args"], list)
    assert all(server["enabled"] is False for server in data["mcp_servers"].values())
    assert data["fallback_providers"] == []
    assert "YOUR_MODEL_ID" in str(data["model"])


def test_duplicate_yaml_keys_are_rejected(tmp_path):
    path = tmp_path / "duplicate.yaml"
    path.write_text("a: 1\na: 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate YAML key"):
        validate_repo.load_yaml(path)


def test_added_credential_patterns_match_examples():
    import ast
    import re

    source = (ROOT / "scripts" / "audit_skills.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    patterns = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(getattr(target, "id", None) == "SECRET_PATTERNS" for target in node.targets)
    )
    samples = (
        "Bearer " + "A" * 32,
        "ghu_" + "A" * 30,
        "ghs_" + "B" * 30,
        "ghr_" + "C" * 30,
        "aws_secret_access_key='" + "A" * 40 + "'",
        "sk_live_" + "A" * 24,
        "sk-proj-" + "A" * 24,
        "glpat-" + "A" * 20,
        "npm_" + "A" * 36,
        "AKIA" + "B" * 16,
        "postgres://user:" + "A" * 32 + "@example.test/db",
        "mongodb+srv://user:" + "B" * 32 + "@example.test/db",
    )
    for sample in samples:
        assert any(re.search(pattern, sample) for pattern in patterns)
    assert not find_secret_hits("fixture/SKILL.md", "documented AWS example: AKIAIOSFODNN7EXAMPLE")


def test_secret_scan_does_not_ignore_a_credential_just_because_line_says_scan():
    leaked = "This scan found Bearer " + "A" * 32
    assert find_secret_hits("fixture/SKILL.md", leaked)
    regex_example = r"grep -E 'postgres(?:ql)?://[^\s:@]+:[^\s@]+@' repo/"
    assert not find_secret_hits("fixture/SKILL.md", regex_example)
    no_group_regex = r"grep -E 'postgres://[^:@]+:[^@]+@' repo/"
    assert not find_secret_hits("fixture/SKILL.md", no_group_regex)
    mixed = regex_example + " # leaked Bearer " + "A" * 32
    assert find_secret_hits("fixture/SKILL.md", mixed)
    header_only = 'private_key: "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----"'
    assert not find_secret_hits("fixture/SKILL.md", header_only)
    key_block = "-----BEGIN PRIVATE KEY-----\n" + "A" * 64 + "\n-----END PRIVATE KEY-----"
    assert find_secret_hits("fixture/SKILL.md", key_block)


def test_public_secret_scanner_covers_text_outside_the_skill_tree(tmp_path):
    from scripts.audit_public_secrets import scan_paths

    key_shaped_value = "sk-" + "A" * 32
    (tmp_path / "README.md").write_text(f"Example: {key_shaped_value}\n", encoding="utf-8")
    secret_named_file = Path(key_shaped_value + ".txt")
    (tmp_path / secret_named_file).write_text("", encoding="utf-8")
    hits, errors, scanned, skipped = scan_paths(tmp_path, [Path("README.md"), secret_named_file])

    assert not errors and scanned == 2 and skipped == 0
    assert len(hits) == 1
    assert "README.md" in hits[0] and "[REDACTED].txt" not in hits[0]
    assert key_shaped_value not in "\n".join(hits)


def test_public_secret_scanner_does_not_follow_symlinks(tmp_path):
    from scripts.audit_public_secrets import scan_paths

    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("sk-" + "A" * 32, encoding="utf-8")
    (root / "linked.txt").symlink_to(outside)

    hits, errors, scanned, skipped = scan_paths(root, [Path("linked.txt")])
    assert not hits and not errors
    assert scanned == 0 and skipped == 1


def test_public_copy_matches_license_and_configurable_routes():
    app = (ROOT / "src" / "App.jsx").read_text(encoding="utf-8")
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    integrations = (ROOT / "src" / "data-integrations.json").read_text(encoding="utf-8")
    setup = (ROOT / "SETUP.md").read_text(encoding="utf-8")
    integration = (ROOT / "INTEGRATION.md").read_text(encoding="utf-8")
    config_template = (ROOT / "config.yaml.template").read_text(encoding="utf-8")
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")

    assert "CC BY-NC 4.0" in license_text and "CC BY-NC 4.0" in app
    for unverified in ("MIT License", "Free Models", "No API Key Required", "Token Savings", "CodeGraph Nodes", "xKiro API", "OpenRouter free", "OmniRoute Gateway", "Paid (last resort)", "LightRAG Fallback", "Mandatory docs & knowledge graph refresh"):
        assert unverified not in app
    assert "Profile-Configured Model Routing" in app
    assert "model.default" in app and "model.provider" in app
    assert "Repository Skill Catalog" in (ROOT / "legacy" / "index-tailwind.html").read_text(encoding="utf-8")
    assert "Profile-Configured Model Routing" in (ROOT / "legacy" / "index-tailwind.html").read_text(encoding="utf-8")
    for stale_claim in ("xKiro API", "OpenRouter free", "OmniRoute Gateway", "Paid (last resort)", "LightRAG Fallback", "Mandatory docs & knowledge graph refresh"):
        assert stale_claim not in app
    legacy_paths = (ROOT / "legacy" / "index.html", ROOT / "legacy" / "index-tailwind.html")
    for legacy_path in legacy_paths:
        legacy = legacy_path.read_text(encoding="utf-8")
        for stale_claim in ("Free Models", "Freebuff", "FreeLLMAPI", "OpenRouter:free", "Paid (last resort)", "DeepSeek V4 Flash", "Token Savings", "35×", "1,233×", "668+", "Token Saver", "free model", "OpenCode", "ECC", "Graphify", "CodeGraph"):
            assert stale_claim.lower() not in legacy.lower(), f"{legacy_path}: {stale_claim}"
    assert "model choice follows your Hermes profile" in integrations
    assert "GLM 5.2" not in integrations
    assert "connect.composio.dev/mcp" not in integrations
    assert "60+ design systems" not in integrations
    integration_rows = [line for line in integrations.splitlines() if '"d":' in line]
    assert len(integration_rows) == 14
    assert all("Optional" in line or "profile" in line for line in integration_rows)
    assert "## Step 6: Optional Provider" in setup
    assert "## Step 8: Optional Obsidian Vault" in setup
    assert setup.index("## Step 9: Verify the Configured Route") < setup.index("## Step 10: Test the Pipeline")
    assert "hermes config env-path" in setup
    assert "hermes config env-path" in integration
    assert all("~/.hermes/.env" not in text for text in (setup, integration, config_template))
    assert "cp .env.example .env" not in setup and "source .env" not in setup
    assert "FreeLLMAPI" not in setup and "FreeLLMAPI" not in env_example
    assert "Default dashboard login" not in env_example
    for variable in ("HERMES_WORKFLOW_ROOT", "HERMES_EXTERNAL_SKILLS_ROOT", "LLMQUANT_API_KEY", "FIRECRAWL_API_KEY", "FIGMA_API_KEY", "OPENDESIGN_EXECUTABLE", "OPENDESIGN_DAEMON_CLI"):
        line = next(line for line in env_example.splitlines() if line.startswith(f"{variable}="))
        assert line.endswith("=") if "_KEY" in variable else "=" in line
    assert "Mandatory post-execution phase" not in integration
    assert "ordinary tasks do not create notes" in integration.lower()
    for stale_claim in ("139-entry", "FreeLLMAPI", "Freebuff", "26,005", "BUNDLE RULE", "OpenRouter free tier"):
        assert stale_claim not in integration


def test_readme_and_meta_prompt_are_profile_neutral():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    meta_prompt = (ROOT / "META_PROMPT.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "public-quality.yml").read_text(encoding="utf-8")

    for command in ("hermes config path", "hermes config env-path", "hermes config check", "hermes mcp list"):
        assert command in readme
    for unsafe_copy in (
        "cp config.yaml.template ~/.hermes/config.yaml",
        "cp .env.example ~/.hermes/.env",
    ):
        assert unsafe_copy not in readme
    for stale_claim in ("cheap first", "50×", "1,233×", "715 top-level directories", "OPENROUTER_API_KEY", "HERMES_USERNAME", "Graphify", "last configured provider"):
        assert stale_claim not in readme

    assert "not an installed Hermes profile" in meta_prompt
    assert "does not load skills" in meta_prompt
    assert "hermes config env-path" in meta_prompt
    for stale_claim in (
        "FreeLLMAPI",
        "free-ai-model-router",
        "freellmapi-admin",
        "5-layer free-first chain",
        "Graphify (v0.8.37)",
        "50× to 1,233×",
        "Model used for this session:",
    ):
        assert stale_claim not in meta_prompt

    assert "scripts/audit_public_secrets.py" in security
    assert "not proof" in security
    assert "npm run lint:skills" in security
    catalog = (ROOT / "SKILLS_CATALOG.md").read_text(encoding="utf-8")
    assert "1,484 repository skills" in catalog
    assert "715 top-level directories" not in catalog
    assert "run: python scripts/audit_public_secrets.py" in workflow
    assert "npm run lint:skills" in workflow
    assert "git diff --exit-code -- docs" in workflow
    assert "git ls-files --others --exclude-standard docs" in workflow
    for path in ("README.md", "META_PROMPT.md", "SECURITY.md", "scripts/**", "tests/**"):
        assert f'"{path}"' in workflow
    assert '".env.example"' in workflow
    assert '"LICENSE"' in workflow
    assert '".github/workflows/public-quality.yml"' in workflow
    assert '"package*.json"' in workflow
    assert '"skills/**"' in workflow
    assert '"docs/**"' in workflow
    assert '"src/**"' in workflow
    assert '"config.yaml.template"' in workflow
    assert '"SETUP.md"' in workflow
    assert '"SKILLS_CATALOG.md"' in workflow
    assert '"INTEGRATION.md"' in workflow
    assert '"index.html"' in workflow
    assert '"vite.config.*"' in workflow
    assert '".github/workflows/public-quality.yml"' in workflow


def test_repo_validator_passes_current_tree():
    assert validate_repo.main() == 0


def test_drift_checker_accepts_matching_fixture(tmp_path, capsys, monkeypatch):
    from scripts import repo_drift

    repo = tmp_path / "repo"
    live = tmp_path / "live"
    for root in (repo, live):
        skill = root / "skills" / "example"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: example\ndescription: Example skill\n---\n", encoding="utf-8"
        )
    (repo / "README.md").write_text("", encoding="utf-8")
    (repo / "SKILLS_CATALOG.md").write_text("", encoding="utf-8")
    (repo / "INTEGRATION.md").write_text("", encoding="utf-8")
    monkeypatch.setattr(repo_drift, "parse_args", lambda: type("Args", (), {
        "repo_root": repo, "live_root": live
    })())
    assert repo_drift.main() == 0
    assert "OK: repo matches the live tree" in capsys.readouterr().out


def test_drift_checker_reports_missing_live_root(tmp_path, capsys, monkeypatch):
    from scripts import repo_drift

    repo = tmp_path / "repo"
    (repo / "skills" / "example").mkdir(parents=True)
    (repo / "skills" / "example" / "SKILL.md").write_text(
        "---\nname: example\ndescription: Example skill\n---\n", encoding="utf-8"
    )
    (repo / "README.md").write_text("", encoding="utf-8")
    (repo / "SKILLS_CATALOG.md").write_text("", encoding="utf-8")
    (repo / "INTEGRATION.md").write_text("", encoding="utf-8")
    monkeypatch.setattr(repo_drift, "parse_args", lambda: type("Args", (), {
        "repo_root": repo, "live_root": tmp_path / "missing"
    })())
    assert repo_drift.main() == 2
    assert "LIVE ROOT MISSING" in capsys.readouterr().out
