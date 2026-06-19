"""Plot Pareto benchmark projections and hypervolume bars."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--case")
    return parser


def main(argv=None) -> None:
    import matplotlib.pyplot as plt

    args = build_parser().parse_args(argv)
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = data["cases"]
    selected_cases = [args.case] if args.case else list(cases)

    for case in selected_cases:
        payload = cases[case]
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        projections = [((0, 1), "MSR", "CGCC"), ((0, 2), "MSR", "ETR"), ((1, 2), "CGCC", "ETR")]
        greedy = payload.get("greedy_point", {}).get("objectives")
        for algorithm, algo_payload in payload["algorithms"].items():
            first = algo_payload["raw"][0] if algo_payload["raw"] else {"front": []}
            points = first["front"]
            for ax, ((x_idx, y_idx), x_label, y_label) in zip(axes, projections):
                if points:
                    ax.scatter([p[x_idx] for p in points], [p[y_idx] for p in points], label=algorithm, s=20)
                if greedy:
                    ax.scatter(
                        [greedy[x_idx]],
                        [greedy[y_idx]],
                        marker="*",
                        s=120,
                        c="black",
                        label="greedy" if algorithm == next(iter(payload["algorithms"])) else None,
                    )
                ax.set_xlabel(x_label)
                ax.set_ylabel(y_label)
                ax.set_xlim(0, 1.02)
                ax.set_ylim(0, 1.02)
        axes[0].legend(fontsize=8)
        fig.suptitle(f"Pareto projections: {case}")
        fig.tight_layout()
        fig.savefig(out_dir / f"{case.replace('/', '_')}_projections.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        algs = list(payload["algorithms"])
        means = [payload["algorithms"][alg]["hv"]["mean"] for alg in algs]
        stds = [payload["algorithms"][alg]["hv"]["std"] for alg in algs]
        ax.bar(algs, means, yerr=stds, capsize=3)
        ax.set_ylabel("Hypervolume")
        ax.set_ylim(0, max(1.0, max(means, default=0.0) * 1.15))
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()
        fig.savefig(out_dir / f"{case.replace('/', '_')}_hv.png", dpi=160)
        plt.close(fig)


if __name__ == "__main__":
    main()
