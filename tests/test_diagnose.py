import json
import hashlib
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/codex-session-scout/scripts/codex-session-scout"
SESSION_ID = "abcdef01-1234-5678-90ab-abcdef012345"
OTHER_SESSION_ID = "abcdef02-1234-5678-90ab-abcdef012345"


class DiagnoseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.codex_home = self.root / "codex"
        self.session_dir = self.codex_home / "sessions" / "2026" / "11" / "21"
        self.session_dir.mkdir(parents=True)
        self.project = self.root / "project"
        self.project.mkdir()
        self.session_path = self.session_dir / f"rollout-2026-11-21T09-00-00-{SESSION_ID}.jsonl"
        self.session_path.write_text(
            json.dumps({"type": "session_meta", "payload": {"id": SESSION_ID, "cwd": str(self.project)}}) + "\n",
            encoding="utf-8",
        )
        self.env = {**os.environ, "CODEX_HOME": str(self.codex_home)}

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args, env=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=env or self.env,
            check=False,
        )

    def test_diagnose_correlates_pane_native_hook_and_codex_logs(self):
        log_dir = self.project / ".omx" / "logs"
        log_dir.mkdir(parents=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        (log_dir / "native-hook-test.jsonl").write_text(
            "\n".join([
                json.dumps({"timestamp": timestamp, "type": "native_hook_dispatch_error", "hook_event_name": "PostToolUse", "session_id": SESSION_ID, "error": "fixture hook dispatch failed"}),
                json.dumps({"timestamp": timestamp, "type": "native_hook_dispatch_error", "hook_event_name": "Stop", "session_id": OTHER_SESSION_ID, "error": "unrelated session"}),
            ]) + "\n",
            encoding="utf-8",
        )
        database = self.codex_home / "logs_2.sqlite"
        database.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database)
        connection.execute("CREATE TABLE logs (ts INTEGER, ts_nanos INTEGER, level TEXT, target TEXT, feedback_log_body TEXT, module_path TEXT, line INTEGER, thread_id TEXT)")
        now = int(time.time())
        connection.executemany(
            "INSERT INTO logs VALUES (?, 0, ?, ?, ?, ?, ?, ?)",
            [
                (now, "ERROR", "codex_core::hooks::runner", "hook exited with code 1: dispatch failed", "codex_core::hooks::runner", 31, SESSION_ID),
                (now, "ERROR", "codex_core::hooks::runner", "unrelated failure", "codex_core::hooks::runner", 32, OTHER_SESSION_ID),
                (now, "WARN", "codex_mcp::client", "MCP server startup failed server_name=computer-use", "codex_mcp::client", 43, None),
            ],
        )
        connection.commit()
        connection.close()

        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        fake_tmux = fake_bin / "tmux"
        fake_tmux.write_text(
            "#!/usr/bin/env python3\n"
            "print('• Hook failed')\n"
            "print('  └ hook exited with code 1')\n",
            encoding="utf-8",
        )
        fake_tmux.chmod(0o755)
        env = {**self.env, "PATH": f"{fake_bin}:{self.env.get('PATH', '')}"}
        result = self.run_cli("diagnose", SESSION_ID, "--since", "1h", "--tmux-pane", "%0", "--format", "json", env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["session"]["id"], SESSION_ID)
        self.assertEqual(report["summary"]["visible_hook_failures"], 1)
        self.assertEqual(len(report["omx_native_hook_errors"]), 1)
        self.assertEqual(report["omx_native_hook_errors"][0]["hook_event_name"], "PostToolUse")
        details = " ".join(record["detail"] for record in report["codex_app_logs"]["records"])
        self.assertIn("hook exited with code 1", details)
        self.assertIn("MCP server startup failed", details)
        self.assertNotIn("unrelated failure", details)

    def test_diagnose_reports_missing_logs_without_failing(self):
        result = self.run_cli("diagnose", SESSION_ID, "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["omx_native_hook_errors"], [])
        self.assertEqual(report["codex_app_logs"]["records"], [])
        self.assertEqual(report["codex_app_logs"]["error"], "Codex app log database not found")

    def test_diagnose_detects_orphaned_live_pin_reclaim_hardlink_read_only(self):
        version = "0.22.6"
        cache_base = self.codex_home / "plugins" / "cache" / "oh-my-codex-local" / "oh-my-codex"
        version_dir = cache_base / version
        (version_dir / ".codex-plugin").mkdir(parents=True)
        (version_dir / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "oh-my-codex", "version": version}), encoding="utf-8"
        )
        pin_dir = cache_base / ".omx-pins" / version
        pin_dir.mkdir(parents=True)

        dead_pid = 999_999_999
        while True:
            try:
                os.kill(dead_pid, 0)
            except ProcessLookupError:
                break
            except PermissionError:
                dead_pid += 1
                continue
            dead_pid += 1
        token = "12345678-1234-5678-90ab-abcdef012345"
        version_hash = hashlib.sha256(version.encode()).hexdigest()[:24]
        lock_path = cache_base / f".omx-live-pin-{version_hash}.lock"
        lock_path.write_text(
            json.dumps({"version": 1, "pid": dead_pid, "operation": "pin", "token": token}) + "\n",
            encoding="utf-8",
        )
        expected_stage = f"{lock_path.name}.stage-{dead_pid}-{token}"
        reclaim_path = cache_base / f".{expected_stage}.reclaim-{dead_pid}-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
        os.link(lock_path, reclaim_path)
        session_hash = hashlib.sha256(SESSION_ID.encode()).hexdigest()
        intent_path = cache_base / f".omx-live-pin-intent-{version_hash}-{session_hash}.json"
        intent_path.write_text(
            json.dumps({"version": 1, "cacheVersion": version, "sessionHash": session_hash}), encoding="utf-8"
        )

        original_inode = lock_path.stat().st_ino
        result = self.run_cli("diagnose", SESSION_ID, "--format", "json")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        record, = report["omx_plugin_cache_pin_locks"]["records"]
        self.assertEqual(record["status"], "orphaned_reclaim_hardlink")
        self.assertEqual(record["version"], version)
        self.assertEqual(record["owner_state"], "exited")
        self.assertEqual(record["link_count"], 2)
        self.assertFalse(record["expected_stage_present"])
        self.assertEqual(record["same_inode_reclaim_links"], 1)
        self.assertFalse(record["session_pin_present"])
        self.assertTrue(record["session_intent_present"])
        self.assertEqual(report["summary"]["orphaned_omx_plugin_pin_locks"], 1)
        self.assertEqual(lock_path.stat().st_ino, original_inode)
        self.assertTrue(lock_path.exists())
        self.assertTrue(reclaim_path.exists())

    def test_diagnose_requires_an_existing_session(self):
        result = self.run_cli("diagnose", OTHER_SESSION_ID)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Session id not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
