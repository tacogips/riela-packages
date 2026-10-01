"""Regression checks for issue #130: write ownership, source snapshots and generated artifact roots."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PACKAGES = Path(__file__).resolve().parents[2]
CODEX_SCRIPTS = PACKAGES / "codex-design-and-implement-review-loop/workflows/codex-design-and-implement-review-loop/scripts"
DISPATCH_SCRIPTS = [
    CODEX_SCRIPTS / "dispatch-plans.py",
    PACKAGES / "fable-and-improve-opus/workflows/fable-and-improve-opus/scripts/dispatch-plans.py",
    PACKAGES / "opus-luna-design-and-implement-review-loop/workflows/opus-luna-design-and-implement-review-loop/scripts/dispatch-plans.py",
]
GATE_SCRIPT = CODEX_SCRIPTS / "validate-plan-contract.py"
SCRATCH = PACKAGES.parent / "tmp"


def load(script: Path, name: str = "dispatch_copy"):
    spec = importlib.util.spec_from_file_location(name, script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plan(plan_id: str = "tools", **fields) -> dict:
    result = {
        "planId": plan_id,
        "planPath": f"impl-plans/active/{plan_id}.md",
        "dependsOn": [],
        "writePaths": ["src/app.py"],
        "sharedPaths": [],
        "acceptanceCriteria": [f"{plan_id} is implemented"],
        "verification": ["python -m unittest"],
    }
    result.update(fields)
    return result


def manifest(plans: list[dict]) -> dict:
    return {
        "taskId": "artifact-roots",
        "implementationBranch": "feat/tools",
        "baseBranch": "main",
        "remote": "origin",
        "evidenceRoot": "tmp/artifact-roots",
        "reviewContext": {
            "issueReference": "tacogips/riela#130",
            "userProblem": "Generated tools must not become source snapshots.",
            "requiredOutcomes": ["Tool installs are artifact evidence"],
            "nonGoals": [],
            "constraints": [],
            "designDecisionsAndRationale": [],
            "intentionalTradeoffs": [],
            "supportedEdgeCases": [],
            "outOfScopeEdgeCases": [],
            "sourcePaths": ["src/app.py"],
        },
        "plans": plans,
    }


def fill(directory: Path, count: int) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for index in range(count):
        (directory / f"f{index:04d}").write_text("")


def sparse(path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


class ArtifactRootsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        SCRATCH.mkdir(exist_ok=True)
        self._directory = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.root = Path(self._directory.name).resolve()
        self.modules = [load(script) for script in DISPATCH_SCRIPTS]

    def tearDown(self) -> None:
        self._directory.cleanup()

    def project(self, module, plans: list[dict], accepted: list[str] | None = None) -> dict:
        manifest_path = "impl-plans/active/dispatch.json"
        manifest_file = self.root / manifest_path
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_file.write_text(json.dumps(manifest(plans)))
        envelope = {"input": {"_rielaInput": {"messages": [{
            "fromStepId": "integration-review",
            "createdOrder": 1,
            "payload": {"acceptedPlanIds": accepted or []},
        }]}}}
        with mock.patch.object(module.Path, "cwd", return_value=self.root), \
             mock.patch.object(module, "checkpoint_source", return_value=(manifest_path, "a" * 40)), \
             mock.patch.object(module, "verify_checkpoint"):
            return module.project(envelope)

    def items(self, module, plans: list[dict], accepted: list[str] | None = None) -> dict:
        result = self.project(module, plans, accepted)
        return {item["planId"]: item for item in result["payload"]["implementationItems"]}


class ProjectionTests(ArtifactRootsTestCase):
    def test_dispatch_scripts_stay_identical(self) -> None:
        reference = DISPATCH_SCRIPTS[0].read_bytes()
        for script in DISPATCH_SCRIPTS[1:]:
            with self.subTest(script=script):
                self.assertEqual(script.read_bytes(), reference)

    def test_old_manifest_without_artifact_roots_projects_empty_list(self) -> None:
        for module in self.modules:
            with self.subTest(module=module.__file__):
                item = self.items(module, [plan(writePaths=["src/app.py"], sharedPaths=["src/shared.py"])])["tools"]
                self.assertEqual(item["artifactRoots"], [])
                self.assertEqual(item["trackedPaths"], ["src/app.py", "src/shared.py"])

    def test_artifact_roots_are_removed_from_tracked_paths_but_keep_ownership(self) -> None:
        fill(self.root / "native-tools/cache", 600)
        sparse(self.root / "native-tools/bin/tool", 9_000_000)
        (self.root / "native-tools/toolchain.json").write_text("{}")
        for module in self.modules:
            with self.subTest(module=module.__file__):
                item = self.items(module, [plan(
                    writePaths=["src/app.py", "native-tools", "native-tools/toolchain.json"],
                    artifactRoots=["native-tools"],
                )])["tools"]
                self.assertEqual(item["writePaths"], ["src/app.py", "native-tools", "native-tools/toolchain.json"])
                self.assertEqual(item["artifactRoots"], ["native-tools"])
                self.assertEqual(item["trackedPaths"], ["src/app.py", "native-tools/toolchain.json"])

    def test_artifact_root_must_exactly_equal_a_write_path(self) -> None:
        for module in self.modules:
            with self.subTest(module=module.__file__):
                with self.assertRaisesRegex(ValueError, "must exactly equal one of the plan's writePaths"):
                    self.items(module, [plan(writePaths=["src/app.py", "tools"], artifactRoots=["tools/bin"])])

    def test_artifact_root_must_not_be_shared(self) -> None:
        for module in self.modules:
            with self.subTest(module=module.__file__):
                with self.assertRaisesRegex(ValueError, "must not appear in sharedPaths"):
                    self.items(module, [plan(
                        writePaths=["src/app.py", "tools"], sharedPaths=["tools"], artifactRoots=["tools"],
                    )])

    def test_source_paths_must_remain_after_artifact_removal(self) -> None:
        for module in self.modules:
            with self.subTest(module=module.__file__):
                with self.assertRaisesRegex(ValueError, "no source snapshot paths.*audit manifest.*writePaths"):
                    self.items(module, [plan(writePaths=["tools"], artifactRoots=["tools"])])

    def test_artifact_root_inside_a_source_path_is_rejected(self) -> None:
        for module in self.modules:
            with self.subTest(module=module.__file__):
                with self.assertRaisesRegex(ValueError, "'tools/cache' lies inside source snapshot path 'tools'"):
                    self.items(module, [plan(writePaths=["tools", "tools/cache"], artifactRoots=["tools/cache"])])

    def test_source_file_inside_an_artifact_root_is_allowed(self) -> None:
        (self.root / "tools").mkdir()
        (self.root / "tools/toolchain.json").write_text("{}")
        for module in self.modules:
            with self.subTest(module=module.__file__):
                item = self.items(module, [plan(writePaths=["tools/toolchain.json", "tools"], artifactRoots=["tools"])])["tools"]
                self.assertEqual(item["trackedPaths"], ["tools/toolchain.json"])

    def test_nested_artifact_roots_are_rejected(self) -> None:
        for module in self.modules:
            with self.subTest(module=module.__file__):
                with self.assertRaisesRegex(ValueError, "artifactRoots overlap"):
                    self.items(module, [plan(
                        writePaths=["src/app.py", "tools", "tools/cache"], artifactRoots=["tools", "tools/cache"],
                    )])

    def test_artifact_roots_use_concrete_path_rule_and_limit(self) -> None:
        module = self.modules[0]
        with self.assertRaisesRegex(ValueError, "concrete repository-relative"):
            self.items(module, [plan(writePaths=["src/app.py"], artifactRoots=["tools/*"])])
        with self.assertRaisesRegex(ValueError, "artifactRoots value .* must be an array"):
            self.items(module, [plan(writePaths=["src/app.py"], artifactRoots="tools")])
        roots = [f"tools/t{index}" for index in range(65)]
        with self.assertRaisesRegex(ValueError, "declares 65 roots \\(limit 64\\)"):
            self.items(module, [plan(writePaths=["src/app.py", *roots], artifactRoots=roots)])
        roots = roots[:64]
        item = self.items(module, [plan(writePaths=["src/app.py", *roots], artifactRoots=roots)])["tools"]
        self.assertEqual(len(item["artifactRoots"]), 64)


class PreflightTests(ArtifactRootsTestCase):
    def test_source_root_at_entry_limit_is_accepted(self) -> None:
        fill(self.root / "tools", 511)  # the directory itself plus 511 files = 512 entries
        item = self.items(self.modules[0], [plan(writePaths=["tools"])])["tools"]
        self.assertEqual(item["trackedPaths"], ["tools"])

    def test_source_root_above_entry_limit_requires_amendment(self) -> None:
        fill(self.root / "tools", 512)
        for module in self.modules:
            with self.subTest(module=module.__file__):
                with self.assertRaisesRegex(
                    ValueError,
                    r"bounded checkpoint amendment required: plan tools source root 'tools' currently has 513 entries.*limit 512.*artifactRoots",
                ):
                    self.items(module, [plan(writePaths=["tools"])])

    def test_entry_limit_applies_across_all_source_paths_of_a_plan(self) -> None:
        fill(self.root / "a", 300)
        fill(self.root / "b", 300)
        with self.assertRaisesRegex(ValueError, "source root 'b' currently has 301 entries.*expand to 602 entries"):
            self.items(self.modules[0], [plan(writePaths=["a", "b"])])

    def test_missing_source_root_counts_one_entry(self) -> None:
        fill(self.root / "a", 510)  # 511 entries plus one missing declared path = 512
        item = self.items(self.modules[0], [plan(writePaths=["a", "missing.txt"])])["tools"]
        self.assertEqual(item["trackedPaths"], ["a", "missing.txt"])
        with self.assertRaisesRegex(ValueError, "expand to 513 entries"):
            self.items(self.modules[0], [plan(writePaths=["a", "missing.txt", "missing-too.txt"])])

    def test_overlapping_source_roots_are_counted_once(self) -> None:
        fill(self.root / "a", 400)
        item = self.items(self.modules[0], [plan(writePaths=["a", "a/f0001"])])["tools"]
        self.assertEqual(item["trackedPaths"], ["a", "a/f0001"])

    def test_source_file_above_byte_limit_requires_amendment(self) -> None:
        sparse(self.root / "tools/bin/tool", 8_000_001)
        with self.assertRaisesRegex(ValueError, "'tools/bin/tool' with 8000001 bytes \\(limit 8000000 per file\\)"):
            self.items(self.modules[0], [plan(writePaths=["tools"])])
        sparse(self.root / "edge/file", 8_000_000)
        self.items(self.modules[0], [plan(writePaths=["edge"])])

    def test_source_total_above_byte_limit_requires_amendment(self) -> None:
        for index in range(9):
            sparse(self.root / f"blobs/b{index}", 7_500_000)
        with self.assertRaisesRegex(ValueError, "source snapshot total to 67500000 bytes \\(limit 64000000\\)"):
            self.items(self.modules[0], [plan(writePaths=["blobs"])])

    def test_same_growth_as_artifact_root_is_accepted(self) -> None:
        fill(self.root / "tools/cache", 1_000)
        sparse(self.root / "tools/bin/tool", 70_000_000)
        os.symlink("bin/tool", self.root / "tools/current")
        (self.root / "tools/toolchain.json").write_text("{}")
        item = self.items(self.modules[0], [plan(
            writePaths=["tools", "tools/toolchain.json"], artifactRoots=["tools"],
        )])["tools"]
        self.assertEqual(item["trackedPaths"], ["tools/toolchain.json"])

    def test_symlink_inside_source_root_is_rejected(self) -> None:
        (self.root / "src").mkdir()
        os.symlink("../outside", self.root / "src/link")
        with self.assertRaisesRegex(ValueError, "refuses symlink entries inside a source root at 'src/link'"):
            self.items(self.modules[0], [plan(writePaths=["src"])])

    def test_symlink_ancestry_is_rejected_for_both_selections(self) -> None:
        (self.root / "real").mkdir()
        os.symlink("real", self.root / "alias")
        with self.assertRaisesRegex(ValueError, "source root 'alias/x': fanout change tracking refuses symlink ancestry"):
            self.items(self.modules[0], [plan(writePaths=["alias/x"])])
        with self.assertRaisesRegex(ValueError, "artifact root 'alias': fanout change tracking refuses symlink ancestry"):
            self.items(self.modules[0], [plan(writePaths=["src/app.py", "alias"], artifactRoots=["alias"])])

    def test_accepted_plans_are_not_preflighted(self) -> None:
        fill(self.root / "tools", 600)
        items = self.items(self.modules[0], [
            plan("done", writePaths=["tools"]),
            plan("next", writePaths=["src/app.py"], dependsOn=["done"]),
        ], accepted=["done"])
        self.assertEqual(sorted(items), ["done", "next"])


class ValidateManifestCliTests(ArtifactRootsTestCase):
    def run_cli(self, plans: list[dict]) -> tuple[int, dict]:
        path = self.root / "impl-plans/active/dispatch.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest(plans)))
        result = subprocess.run(
            [sys.executable, str(DISPATCH_SCRIPTS[0]), "--validate-manifest", "impl-plans/active/dispatch.json"],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def test_report_lists_roots_counts_and_limits(self) -> None:
        fill(self.root / "tools/cache", 600)
        (self.root / "tools/toolchain.json").write_text("{}")
        code, report = self.run_cli([plan(writePaths=["tools", "tools/toolchain.json", "src/app.py"], artifactRoots=["tools"])])
        self.assertEqual(code, 0)
        self.assertTrue(report["valid"])
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["limits"], {
            "sourcePaths": 512, "sourceEntries": 512, "sourceFileBytes": 8_000_000,
            "sourceTotalBytes": 64_000_000, "artifactRoots": 64,
        })
        entry = report["plans"][0]
        self.assertEqual(entry["planId"], "tools")
        self.assertEqual(entry["trackedPaths"], ["tools/toolchain.json", "src/app.py"])
        self.assertEqual(entry["artifactRoots"], ["tools"])
        roots = {root["path"]: root for root in entry["roots"]}
        self.assertEqual(roots["tools"]["selection"], "artifact")
        self.assertTrue(roots["tools"]["expectedToGrow"])
        self.assertEqual(roots["tools"]["entries"], 603)
        self.assertEqual(roots["src/app.py"], {**roots["src/app.py"], "exists": False, "kind": "missing", "entries": 1})
        self.assertFalse(roots["tools/toolchain.json"]["expectedToGrow"])

    def test_invalid_manifest_exits_nonzero_with_errors(self) -> None:
        fill(self.root / "tools", 600)
        code, report = self.run_cli([
            plan("grows", writePaths=["tools"]),
            plan("ok", writePaths=["src/app.py"]),
            plan("unowned", writePaths=["src/app.py"], artifactRoots=["tools"]),
        ])
        self.assertEqual(code, 1)
        self.assertFalse(report["valid"])
        by_plan = {entry["planId"]: entry for entry in report["plans"]}
        self.assertRegex(by_plan["grows"]["errors"][0], "currently has 601 entries")
        self.assertEqual(by_plan["grows"]["roots"][0]["entries"], 601)
        self.assertEqual(by_plan["ok"]["errors"], [])
        self.assertRegex(by_plan["unowned"]["errors"][0], "must exactly equal one of the plan's writePaths")
        self.assertEqual(len(report["errors"]), 2)


class CheckpointGateTests(ArtifactRootsTestCase):
    def run_gate(self, plans: list[dict], checkpoint: dict | None = None) -> dict:
        manifest_path = "impl-plans/active/dispatch.json"
        path = self.root / manifest_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest(plans)))
        payload = checkpoint if checkpoint is not None else {
            "checkpoint_blocked": False,
            "status": "ready",
            "commitMessage": "docs: checkpoint plans",
            "committedFiles": [manifest_path, "impl-plans/active/tools.md"],
            "manifestPath": manifest_path,
            "evidenceRoot": "tmp/artifact-roots",
            "blockers": [],
        }
        envelope = {"input": {"_rielaInput": {"messages": [
            {"fromStepId": "plan-checkpoint", "createdOrder": 1, "payload": payload},
        ]}}}
        result = subprocess.run(
            [sys.executable, str(GATE_SCRIPT)], cwd=self.root, input=json.dumps(envelope) + "\n",
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_valid_contract_passes_commit_request_through(self) -> None:
        fill(self.root / "tools/cache", 600)
        (self.root / "tools/toolchain.json").write_text("{}")
        output = self.run_gate([plan(writePaths=["tools", "tools/toolchain.json"], artifactRoots=["tools"])])
        self.assertEqual(output["when"], {"contract_valid": True})
        payload = output["payload"]
        self.assertTrue(payload["contract_valid"])
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["commitMessage"], "docs: checkpoint plans")
        self.assertEqual(payload["committedFiles"], ["impl-plans/active/dispatch.json", "impl-plans/active/tools.md"])
        self.assertEqual(payload["manifestPath"], "impl-plans/active/dispatch.json")
        self.assertTrue(payload["report"]["valid"])

    def test_invalid_contract_routes_back_to_plan_author_without_commit_request(self) -> None:
        fill(self.root / "tools", 600)
        output = self.run_gate([plan(writePaths=["tools"])])
        self.assertEqual(output["when"], {"contract_valid": False})
        payload = output["payload"]
        self.assertFalse(payload["contract_valid"])
        self.assertNotIn("commitMessage", payload)
        self.assertNotIn("committedFiles", payload)
        self.assertEqual(len(payload["findings"]), 1)
        finding = payload["findings"][0]
        self.assertEqual(finding["severity"], "high")
        self.assertEqual(finding["targetStep"], "step4-impl-plan-create")
        self.assertEqual(finding["file"], "impl-plans/active/dispatch.json")
        self.assertRegex(finding["message"], "currently has 601 entries.*limit 512")
        self.assertTrue(payload["resumeCriteria"])

    def test_manifest_is_derived_from_committed_files_when_path_is_omitted(self) -> None:
        output = self.run_gate([plan()], {
            "checkpoint_blocked": False, "status": "ready", "commitMessage": "docs: checkpoint",
            "committedFiles": ["impl-plans/active/dispatch.json"], "blockers": [],
        })
        self.assertTrue(output["when"]["contract_valid"])
        self.assertEqual(output["payload"]["manifestPath"], "impl-plans/active/dispatch.json")

    def test_unreadable_manifest_is_a_finding_not_acceptance(self) -> None:
        output = self.run_gate([plan()], {
            "checkpoint_blocked": False, "status": "ready", "commitMessage": "docs: checkpoint",
            "committedFiles": [], "manifestPath": "impl-plans/active/absent.json", "blockers": [],
        })
        self.assertFalse(output["when"]["contract_valid"])
        self.assertRegex(output["payload"]["findings"][0]["message"], "regular non-symlink file")


if __name__ == "__main__":
    unittest.main()
