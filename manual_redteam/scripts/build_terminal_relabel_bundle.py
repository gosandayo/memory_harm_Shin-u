#!/usr/bin/env python3
"""Build a condition-masked bundle for terminal verdict relabeling.

This script implements the `build_masked_bundle` step registered in
2026-05-19_cold_terminal_factor_panel_gpt4omini/manifest.yaml. It does not call
any model. It emits:
  - relabel/masked_bundle.jsonl: endpoint + locked target proposition + reply
  - relabel/SEALED_mapping.json: id -> unmasked provenance
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def resolve(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else REPO_ROOT / p


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=None)
    return p.parse_args()


def endpoint_for_cell(cell_name: str) -> str:
    if cell_name.startswith("S13_"):
        return "S13_PERSONAL_VERDICT"
    if cell_name.startswith("S14_"):
        return "S14_ACTION_VERDICT"
    raise ValueError(f"cannot infer endpoint for cell {cell_name!r}")


def run_idx_for_branch(branch_name: str) -> int:
    if "_run" not in branch_name:
        raise ValueError(f"branch name does not contain _runNN: {branch_name}")
    return int(branch_name.rsplit("_run", 1)[1])


def read_terminal_reply(path: Path) -> tuple[str, str, str]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assistants = [r for r in rows if r.get("role") == "assistant"]
    users = [r for r in rows if r.get("role") == "user"]
    if len(assistants) != 1 or len(users) != 1:
        raise ValueError(f"expected one user and one assistant in {path}")
    reply = assistants[-1]["content"]
    rung = assistants[-1].get("rung") or users[-1].get("rung")
    src_sha1 = hashlib.sha1(path.read_bytes()).hexdigest()
    return reply, str(rung), src_sha1


def main() -> int:
    args = parse_args()
    manifest_path = resolve(args.manifest)
    run_root = manifest_path.parent
    output_dir = resolve(args.output_dir) if args.output_dir else run_root / "relabel"
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    target_props = manifest["labeling"]["target_propositions"]
    cells = [c["name"] for c in manifest["cells"] if not c.get("pending_signoff")]

    masked_path = output_dir / "masked_bundle.jsonl"
    mapping_path = output_dir / "SEALED_mapping.json"
    mapping: dict[str, dict] = {}

    with masked_path.open("w", encoding="utf-8") as masked:
        for cell in sorted(cells):
            endpoint = endpoint_for_cell(cell)
            proposition = target_props[endpoint]
            for msg_path in sorted((run_root / "branches").glob(f"{cell}_run*/messages.jsonl")):
                branch = msg_path.parent.name
                run_idx = run_idx_for_branch(branch)
                reply, rung, src_sha1 = read_terminal_reply(msg_path)
                item_id = hashlib.sha1(f"{cell}:{run_idx}:{src_sha1}".encode("utf-8")).hexdigest()
                masked.write(
                    json.dumps(
                        {
                            "id": item_id,
                            "endpoint": endpoint,
                            "target_proposition": " ".join(str(proposition).split()),
                            "assistant_reply": reply,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                mapping[item_id] = {
                    "cell": cell,
                    "run_idx": run_idx,
                    "messages_path": str(msg_path.relative_to(REPO_ROOT)),
                    "rung_token": rung,
                    "source_sha1": src_sha1,
                }

    mapping_path.write_text(json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {masked_path.relative_to(REPO_ROOT)} ({len(mapping)} items)")
    print(f"wrote {mapping_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
